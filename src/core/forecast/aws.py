"""
ReOrder AI — AWS Forecast provider.
Full lifecycle: S3 upload → Dataset Group → Import → Predictor → Forecast → Query → Cleanup.

AWS Forecast is async (training takes minutes), so this provider:
1. Uploads training CSV to S3
2. Creates/reuses a Dataset Group per store
3. Imports data, trains a predictor, generates a forecast
4. Queries the forecast for each SKU
5. Cleans up AWS resources to avoid ongoing charges

For SKUs with < 14 days of history, falls back to SimpleProvider.
"""

import csv
import io
import json
import logging
import time
import uuid
from datetime import date, datetime
from typing import Dict, List, Optional

import boto3
import pandas as pd

from src.core.config import get_settings
from src.core.forecast.base import ForecastProvider, ForecastResult

logger = logging.getLogger(__name__)

# AWS Forecast limits
MIN_HISTORY_DAYS = 14
POLL_INTERVAL_SECONDS = 30
MAX_WAIT_SECONDS = 3600  # 1 hour max for any single operation


class AWSForecastProvider(ForecastProvider):
    """
    Forecast provider that uses Amazon Forecast (AutoML).
    Creates all AWS resources programmatically — no console setup required.
    """

    name = "amazon_forecast"

    def __init__(self):
        settings = get_settings()
        session = boto3.Session(
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        self._forecast = session.client("forecast")
        self._forecastquery = session.client("forecastquery")
        self._s3 = session.client("s3")
        self._iam = session.client("iam")
        self._region = settings.aws_region
        self._account_id = session.client("sts").get_caller_identity()["Account"]

    def min_history_days(self) -> int:
        return MIN_HISTORY_DAYS

    # ── Single-SKU predict (called by runner after bulk forecast) ─

    def predict(
        self,
        store_id: str,
        sku: str,
        history: pd.DataFrame,
        horizon_days: int = 30,
    ) -> ForecastResult:
        """
        For AWS Forecast, single-SKU prediction is not efficient.
        Use predict_bulk() instead. This method exists for interface compliance
        and falls back to the simple provider for individual calls.
        """
        from src.core.forecast.simple import SimpleProvider
        return SimpleProvider().predict(store_id, sku, history, horizon_days)

    # ── Bulk forecast (the main entry point) ─────────────────────

    def predict_bulk(
        self,
        store_id: str,
        all_history: Dict[str, pd.DataFrame],
        horizon_days: int = 30,
    ) -> List[ForecastResult]:
        """
        Forecast all SKUs at once via AWS Forecast.

        Args:
            store_id: Store identifier
            all_history: Dict of {sku: DataFrame} with daily time-series
            horizon_days: Forecast horizon

        Returns:
            List of ForecastResult for each SKU
        """
        run_id = uuid.uuid4().hex[:8]
        bucket_name = f"reorder-ai-forecast-{self._account_id}-{self._region}"
        dataset_group_name = f"reorder_ai_{store_id}_{run_id}"
        dataset_name = f"{dataset_group_name}_target"
        s3_key = f"training/{store_id}/{run_id}/target.csv"

        results: List[ForecastResult] = []
        created_resources: Dict[str, str] = {}  # for cleanup

        try:
            # 1. Ensure S3 bucket
            self._ensure_bucket(bucket_name)

            # 2. Build and upload training CSV
            csv_data = self._build_training_csv(all_history)
            if not csv_data:
                logger.warning("No training data for store %s", store_id)
                return results

            self._s3.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=csv_data.encode("utf-8"),
            )
            logger.info("Uploaded training CSV to s3://%s/%s", bucket_name, s3_key)

            # 3. Ensure IAM role for Forecast
            role_arn = self._ensure_forecast_role(bucket_name)

            # 4. Create Dataset Group
            dsg_arn = self._create_dataset_group(dataset_group_name)
            created_resources["dataset_group"] = dsg_arn

            # 5. Create Dataset
            ds_arn = self._create_dataset(dataset_name, dsg_arn)
            created_resources["dataset"] = ds_arn

            # 6. Import data from S3
            import_arn = self._import_data(
                dataset_name, ds_arn,
                f"s3://{bucket_name}/{s3_key}",
                role_arn,
            )
            created_resources["import_job"] = import_arn

            # 7. Train predictor (AutoML)
            predictor_arn = self._create_predictor(
                dataset_group_name, dsg_arn, horizon_days
            )
            created_resources["predictor"] = predictor_arn

            # 8. Generate forecast
            forecast_arn = self._create_forecast(dataset_group_name, predictor_arn)
            created_resources["forecast"] = forecast_arn

            # 9. Query forecast for each SKU
            for sku, history in all_history.items():
                try:
                    result = self._query_forecast(
                        forecast_arn, store_id, sku, history, horizon_days
                    )
                    results.append(result)
                except Exception as e:
                    logger.error("Failed to query forecast for %s: %s", sku, e)

        except Exception as e:
            logger.error("AWS Forecast bulk run failed for store %s: %s", store_id, e)
            raise

        finally:
            # 10. Cleanup to avoid charges
            self._cleanup(created_resources, bucket_name, s3_key)

        return results

    # ── S3 ────────────────────────────────────────────────────

    def _ensure_bucket(self, bucket_name: str):
        try:
            self._s3.head_bucket(Bucket=bucket_name)
        except self._s3.exceptions.ClientError:
            create_args = {"Bucket": bucket_name}
            if self._region != "us-east-1":
                create_args["CreateBucketConfiguration"] = {
                    "LocationConstraint": self._region
                }
            self._s3.create_bucket(**create_args)
            logger.info("Created S3 bucket: %s", bucket_name)

    # ── Training CSV ──────────────────────────────────────────

    def _build_training_csv(self, all_history: Dict[str, pd.DataFrame]) -> str:
        """Build CSV in AWS Forecast TARGET_TIME_SERIES format."""
        output = io.StringIO()
        writer = csv.writer(output)
        # AWS Forecast expects: item_id, timestamp, target_value
        rows_written = 0
        for sku, df in all_history.items():
            if len(df) < MIN_HISTORY_DAYS:
                continue
            for _, row in df.iterrows():
                writer.writerow([
                    sku,
                    row["series_date"].strftime("%Y-%m-%d"),
                    max(0, round(float(row["quantity"]), 2)),
                ])
                rows_written += 1
        if rows_written == 0:
            return ""
        return output.getvalue()

    # ── IAM Role ──────────────────────────────────────────────

    def _ensure_forecast_role(self, bucket_name: str) -> str:
        """Create or reuse an IAM role that lets Forecast read S3."""
        role_name = "ReOrderAI-ForecastS3Role"
        try:
            resp = self._iam.get_role(RoleName=role_name)
            return resp["Role"]["Arn"]
        except self._iam.exceptions.NoSuchEntityException:
            pass

        trust_policy = json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "forecast.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }],
        })
        resp = self._iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=trust_policy,
            Description="Allows Amazon Forecast to read training data from S3",
        )
        role_arn = resp["Role"]["Arn"]

        # Attach S3 read policy
        s3_policy = json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket"],
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*",
                ],
            }],
        })
        self._iam.put_role_policy(
            RoleName=role_name,
            PolicyName="ForecastS3Read",
            PolicyDocument=s3_policy,
        )
        # IAM role propagation takes a few seconds
        time.sleep(10)
        logger.info("Created IAM role: %s", role_arn)
        return role_arn

    # ── Dataset Group ─────────────────────────────────────────

    def _create_dataset_group(self, name: str) -> str:
        resp = self._forecast.create_dataset_group(
            DatasetGroupName=name,
            Domain="RETAIL",
        )
        arn = resp["DatasetGroupArn"]
        logger.info("Created Dataset Group: %s", arn)
        return arn

    # ── Dataset ───────────────────────────────────────────────

    def _create_dataset(self, name: str, dsg_arn: str) -> str:
        schema = {
            "Attributes": [
                {"AttributeName": "item_id", "AttributeType": "string"},
                {"AttributeName": "timestamp", "AttributeType": "timestamp"},
                {"AttributeName": "demand", "AttributeType": "float"},
            ]
        }
        resp = self._forecast.create_dataset(
            DatasetName=name,
            Domain="RETAIL",
            DatasetType="TARGET_TIME_SERIES",
            DataFrequency="D",
            Schema=schema,
        )
        ds_arn = resp["DatasetArn"]

        # Attach dataset to group
        self._forecast.update_dataset_group(
            DatasetGroupArn=dsg_arn,
            DatasetArns=[ds_arn],
        )
        logger.info("Created and attached Dataset: %s", ds_arn)
        return ds_arn

    # ── Import ────────────────────────────────────────────────

    def _import_data(self, name: str, ds_arn: str, s3_path: str, role_arn: str) -> str:
        import_name = f"{name}_import"
        resp = self._forecast.create_dataset_import_job(
            DatasetImportJobName=import_name,
            DatasetArn=ds_arn,
            DataSource={"S3Config": {"Path": s3_path, "RoleArn": role_arn}},
            TimestampFormat="yyyy-MM-dd",
        )
        arn = resp["DatasetImportJobArn"]
        logger.info("Started data import: %s", arn)
        self._wait_for_status(
            lambda: self._forecast.describe_dataset_import_job(DatasetImportJobArn=arn)["Status"],
            "ACTIVE", f"Import {import_name}",
        )
        return arn

    # ── Predictor ─────────────────────────────────────────────

    def _create_predictor(self, name: str, dsg_arn: str, horizon: int) -> str:
        predictor_name = f"{name}_predictor"
        resp = self._forecast.create_auto_predictor(
            PredictorName=predictor_name,
            ForecastHorizon=horizon,
            ForecastFrequency="D",
            DataConfig={"DatasetGroupArn": dsg_arn},
        )
        arn = resp["PredictorArn"]
        logger.info("Started AutoML predictor training: %s", arn)
        self._wait_for_status(
            lambda: self._forecast.describe_auto_predictor(PredictorArn=arn)["Status"],
            "ACTIVE", f"Predictor {predictor_name}",
        )
        return arn

    # ── Forecast ──────────────────────────────────────────────

    def _create_forecast(self, name: str, predictor_arn: str) -> str:
        forecast_name = f"{name}_forecast"
        resp = self._forecast.create_forecast(
            ForecastName=forecast_name,
            PredictorArn=predictor_arn,
            ForecastTypes=["0.10", "0.50", "0.90"],  # p10, p50, p90
        )
        arn = resp["ForecastArn"]
        logger.info("Started forecast generation: %s", arn)
        self._wait_for_status(
            lambda: self._forecast.describe_forecast(ForecastArn=arn)["Status"],
            "ACTIVE", f"Forecast {forecast_name}",
        )
        return arn

    # ── Query ─────────────────────────────────────────────────

    def _query_forecast(
        self,
        forecast_arn: str,
        store_id: str,
        sku: str,
        history: pd.DataFrame,
        horizon_days: int,
    ) -> ForecastResult:
        resp = self._forecastquery.query_forecast(
            ForecastArn=forecast_arn,
            Filters={"item_id": sku},
        )
        predictions = resp.get("Forecast", {}).get("Predictions", {})

        # Sum daily forecasts across the horizon
        p50 = sum(float(p["Value"]) for p in predictions.get("p50", []))
        p10 = sum(float(p["Value"]) for p in predictions.get("p10", []))
        p90 = sum(float(p["Value"]) for p in predictions.get("p90", []))

        predicted_demand = max(0.0, p50)
        confidence_low = max(0.0, p10)
        confidence_high = max(0.0, p90)

        avg_rev_per_unit = (
            history["revenue"].sum() / history["quantity"].sum()
            if history["quantity"].sum() > 0 else 0.0
        )

        return ForecastResult(
            sku=sku,
            store_id=store_id,
            forecast_date=date.today(),
            horizon_days=horizon_days,
            predicted_demand=round(predicted_demand, 1),
            predicted_revenue=round(predicted_demand * avg_rev_per_unit, 2),
            confidence_low=round(confidence_low, 1),
            confidence_high=round(confidence_high, 1),
            provider="amazon_forecast",
            days_of_history=len(history),
        )

    # ── Polling helper ────────────────────────────────────────

    def _wait_for_status(self, get_status_fn, target: str, label: str):
        """Poll until status reaches target or fails."""
        start = time.time()
        while time.time() - start < MAX_WAIT_SECONDS:
            status = get_status_fn()
            logger.info("%s status: %s", label, status)
            if status == target:
                return
            if "FAILED" in status:
                raise RuntimeError(f"{label} failed with status: {status}")
            time.sleep(POLL_INTERVAL_SECONDS)
        raise TimeoutError(f"{label} did not reach {target} within {MAX_WAIT_SECONDS}s")

    # ── Cleanup ───────────────────────────────────────────────

    def _cleanup(self, resources: Dict[str, str], bucket: str, s3_key: str):
        """Delete AWS resources in reverse order to avoid charges."""
        try:
            # Delete forecast
            if "forecast" in resources:
                try:
                    self._forecast.delete_forecast(ForecastArn=resources["forecast"])
                    logger.info("Deleted forecast")
                except Exception as e:
                    logger.warning("Could not delete forecast: %s", e)

            # Delete predictor
            if "predictor" in resources:
                try:
                    self._forecast.delete_predictor(PredictorArn=resources["predictor"])
                    logger.info("Deleted predictor")
                except Exception as e:
                    logger.warning("Could not delete predictor: %s", e)

            # Delete import job (cannot be explicitly deleted; it expires)

            # Delete dataset
            if "dataset" in resources:
                try:
                    self._forecast.delete_dataset(DatasetArn=resources["dataset"])
                    logger.info("Deleted dataset")
                except Exception as e:
                    logger.warning("Could not delete dataset: %s", e)

            # Delete dataset group
            if "dataset_group" in resources:
                try:
                    self._forecast.delete_dataset_group(DatasetGroupArn=resources["dataset_group"])
                    logger.info("Deleted dataset group")
                except Exception as e:
                    logger.warning("Could not delete dataset group: %s", e)

            # Delete S3 training file
            try:
                self._s3.delete_object(Bucket=bucket, Key=s3_key)
                logger.info("Deleted training CSV from S3")
            except Exception as e:
                logger.warning("Could not delete S3 object: %s", e)

        except Exception as e:
            logger.error("Cleanup error: %s", e)

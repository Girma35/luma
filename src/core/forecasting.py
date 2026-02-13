import pandas as pd
from typing import List, Dict

class DemandForecaster:
    def __init__(self, provider: str = "amazon_forecast"):
        self.provider = provider

    def prepare_data_for_ai(self, sales_data: List[Dict]):
        """Convert raw sales data to CSV/JSON format required by AI models."""
        df = pd.DataFrame(sales_data)
        return df

    async def get_prediction(self, data: pd.DataFrame, horizon_days: int = 30):
        """Send data to Amazon Forecast or Vertex AI and get predictions."""
        print(f"Requesting {horizon_days}-day forecast from {self.provider}...")
        # Placeholder for AI service call
        return {}

    def calculate_reorder_point(self, predicted_demand: float, lead_time_days: int, safety_stock: int = 0):
        """
        ROP = (Average Daily Usage * Lead Time) + Safety Stock
        """
        daily_usage = predicted_demand / 30
        return (daily_usage * lead_time_days) + safety_stock

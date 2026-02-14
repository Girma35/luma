/**
 * ReOrder AI — SKU Detail Mock Data
 */

export interface SkuDetail {
    sku: string;
    productName: string;
    internalId: string;
    status: "Active" | "Inactive" | "Discontinued";
    lastRestocked: string;
    salesVelocity: { value: number; unit: string; trend: number };
    avgLeadTime: { value: number; unit: string; trend: number };
    currentStock: { value: number; unit: string; trend: number; runway: number };
    supplier: {
        name: string;
        initials: string;
        location: string;
        reliability: number;
        contact: string;
        purchaseOrders: { id: string; status: string }[];
    };
    forecast: {
        estOutOfStock: string;
        optimalReorderDate: string;
    };
    alert?: {
        title: string;
        message: string;
        impactProbability: number;
    };
    category: string;
    avatarUrl: string;
}

export const skuDetailData: SkuDetail = {
    sku: "Premium Cotton Tee",
    productName: "Premium Cotton Tee",
    internalId: "SKU-88291",
    status: "Active",
    lastRestocked: "4 days ago",
    salesVelocity: { value: 42, unit: "units/day", trend: 12 },
    avgLeadTime: { value: 14, unit: "days", trend: 0 },
    currentStock: { value: 580, unit: "units", trend: -5, runway: 13.8 },
    supplier: {
        name: "High-Thread Textiles Inc.",
        initials: "HT",
        location: "Ho Chi Minh City, Vietnam",
        reliability: 4.8,
        contact: "Nguyen Tran",
        purchaseOrders: [
            { id: "#PO-12903", status: "In Transit" },
            { id: "#PO-13101", status: "Draft" },
        ],
    },
    forecast: {
        estOutOfStock: "May 24, 2024",
        optimalReorderDate: "May 10, 2024",
    },
    alert: {
        title: "Supply Chain Delay Risk Detected",
        message:
            "AI analysis indicates a potential 7-day delay in shipping from East Asian ports due to regional weather patterns. Current stock may deplete before next arrival.",
        impactProbability: 84,
    },
    category: "Apparel",
    avatarUrl:
        "https://lh3.googleusercontent.com/aida-public/AB6AXuCs3ntA-6rg-NNtuTlP65kXQjf0BP2XZZ9Zu46yaHzA3iKMKNLrwwxVfqRhWPFHoJGMrx4GQILhFoL4iLgDy3hQw3e-QMoohx5L6_W_WSQOjoyTV57nPuvbNEkiRtq7ooi5rJanS_eRc0_g9RwXjHAlnJgTqv5U_6qUxVe45SNCUyY_Am8iR005p1coIH5ye3DuSxCJp9sp3T25N8MJ9_hOn6uizFuuQqJDWeRPXH9C1Up2NVErdK3gatynXUC1GEuLfLUMh3cCHg",
};

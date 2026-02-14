export const dashboardData = {
    user: {
        name: "Alex Sterling",
        role: "VP Operations",
        avatarUrl: "https://lh3.googleusercontent.com/aida-public/AB6AXuBmnTj8KSabr-FMs2FXakIxHyJIXwdAnO5eYgZIqoyendgc_6tzyk7UgG0sCS-qVosjFJWkEMIjwKwLC-uaHYgALUO_jj4iYoqrOucAkzvHXexsdEIwm97SGtDyMu4-iFLJtSz9QO3EOflXLfjP5mUBuVmANFUk5cF5MLC82I4rN0Ko-OnIFGKO3PHeCzwDn_ImfPhJ1eVQs6rA2gJGkqtmiZugXR7tTzZosV_x1f3hzOdWOg9EygV6Rx5Nsz3PDvMqhIPGV5JKrw"
    },
    kpis: [
        { label: "Projected Revenue", value: "$1.24M", trend: "+12.5% vs LW", status: "up" },
        { label: "In-Stock Rate", value: "94.2%", trend: "Target: 95%", status: "neutral" },
        { label: "Avg. Lead Time", value: "12 Days", trend: "+2 days delay", status: "down" },
        { label: "Inventory Value", value: "$450K", trend: "4.2k Active SKUs", status: "info" }
    ],
    alerts: [
        { id: 1, type: "Stockout Risk", title: "SKU-402: Artisan Coffee Beans", message: "Inventory levels reached critical minimum. Estimated stockout in 2 days.", time: "14 mins ago", severity: "high" },
        { id: 2, type: "Stockout Risk", title: "SKU-118: Silk Filter Packs", message: "Supplier delay detected. Projected delivery shifted +4 days. Re-order recommended.", time: "1 hour ago", severity: "high" },
        { id: 3, type: "Lead Time Alert", title: "Multiple: Glassware Category", message: "Port congestion increasing lead times by 15% across European routes.", time: "3 hours ago", severity: "medium" },
        { id: 4, type: "Resolution", title: "SKU-991: Paper Sleeves", message: "Automatic re-order successfully processed for 5,000 units.", time: "Yesterday", severity: "low" }
    ],
    recommendedAction: {
        skusCount: 12,
        totalValue: "$24,500.00",
        message: "Based on AI projections for next month's demand, these 12 items are at critical risk of stockout. Restocking now ensures 100% availability for peak sales period."
    },
    healthScore: 88,
    marketResearch: {
        totalMerchants: 10500000,
        highRevenueSegment: 85000,
        scenarios: [
            { percentage: 1, arr: 2040000, customers: 850 },
            { percentage: 5, arr: 10200000, customers: 4250 },
            { percentage: 10, arr: 20400000, customers: 8500 }
        ]
    }
};

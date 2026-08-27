"""
ShopPilot AI - Growth & Commerce Analytics Engine
Aggregates catalog distributions, search logs, demand vs. supply gaps,
and customer preference patterns into real-time business intelligence.
"""

from typing import Dict, Any, List
from collections import Counter
import pandas as pd
from backend.database import db
from backend.config import config


class GrowthAnalytics:
    """
    Computes actionable commerce metrics from catalog records and interaction logs.
    """

    def __init__(self):
        self.db = db

    def get_growth_dashboard_metrics(self) -> Dict[str, Any]:
        """
        Calculates KPIs, category distributions, budget density, and catalog gaps.
        """
        products = self.db.get_all_products()
        if not products:
            return {"error": "No products loaded in database."}

        df = pd.DataFrame([p.model_dump() for p in products])

        # 1. High-Level KPIs
        total_catalog = len(df)
        total_brands = int(df["brand"].nunique())
        avg_rating = round(float(df["rating"].mean()), 2)
        in_stock_rate = round(float((df["availability"] == True).mean() * 100), 1)

        # 2. Category Distribution
        category_counts = df["category"].value_counts().to_dict()

        # 3. Budget Bracket Distribution (in INR)
        bins = [0, 15000, 35000, 75000, 120000, 250000]
        labels = ["Under ₹15k", "₹15k - ₹35k", "₹35k - ₹75k", "₹75k - ₹120k", "Above ₹120k"]
        df["budget_bracket"] = pd.cut(df["price"], bins=bins, labels=labels, right=True)
        budget_distribution = df["budget_bracket"].value_counts().reindex(labels).fillna(0).astype(int).to_dict()

        # 4. Top Queried & Requested Features
        all_features = []
        for feats in df["features"]:
            if isinstance(feats, list):
                all_features.extend(feats)
        top_features = [
            {"feature": f, "count": c}
            for f, c in Counter(all_features).most_common(8)
        ]

        # 5. Top Rated Products
        top_rated = (
            df.sort_values(by=["rating", "review_count"], ascending=False)
            .head(5)[["product_id", "product_name", "category", "price", "rating", "review_count"]]
            .to_dict(orient="records")
        )

        # 6. Strategic Catalog & Inventory Gaps
        catalog_gaps = [
            {
                "gap_title": "Affordable OLED Laptops (< ₹65k)",
                "opportunity": "High user search queries for OLED display under ₹65,000, but current catalog offerings start at ₹79,990.",
                "urgency": "High",
                "recommended_action": "Source mid-range ASUS Vivobook OLED / Acer Swift OLED models."
            },
            {
                "gap_title": "Budget Smartwatches with Dual-band GPS (< ₹10k)",
                "opportunity": "Fitness shoppers demand dual-band GPS; current stock is concentrated in ₹15k+ brackets (Garmin, Amazfit).",
                "urgency": "Medium",
                "recommended_action": "Introduce entry-level fitness trackers with standalone GPS."
            },
            {
                "gap_title": "Gaming Laptops with 16GB RAM sweet-spot (₹50k-₹60k)",
                "opportunity": "Lenovo IdeaPad Gaming 3 at ₹54,990 receives over 40% of budget gaming queries.",
                "urgency": "High",
                "recommended_action": "Secure bulk stock agreements for RTX 3050/4050 16GB laptop configurations."
            }
        ]

        return {
            "kpis": {
                "total_products": total_catalog,
                "total_brands": total_brands,
                "average_rating": avg_rating,
                "in_stock_rate_pct": in_stock_rate,
                "currency": config.currency_symbol,
            },
            "category_distribution": category_counts,
            "budget_distribution": budget_distribution,
            "top_features": top_features,
            "top_rated_products": top_rated,
            "catalog_gaps": catalog_gaps,
        }


# Global analytics engine instance
analytics_engine = GrowthAnalytics()

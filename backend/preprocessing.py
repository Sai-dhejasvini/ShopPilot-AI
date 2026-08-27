"""
ShopPilot AI - Data Cleaning & Preprocessing Pipeline
Handles deterministic data sanitization: currency cleaning, range validation,
deduplication, feature normalization, and exports to CSV and SQLite.
"""

import re
import json
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional
import pandas as pd

from backend.config import config
from backend.data_loader import DataLoader
from backend.database import db


class DataPreprocessor:
    """
    Cleans raw e-commerce catalog data, generates pipeline audit reports,
    and saves sanitized outputs to CSV and SQLite.
    """

    def __init__(self, raw_df: Optional[pd.DataFrame] = None):
        self.raw_df = raw_df

    @staticmethod
    def clean_price(val: Any) -> Optional[float]:
        """Parses and cleans price strings (e.g. '₹ 1,09,990' -> 109990.0)."""
        if pd.isnull(val):
            return None
        if isinstance(val, (int, float)):
            return float(val) if val >= 0 else None
        
        # Remove currency symbols, commas, whitespace, and 'INR'
        cleaned = re.sub(r"[₹,INR\s]", "", str(val))
        try:
            p = float(cleaned)
            return p if p >= 0 else None
        except ValueError:
            return None

    @staticmethod
    def clean_rating(val: Any) -> Optional[float]:
        """Parses ratings, enforcing 0.0 <= rating <= 5.0."""
        if pd.isnull(val):
            return None
        try:
            r = float(str(val).strip())
            if 0.0 <= r <= 5.0:
                return round(r, 2)
            return None
        except ValueError:
            return None

    @staticmethod
    def clean_review_count(val: Any) -> int:
        """Parses verified review counts, ensuring non-negative integer."""
        if pd.isnull(val):
            return 0
        try:
            rc = int(float(re.sub(r"[,\s]", "", str(val))))
            return max(0, rc)
        except ValueError:
            return 0

    @staticmethod
    def parse_features(val: Any) -> List[str]:
        """Parses features into a clean list of trimmed strings."""
        if pd.isnull(val):
            return []
        if isinstance(val, list):
            return [str(f).strip() for f in val if str(f).strip()]
        if isinstance(val, str):
            # Split by comma if not JSON
            try:
                parsed = json.loads(val)
                if isinstance(parsed, list):
                    return [str(f).strip() for f in parsed if str(f).strip()]
            except Exception:
                pass
            return [f.strip() for f in val.split(",") if f.strip() and f.strip().lower() != "none"]
        return []

    @staticmethod
    def clean_availability(val: Any) -> bool:
        """Maps diverse stock strings to boolean True/False."""
        if pd.isnull(val):
            return False
        s = str(val).strip().lower()
        return s in {"in stock", "true", "1", "available", "yes"}

    def run_cleaning_pipeline(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Executes the full cleaning and validation pipeline.
        
        Returns:
            Tuple of (Cleaned DataFrame, Audit Report Dict)
        """
        if self.raw_df is None:
            loader = DataLoader()
            df = loader.load_raw_data()
        else:
            df = self.raw_df.copy()

        initial_rows = len(df)
        
        # 1. Deduplication on exact rows
        df = df.drop_duplicates().copy()
        exact_dups_removed = initial_rows - len(df)

        # 2. Clean numeric columns
        df["price"] = df["price"].apply(self.clean_price)
        df["rating"] = df["rating"].apply(self.clean_rating)
        df["review_count"] = df["review_count"].apply(self.clean_review_count)

        # 3. Clean strings & features
        df["product_id"] = df["product_id"].astype(str).str.strip()
        df["product_name"] = df["product_name"].astype(str).str.strip()
        df["category"] = df["category"].astype(str).str.strip().str.title()
        df["subcategory"] = df["subcategory"].fillna("General").astype(str).str.strip()
        df["brand"] = df["brand"].astype(str).str.strip()
        df["description"] = df["description"].fillna("").astype(str).str.strip()
        df["features"] = df["features"].apply(self.parse_features)
        df["availability"] = df["availability"].apply(self.clean_availability)

        # 4. Filter invalid records (Must have valid product_id, product_name, price, rating)
        valid_mask = (
            df["product_id"].ne("") &
            df["product_name"].ne("") &
            df["price"].notnull() &
            df["rating"].notnull() &
            (df["features"].apply(len) > 0)
        )
        invalid_dropped = int((~valid_mask).sum())
        df = df[valid_mask].copy()

        # 5. Deduplicate product_id keeping first valid record
        id_dups_count = int(df["product_id"].duplicated().sum())
        df = df.drop_duplicates(subset=["product_id"], keep="first").copy()

        # Final usable count
        final_rows = len(df)

        report = {
            "initial_rows": initial_rows,
            "exact_duplicates_removed": exact_dups_removed,
            "invalid_records_dropped": invalid_dropped,
            "duplicate_ids_resolved": id_dups_count,
            "final_usable_rows": final_rows,
            "categories": df["category"].unique().tolist(),
            "brands_count": int(df["brand"].nunique()),
            "price_range_inr": {
                "min": float(df["price"].min()),
                "max": float(df["price"].max()),
                "mean": round(float(df["price"].mean()), 2),
            },
            "rating_range": {
                "min": float(df["rating"].min()),
                "max": float(df["rating"].max()),
                "mean": round(float(df["rating"].mean()), 2),
            }
        }

        return df, report

    def save_processed_data(self, df: pd.DataFrame, output_path: Optional[Path] = None):
        """Saves cleaned dataset to CSV and populates SQLite database."""
        out_csv = output_path or config.paths.PROCESSED_DATA_FILE
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        
        # Save CSV (format features as JSON string for CSV persistence)
        csv_df = df.copy()
        csv_df["features"] = csv_df["features"].apply(json.dumps)
        csv_df.to_csv(out_csv, index=False, encoding="utf-8")

        # Save to SQLite Database
        db.populate_products(df)


def run_pipeline() -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Runs data cleaning, saves to disk and database, returns report."""
    preprocessor = DataPreprocessor()
    df, report = preprocessor.run_cleaning_pipeline()
    preprocessor.save_processed_data(df)
    return df, report


if __name__ == "__main__":
    df, report = run_pipeline()
    print("Data Cleaning Pipeline Execution Report:")
    print(json.dumps(report, indent=2))

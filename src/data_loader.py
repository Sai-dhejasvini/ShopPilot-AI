"""
ShopPilot AI - Data Loader Module
Handles raw CSV loading, validation of required target schema, and schema inspection.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd

from src.config import config


REQUIRED_COLUMNS: List[str] = [
    "product_id",
    "product_name",
    "category",
    "subcategory",
    "brand",
    "price",
    "rating",
    "review_count",
    "description",
    "features",
    "availability",
]


class DataLoaderError(Exception):
    """Custom exception raised when data loading or validation fails."""
    pass


class DataLoader:
    """
    Responsible for loading raw and processed datasets from disk,
    verifying target column headers, and generating structural summaries.
    """

    def __init__(self, raw_data_path: Optional[Path] = None):
        self.raw_data_path = raw_data_path or config.paths.RAW_DATA_FILE

    def load_raw_data(self) -> pd.DataFrame:
        """
        Loads the raw CSV dataset into a Pandas DataFrame.

        Raises:
            DataLoaderError: If file not found or corrupted.
        """
        if not self.raw_data_path.exists():
            raise DataLoaderError(
                f"Raw dataset file not found at: {self.raw_data_path}. "
                f"Please ensure the file exists or run the data generator."
            )

        try:
            df = pd.read_csv(self.raw_data_path, encoding="utf-8")
        except Exception as e:
            raise DataLoaderError(f"Failed to read CSV at {self.raw_data_path}: {str(e)}")

        self.validate_schema(df)
        return df

    def validate_schema(self, df: pd.DataFrame) -> bool:
        """
        Validates that all required columns are present in the DataFrame.

        Raises:
            DataLoaderError: If any required column is missing.
        """
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            raise DataLoaderError(
                f"Dataset is missing required columns: {missing_cols}. "
                f"Expected columns: {REQUIRED_COLUMNS}"
            )
        return True

    def get_dataset_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generates comprehensive dataset profile summary for inspection.
        """
        return {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "duplicate_ids": int(df["product_id"].duplicated().sum()) if "product_id" in df.columns else 0,
            "duplicate_rows": int(df.duplicated().sum()),
            "categories": df["category"].dropna().unique().tolist() if "category" in df.columns else [],
            "brands_count": df["brand"].nunique() if "brand" in df.columns else 0,
        }


def load_raw_dataset() -> pd.DataFrame:
    """Convenience function to load raw dataset with default config."""
    loader = DataLoader()
    return loader.load_raw_data()

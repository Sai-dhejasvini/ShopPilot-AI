"""
ShopPilot AI - Preprocessing & Cleaning Test Suite
"""

import pandas as pd
from backend.preprocessing import DataPreprocessor, run_pipeline
from backend.database import db


def test_clean_price():
    """Verify currency cleaning, comma stripping, and invalid price rejection."""
    assert DataPreprocessor.clean_price("₹ 1,09,990") == 109990.0
    assert DataPreprocessor.clean_price("62,990.50") == 62990.50
    assert DataPreprocessor.clean_price("₹-500") is None
    assert DataPreprocessor.clean_price("N/A") is None
    assert DataPreprocessor.clean_price(None) is None


def test_clean_rating():
    """Verify rating boundary enforcement (0.0 to 5.0)."""
    assert DataPreprocessor.clean_rating("4.8") == 4.8
    assert DataPreprocessor.clean_rating("5.0") == 5.0
    assert DataPreprocessor.clean_rating("6.2") is None
    assert DataPreprocessor.clean_rating("-1.0") is None
    assert DataPreprocessor.clean_rating("None") is None


def test_parse_features():
    """Verify feature string and JSON parsing."""
    res1 = DataPreprocessor.parse_features("16GB RAM, 512GB SSD, M2 Chip")
    assert res1 == ["16GB RAM", "512GB SSD", "M2 Chip"]

    res2 = DataPreprocessor.parse_features('["16GB RAM", "RTX 4060"]')
    assert res2 == ["16GB RAM", "RTX 4060"]

    assert DataPreprocessor.parse_features(None) == []


def test_clean_availability():
    """Verify availability mapping to boolean."""
    assert DataPreprocessor.clean_availability("In Stock") is True
    assert DataPreprocessor.clean_availability("True") is True
    assert DataPreprocessor.clean_availability("Out of Stock") is False
    assert DataPreprocessor.clean_availability("False") is False
    assert DataPreprocessor.clean_availability(None) is False


def test_run_cleaning_pipeline_integrity():
    """Verify full end-to-end cleaning pipeline and reporting."""
    df, report = run_pipeline()
    assert report["final_usable_rows"] > 0
    assert report["invalid_records_dropped"] >= 2
    assert report["exact_duplicates_removed"] >= 1
    assert df["price"].min() >= 0
    assert df["rating"].max() <= 5.0
    assert df["rating"].min() >= 0.0

    # Verify SQLite population
    products = db.get_all_products()
    assert len(products) == len(df)

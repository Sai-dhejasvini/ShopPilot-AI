"""
ShopPilot AI - Data Loader Test Suite
"""

import pytest
import pandas as pd
from pathlib import Path
from backend.data_loader import DataLoader, DataLoaderError, REQUIRED_COLUMNS, load_raw_dataset


def test_load_raw_dataset_success():
    """Verify loading raw dataset returns a valid DataFrame."""
    df = load_raw_dataset()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    for col in REQUIRED_COLUMNS:
        assert col in df.columns


def test_schema_validation_missing_column(tmp_path):
    """Verify DataLoader raises DataLoaderError when required columns are missing."""
    invalid_csv = tmp_path / "invalid.csv"
    invalid_df = pd.DataFrame({
        "product_id": ["P1"],
        "product_name": ["Test"],
        "category": ["Electronics"]
    })
    invalid_df.to_csv(invalid_csv, index=False)

    loader = DataLoader(raw_data_path=invalid_csv)
    with pytest.raises(DataLoaderError) as exc_info:
        loader.load_raw_data()
    assert "missing required columns" in str(exc_info.value)


def test_missing_file_handling():
    """Verify DataLoader raises DataLoaderError for nonexistent file paths."""
    loader = DataLoader(raw_data_path=Path("non_existent_file_12345.csv"))
    with pytest.raises(DataLoaderError) as exc_info:
        loader.load_raw_data()
    assert "Raw dataset file not found" in str(exc_info.value)


def test_dataset_summary_diagnostics():
    """Verify dataset summary outputs accurate structural metadata."""
    loader = DataLoader()
    df = loader.load_raw_data()
    summary = loader.get_dataset_summary(df)

    assert "total_rows" in summary
    assert summary["total_rows"] == len(df)
    assert "missing_values" in summary
    assert "duplicate_ids" in summary
    assert len(summary["categories"]) > 0

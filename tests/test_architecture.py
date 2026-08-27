"""
ShopPilot AI - Architecture Verification Tests
Verifies schemas, configuration loading, directory initialization, and weight validation.
"""

from pathlib import Path
from src.config import config, PathConfig, RankingWeights
from src.schema import (
    Product,
    ExtractedRequirement,
    ScoreBreakdown,
    RankedProduct,
    AgentToolCall,
    GrowthInsight,
)


def test_path_config():
    """Verify that path configurations point to valid relative paths."""
    assert isinstance(config.paths.ROOT_DIR, Path)
    assert config.paths.DATA_DIR.name == "data"
    assert config.paths.RAW_DATA_DIR.name == "raw"
    assert config.paths.PROCESSED_DATA_DIR.name == "processed"


def test_ranking_weights_sum():
    """Verify default ranking weights sum to 1.0."""
    assert config.ranking.validate_weights() is True


def test_product_schema_validation():
    """Verify Product schema creation and field constraints."""
    prod_data = {
        "product_id": "PROD_001",
        "product_name": "Apple MacBook Air M2",
        "category": "Laptop",
        "subcategory": "Ultrabook",
        "brand": "Apple",
        "price": 89990.0,
        "rating": 4.8,
        "review_count": 1250,
        "description": "Apple M2 chip with 8-core CPU and 16GB Unified Memory.",
        "features": ["16GB RAM", "512GB SSD", "M2 Chip", "18-hour battery"],
        "availability": True,
    }
    prod = Product(**prod_data)
    assert prod.product_id == "PROD_001"
    assert prod.price == 89990.0
    assert len(prod.features) == 4


def test_extracted_requirement_schema():
    """Verify requirement extraction validation and budget constraints."""
    req_data = {
        "category": "Laptop",
        "min_price": 50000.0,
        "max_price": 75000.0,
        "brand_preference": ["ASUS", "Lenovo"],
        "required_features": ["16GB RAM", "IPS Display"],
        "priority": "performance",
        "use_case": "Programming",
    }
    req = ExtractedRequirement(**req_data)
    assert req.category == "Laptop"
    assert req.max_price == 75000.0


def test_ranked_product_schema():
    """Verify RankedProduct composition with ScoreBreakdown."""
    prod = Product(
        product_id="P1",
        product_name="Lenovo IdeaPad Gaming 3",
        category="Laptop",
        brand="Lenovo",
        price=54990.0,
        rating=4.3,
        review_count=840,
        features=["16GB RAM", "RTX 3050"],
    )
    scores = ScoreBreakdown(
        budget_fit_score=0.95,
        rating_score=0.86,
        feature_match_score=1.0,
        popularity_score=0.80,
        availability_score=1.0,
        final_score=0.92,
        explanation="Strong budget fit and complete match for 16GB RAM requirement.",
    )
    ranked = RankedProduct(product=prod, rank=1, scores=scores)
    assert ranked.rank == 1
    assert ranked.scores.final_score == 0.92

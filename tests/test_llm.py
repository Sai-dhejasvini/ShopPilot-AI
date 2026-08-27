"""
ShopPilot AI - LLM Extraction & Synthesis Test Suite
"""

import pytest
from backend.llm import LLMClient
from backend.schema import Product, RankedProduct, ScoreBreakdown


@pytest.fixture
def mock_llm_client():
    return LLMClient(provider="mock")


def test_mock_llm_laptop_extraction(mock_llm_client):
    """Verify parsing user prompt into ExtractedRequirement schema."""
    query = "I need a laptop under ₹70,000 for programming with 16GB RAM and good battery life."
    req = mock_llm_client.extract_requirements(query)

    assert req.category == "Laptop"
    assert req.max_price == 70000.0
    assert req.use_case == "Programming"
    assert any("16GB RAM" in f for f in req.required_features)
    assert req.priority == "battery life"


def test_mock_llm_smartphone_extraction(mock_llm_client):
    """Verify smartphone query extraction."""
    query = "Looking for an Apple or Samsung phone under 80k with OLED display"
    req = mock_llm_client.extract_requirements(query)

    assert req.category == "Smartphone"
    assert req.max_price == 80000.0
    assert "Apple" in req.brand_preference or "Samsung" in req.brand_preference
    assert any("OLED" in f for f in req.required_features)


def test_mock_llm_grounded_synthesis(mock_llm_client):
    """Verify synthesis produces factual explanation referencing actual products."""
    prod = Product(
        product_id="LAP004",
        product_name="Lenovo ThinkPad E14",
        category="Laptop",
        brand="Lenovo",
        price=62990.0,
        rating=4.4,
        review_count=1120,
        features=["16GB RAM", "512GB SSD"],
        availability=True,
    )
    scores = ScoreBreakdown(
        budget_fit_score=0.95,
        rating_score=0.88,
        feature_match_score=1.0,
        popularity_score=0.75,
        availability_score=1.0,
        final_score=0.92,
        explanation="Fits budget and matches 16GB RAM",
    )
    ranked = [RankedProduct(product=prod, rank=1, scores=scores)]

    reply = mock_llm_client.synthesize_response("laptop under 70k", ranked)
    assert "Lenovo ThinkPad E14" in reply
    assert "₹62,990" in reply
    assert "4.4★" in reply

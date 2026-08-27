"""
ShopPilot AI - Ranking & Recommender Test Suite
"""

import pytest
from backend.schema import Product, ExtractedRequirement
from backend.config import RankingWeights
from backend.ranking import RankingEngine
from backend.recommender import Recommender
from backend.search import SearchEngine


@pytest.fixture
def sample_catalog():
    return [
        Product(
            product_id="LAP001",
            product_name="Apple MacBook Air M2",
            category="Laptop",
            brand="Apple",
            price=109990.0,
            rating=4.8,
            review_count=2450,
            description="Apple M2 chip 16GB RAM 512GB SSD",
            features=["16GB RAM", "512GB SSD", "M2 Chip", "18hr battery"],
            availability=True,
        ),
        Product(
            product_id="LAP004",
            product_name="Lenovo ThinkPad E14",
            category="Laptop",
            brand="Lenovo",
            price=62990.0,
            rating=4.4,
            review_count=1120,
            description="Core i5 16GB RAM 512GB SSD",
            features=["16GB RAM", "512GB SSD", "Core i5"],
            availability=True,
        ),
        Product(
            product_id="LAP008",
            product_name="Lenovo IdeaPad Gaming 3",
            category="Laptop",
            brand="Lenovo",
            price=54990.0,
            rating=4.3,
            review_count=3200,
            description="AMD Ryzen 5 RTX 3050 16GB RAM",
            features=["16GB RAM", "512GB SSD", "RTX 3050"],
            availability=True,
        ),
    ]


def test_ranking_score_bounds(sample_catalog):
    """Verify all individual and final scores are within [0.0, 1.0]."""
    ranker = RankingEngine()
    req = ExtractedRequirement(category="Laptop", max_price=70000.0, required_features=["16GB RAM"])
    ranked = ranker.rank_products(sample_catalog, req)

    assert len(ranked) == 3
    for rp in ranked:
        assert 0.0 <= rp.scores.budget_fit_score <= 1.0
        assert 0.0 <= rp.scores.rating_score <= 1.0
        assert 0.0 <= rp.scores.feature_match_score <= 1.0
        assert 0.0 <= rp.scores.popularity_score <= 1.0
        assert 0.0 <= rp.scores.availability_score <= 1.0
        assert 0.0 <= rp.scores.final_score <= 1.0
        assert len(rp.scores.explanation) > 0


def test_ranking_sort_order(sample_catalog):
    """Verify products within budget and high feature match rank higher."""
    ranker = RankingEngine()
    req = ExtractedRequirement(category="Laptop", max_price=65000.0, required_features=["16GB RAM", "RTX 3050"])
    ranked = ranker.rank_products(sample_catalog, req)

    # LAP008 has RTX 3050 and is well under 65k budget
    assert ranked[0].product.product_id == "LAP008"
    assert ranked[0].rank == 1


def test_recommender_integration(sample_catalog):
    """Verify end-to-end recommendation workflow."""
    searcher = SearchEngine(products=sample_catalog)
    ranker = RankingEngine()
    rec = Recommender(searcher=searcher, ranker=ranker)

    req = ExtractedRequirement(category="Laptop", max_price=70000.0, required_features=["16GB RAM"])
    results = rec.recommend(req, top_n=2)

    assert len(results) == 2
    assert results[0].scores.final_score >= results[1].scores.final_score

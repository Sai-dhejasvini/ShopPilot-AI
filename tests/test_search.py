"""
ShopPilot AI - Deterministic Search Engine Test Suite
"""

import pytest
from backend.schema import Product, ExtractedRequirement
from backend.search import SearchEngine


@pytest.fixture
def sample_search_engine():
    products = [
        Product(
            product_id="LAP001",
            product_name="Apple MacBook Air M2",
            category="Laptop",
            subcategory="Ultrabook",
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
            subcategory="Business",
            brand="Lenovo",
            price=62990.0,
            rating=4.4,
            review_count=1120,
            description="Intel Core i5 13th Gen 16GB RAM 512GB SSD",
            features=["16GB RAM", "512GB SSD", "Core i5", "FHD IPS"],
            availability=True,
        ),
        Product(
            product_id="LAP008",
            product_name="Lenovo IdeaPad Gaming 3",
            category="Laptop",
            subcategory="Gaming",
            brand="Lenovo",
            price=54990.0,
            rating=4.3,
            review_count=3200,
            description="AMD Ryzen 5 RTX 3050 16GB RAM",
            features=["16GB RAM", "512GB SSD", "RTX 3050", "Ryzen 5"],
            availability=True,
        ),
        Product(
            product_id="PHN001",
            product_name="Apple iPhone 15",
            category="Smartphone",
            subcategory="Flagship",
            brand="Apple",
            price=71999.0,
            rating=4.7,
            review_count=8450,
            description="Dynamic Island 48MP camera A16 Bionic",
            features=["128GB Storage", "6GB RAM", "A16 Bionic", "48MP Camera"],
            availability=True,
        ),
        Product(
            product_id="PHN006",
            product_name="OnePlus Nord CE 4",
            category="Smartphone",
            subcategory="Mid-range",
            brand="OnePlus",
            price=24999.0,
            rating=4.4,
            review_count=9400,
            description="Snapdragon 7 Gen 3 100W Charging",
            features=["128GB Storage", "8GB RAM", "100W Fast Charge"],
            availability=False,  # Out of stock
        ),
    ]
    return SearchEngine(products=products)


def test_search_category_filter(sample_search_engine):
    """Verify category filtering isolates target items."""
    results = sample_search_engine.search(category="Laptop")
    assert len(results) == 3
    for p in results:
        assert p.category == "Laptop"


def test_search_price_budget_filter(sample_search_engine):
    """Verify budget bounds correctly filter items in INR."""
    # Laptops under 70k
    results = sample_search_engine.search(category="Laptop", max_price=70000.0)
    assert len(results) == 2
    for p in results:
        assert p.price <= 70000.0


def test_search_brand_filter(sample_search_engine):
    """Verify brand filtering works case-insensitively."""
    results = sample_search_engine.search(brands=["lenovo"])
    assert len(results) == 2
    for p in results:
        assert p.brand.lower() == "lenovo"


def test_search_feature_regex_match(sample_search_engine):
    """Verify feature regex matching (e.g. RTX GPU)."""
    results = sample_search_engine.search(required_features=["RTX 3050"])
    assert len(results) == 1
    assert results[0].product_id == "LAP008"


def test_search_availability_filter(sample_search_engine):
    """Verify out-of-stock items are excluded by default."""
    results_in_stock = sample_search_engine.search(category="Smartphone", availability_only=True)
    assert len(results_in_stock) == 1
    assert results_in_stock[0].product_id == "PHN001"

    results_all = sample_search_engine.search(category="Smartphone", availability_only=False)
    assert len(results_all) == 2


def test_search_empty_results(sample_search_engine):
    """Verify empty list returned gracefully when no products match."""
    results = sample_search_engine.search(category="Laptop", max_price=10000.0)
    assert results == []


def test_search_by_requirements_schema(sample_search_engine):
    """Verify searching via ExtractedRequirement Pydantic object."""
    req = ExtractedRequirement(
        category="Laptop",
        max_price=65000.0,
        required_features=["16GB RAM"]
    )
    results = sample_search_engine.search_by_requirements(req)
    assert len(results) == 2
    for p in results:
        assert p.price <= 65000.0

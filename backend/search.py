"""
ShopPilot AI - Deterministic Product Search Engine
Provides fast, parametric, vectorless filtering across categories, price bounds,
brands, rating thresholds, and technical feature regular expressions.
"""

import re
from typing import List, Optional, Dict, Any
from backend.schema import Product, ExtractedRequirement
from backend.database import db


class SearchEngine:
    """
    Deterministic search engine for filtering products without LLM hallucination risk.
    Operates on verified in-memory / SQLite catalog records.
    """

    def __init__(self, products: Optional[List[Product]] = None):
        self._products = products or db.get_all_products()

    def reload_products(self):
        """Reloads products from database."""
        self._products = db.get_all_products()

    def search(
        self,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        brands: Optional[List[str]] = None,
        min_rating: Optional[float] = None,
        required_features: Optional[List[str]] = None,
        availability_only: bool = True,
        sort_by: str = "rating_desc",
        top_n: Optional[int] = None,
    ) -> List[Product]:
        """
        Executes deterministic multi-criteria filter over catalog products.
        """
        results = self._products

        # 1. Filter Category
        if category:
            cat_norm = category.strip().lower()
            results = [
                p for p in results
                if p.category.lower() == cat_norm or p.subcategory.lower() == cat_norm
            ]

        # 2. Filter Price Bounds (INR)
        if min_price is not None:
            results = [p for p in results if p.price >= min_price]
        if max_price is not None:
            results = [p for p in results if p.price <= max_price]

        # 3. Filter Brands (Case-Insensitive)
        if brands:
            brands_lower = {b.strip().lower() for b in brands if b.strip()}
            if brands_lower:
                results = [p for p in results if p.brand.lower() in brands_lower]

        # 4. Filter Minimum Rating
        if min_rating is not None:
            results = [p for p in results if p.rating >= min_rating]

        # 5. Filter Stock Availability
        if availability_only:
            results = [p for p in results if p.availability is True]

        # 6. Filter Required Features (Regex / Substring Match in name, description, or features)
        if required_features:
            for feat in required_features:
                feat_clean = feat.strip()
                if not feat_clean:
                    continue
                pattern = re.compile(re.escape(feat_clean), re.IGNORECASE)
                results = [
                    p for p in results
                    if pattern.search(p.product_name)
                    or pattern.search(p.description)
                    or any(pattern.search(f) for f in p.features)
                ]

        # 7. Sorting
        if sort_by == "price_asc":
            results = sorted(results, key=lambda p: p.price)
        elif sort_by == "price_desc":
            results = sorted(results, key=lambda p: p.price, reverse=True)
        elif sort_by == "rating_desc":
            results = sorted(results, key=lambda p: (p.rating, p.review_count), reverse=True)
        elif sort_by == "popularity_desc":
            results = sorted(results, key=lambda p: p.review_count, reverse=True)
        elif sort_by == "discount_desc":
            results = sorted(results, key=lambda p: (p.discount_percentage or 0.0), reverse=True)

        # 8. Top-N Limiting
        if top_n is not None and top_n > 0:
            results = results[:top_n]

        return results

    def search_by_requirements(
        self, req: ExtractedRequirement, top_n: Optional[int] = None
    ) -> List[Product]:
        """Convenience method to search directly with an ExtractedRequirement schema."""
        return self.search(
            category=req.category,
            min_price=req.min_price,
            max_price=req.max_price,
            brands=req.brand_preference,
            min_rating=req.min_rating,
            required_features=req.required_features,
            top_n=top_n,
        )

    def get_by_id(self, product_id: str) -> Optional[Product]:
        """Retrieves single product by product_id."""
        for p in self._products:
            if p.product_id.lower() == product_id.strip().lower():
                return p
        return None

    def get_by_ids(self, product_ids: List[str]) -> List[Product]:
        """Retrieves multiple products preserving input order."""
        id_set = {pid.strip().lower() for pid in product_ids}
        id_map = {p.product_id.lower(): p for p in self._products if p.product_id.lower() in id_set}
        return [id_map[pid.strip().lower()] for pid in product_ids if pid.strip().lower() in id_map]


# Global search engine instance
search_engine = SearchEngine()

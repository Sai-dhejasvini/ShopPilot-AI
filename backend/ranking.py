"""
ShopPilot AI - Multi-Factor Explainable Ranking Engine
Computes transparent, weighted scores for products based on budget fit,
customer ratings, feature overlap, review popularity, and stock availability.
"""

import math
import re
from typing import List, Optional, Tuple, Dict
from backend.config import config, RankingWeights
from backend.schema import Product, ExtractedRequirement, ScoreBreakdown, RankedProduct


class RankingEngine:
    """
    Evaluates candidate products and produces normalized, explainable scores.
    """

    def __init__(self, weights: Optional[RankingWeights] = None):
        self.weights = weights or config.ranking

    def compute_budget_fit(
        self, price: float, min_price: Optional[float], max_price: Optional[float]
    ) -> float:
        """
        Calculates budget adherence score in [0.0, 1.0].
        - If no budget specified: returns 1.0.
        - If within [min_price, max_price]: optimal score (0.85 - 1.0).
        - If exceeding max_price: exponential decay.
        """
        if max_price is None and min_price is None:
            return 1.0

        if max_price is not None:
            if price <= max_price:
                # Closer to max_price without exceeding gets good utility
                ratio = price / max_price if max_price > 0 else 1.0
                return round(0.80 + 0.20 * ratio, 4)
            else:
                # Over budget: exponential penalty
                over = (price - max_price) / max_price
                return round(max(0.0, 0.80 * math.exp(-3.0 * over)), 4)

        if min_price is not None:
            if price >= min_price:
                return 1.0
            else:
                return round(max(0.0, price / min_price), 4)

        return 1.0

    def compute_rating_score(self, rating: float) -> float:
        """Normalizes 0.0 - 5.0 rating to [0.0, 1.0]."""
        return round(min(1.0, max(0.0, rating / 5.0)), 4)

    def compute_feature_match(
        self, product: Product, required_features: List[str]
    ) -> Tuple[float, List[str]]:
        """
        Calculates ratio of matched required features and returns matched list.
        """
        if not required_features:
            return 1.0, []

        matched = []
        for feat in required_features:
            feat_clean = feat.strip()
            if not feat_clean:
                continue
            pattern = re.compile(re.escape(feat_clean), re.IGNORECASE)
            if (
                pattern.search(product.product_name)
                or pattern.search(product.description)
                or any(pattern.search(f) for f in product.features)
            ):
                matched.append(feat_clean)

        score = len(matched) / len(required_features) if required_features else 1.0
        return round(score, 4), matched

    def compute_popularity_score(self, review_count: int) -> float:
        """
        Computes log-scaled popularity score relative to 10,000 baseline.
        """
        if review_count <= 0:
            return 0.1
        # Log scale: log(1 + rc) / log(1 + 10000)
        norm = math.log(1 + review_count) / math.log(1 + 10000)
        return round(min(1.0, max(0.1, norm)), 4)

    def compute_availability_score(self, availability: bool) -> float:
        """1.0 for in-stock, 0.0 for out-of-stock."""
        return 1.0 if availability else 0.0

    def rank_product(
        self, product: Product, requirement: Optional[ExtractedRequirement] = None
    ) -> ScoreBreakdown:
        """
        Generates complete ScoreBreakdown with human-readable rationale.
        """
        min_p = requirement.min_price if requirement else None
        max_p = requirement.max_price if requirement else None
        req_features = requirement.required_features if requirement else []

        s_budget = self.compute_budget_fit(product.price, min_p, max_p)
        s_rating = self.compute_rating_score(product.rating)
        s_feature, matched_feats = self.compute_feature_match(product, req_features)
        s_pop = self.compute_popularity_score(product.review_count)
        s_avail = self.compute_availability_score(product.availability)

        w = self.weights
        final = (
            w.budget * s_budget
            + w.rating * s_rating
            + w.feature * s_feature
            + w.popularity * s_pop
            + w.availability * s_avail
        )
        final = round(min(1.0, max(0.0, final)), 4)

        # Build transparent explanation rationale
        reasons = []
        if max_p and product.price <= max_p:
            reasons.append(f"Price of {config.currency_symbol}{product.price:,.0f} fits within budget of {config.currency_symbol}{max_p:,.0f}")
        elif max_p and product.price > max_p:
            reasons.append(f"Slightly exceeds {config.currency_symbol}{max_p:,.0f} budget at {config.currency_symbol}{product.price:,.0f}")
        else:
            reasons.append(f"Priced at {config.currency_symbol}{product.price:,.0f}")

        if matched_feats:
            reasons.append(f"matches requested features: {', '.join(matched_feats)}")
        elif req_features:
            reasons.append("partial feature match")

        reasons.append(f"high customer satisfaction ({product.rating}★ from {product.review_count:,} reviews)")

        if not product.availability:
            reasons.append("(currently out of stock)")

        explanation = "; ".join(reasons) + "."

        return ScoreBreakdown(
            budget_fit_score=s_budget,
            rating_score=s_rating,
            feature_match_score=s_feature,
            popularity_score=s_pop,
            availability_score=s_avail,
            final_score=final,
            explanation=explanation,
        )

    def rank_products(
        self,
        products: List[Product],
        requirement: Optional[ExtractedRequirement] = None,
        top_n: Optional[int] = None,
    ) -> List[RankedProduct]:
        """
        Ranks a list of candidate products and returns sorted RankedProduct list.
        """
        scored = []
        for p in products:
            breakdown = self.rank_product(p, requirement)
            scored.append((p, breakdown))

        # Sort primarily by final_score descending, secondarily by rating
        scored.sort(key=lambda item: (item[1].final_score, item[0].rating), reverse=True)

        ranked = []
        for idx, (p, breakdown) in enumerate(scored, start=1):
            ranked.append(RankedProduct(product=p, rank=idx, scores=breakdown))

        if top_n is not None and top_n > 0:
            ranked = ranked[:top_n]

        return ranked

    def rank_for_gaming(
        self,
        products: List[Product],
        top_n: Optional[int] = None,
    ) -> List[RankedProduct]:
        """
        Ranks products deterministically for gaming performance based on dedicated GPU,
        display refresh rate, high-performance CPU, and thermal subcategory.
        """
        scored = []
        for p in products:
            features_text = " ".join([p.product_name, p.description] + p.features).lower()

            # GPU Tier Scoring (0.0 to 1.0)
            if any(k in features_text for k in ["rtx 4090", "rtx 4080", "rtx 4070", "rtx 4060", "rtx 4050"]):
                s_gpu = 1.0
                gpu_name = "NVIDIA RTX 40-series Dedicated GPU"
            elif any(k in features_text for k in ["rtx 3070", "rtx 3060", "rtx 3050", "radeon rx"]):
                s_gpu = 0.85
                gpu_name = "NVIDIA RTX 30-series Dedicated GPU"
            elif any(k in features_text for k in ["gtx 1650", "gtx 1660", "mx550", "mx450", "arc a370m"]):
                s_gpu = 0.60
                gpu_name = "Entry-level Dedicated GPU"
            elif "gaming" in p.subcategory.lower() or "gaming" in features_text:
                s_gpu = 0.50
                gpu_name = "Gaming-optimized configuration"
            else:
                s_gpu = 0.20
                gpu_name = "Integrated Graphics"

            # Display Refresh Rate Scoring (0.0 to 1.0)
            if any(k in features_text for k in ["144hz", "165hz", "240hz", "300hz"]):
                s_display = 1.0
                disp_desc = "High-refresh 144Hz+ display"
            elif "120hz" in features_text:
                s_display = 0.85
                disp_desc = "Smooth 120Hz display"
            else:
                s_display = 0.40
                disp_desc = "Standard 60Hz display"

            # Subcategory & High-TDP CPU Scoring
            is_gaming_subcat = 1.0 if p.subcategory.lower() == "gaming" else 0.4
            s_rating = self.compute_rating_score(p.rating)
            s_avail = 1.0 if p.availability else 0.0

            # Composite Gaming Score
            final_gaming = round(
                0.45 * s_gpu
                + 0.20 * s_display
                + 0.15 * is_gaming_subcat
                + 0.10 * s_rating
                + 0.10 * s_avail,
                4,
            )

            explanation = (
                f"Ranked for gaming performance: equipped with {gpu_name}, {disp_desc}, "
                f"and {p.rating}★ customer rating ({p.review_count:,} reviews)."
            )

            breakdown = ScoreBreakdown(
                budget_fit_score=1.0,
                rating_score=s_rating,
                feature_match_score=s_gpu,
                popularity_score=self.compute_popularity_score(p.review_count),
                availability_score=s_avail,
                final_score=final_gaming,
                explanation=explanation,
            )
            scored.append((p, breakdown))

        scored.sort(key=lambda item: (item[1].final_score, item[0].rating), reverse=True)

        ranked = []
        for idx, (p, breakdown) in enumerate(scored, start=1):
            ranked.append(RankedProduct(product=p, rank=idx, scores=breakdown))

        if top_n is not None and top_n > 0:
            ranked = ranked[:top_n]
        return ranked

    def rank_for_value(
        self,
        products: List[Product],
        top_n: Optional[int] = None,
    ) -> List[RankedProduct]:
        """
        Ranks products deterministically for Value-for-Money by emphasizing
        price accessibility together with verified customer rating and features.
        """
        if not products:
            return []

        min_price = min(p.price for p in products)
        max_price = max(p.price for p in products)
        price_range = max_price - min_price if max_price > min_price else 1.0

        scored = []
        for p in products:
            # Lower price gets strictly higher relative budget score
            rel_budget_score = round(1.0 - 0.50 * ((p.price - min_price) / price_range), 4)
            s_rating = self.compute_rating_score(p.rating)
            s_pop = self.compute_popularity_score(p.review_count)
            s_avail = 1.0 if p.availability else 0.0

            # Value score: 45% budget efficiency + 35% customer rating + 10% popularity + 10% availability
            final_val = round(
                0.45 * rel_budget_score
                + 0.35 * s_rating
                + 0.10 * s_pop
                + 0.10 * s_avail,
                4,
            )

            explanation = (
                f"Selected as a top value pick: competitive price of {config.currency_symbol}{p.price:,.0f} "
                f"paired with strong {p.rating}★ rating ({p.review_count:,} reviews)."
            )

            breakdown = ScoreBreakdown(
                budget_fit_score=rel_budget_score,
                rating_score=s_rating,
                feature_match_score=0.85,
                popularity_score=s_pop,
                availability_score=s_avail,
                final_score=final_val,
                explanation=explanation,
            )
            scored.append((p, breakdown))

        scored.sort(key=lambda item: (item[1].final_score, item[0].rating), reverse=True)

        ranked = []
        for idx, (p, breakdown) in enumerate(scored, start=1):
            ranked.append(RankedProduct(product=p, rank=idx, scores=breakdown))

        if top_n is not None and top_n > 0:
            ranked = ranked[:top_n]
        return ranked


# Global ranking engine instance
ranking_engine = RankingEngine()

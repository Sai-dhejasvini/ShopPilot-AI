"""
ShopPilot AI - Recommendation Orchestration Engine
Combines deterministic search filtering with explainable multi-factor ranking.
"""

from typing import List, Optional
from backend.schema import Product, ExtractedRequirement, RankedProduct
from backend.search import search_engine, SearchEngine
from backend.ranking import ranking_engine, RankingEngine


class Recommender:
    """
    Orchestrates the end-to-end recommendation workflow:
    1. Deterministic filtering based on hard requirements.
    2. Fallback relaxation if zero results match.
    3. Multi-criteria explainable scoring.
    4. Top-N ranked candidate delivery.
    """

    def __init__(
        self,
        searcher: Optional[SearchEngine] = None,
        ranker: Optional[RankingEngine] = None,
    ):
        self.searcher = searcher or search_engine
        self.ranker = ranker or ranking_engine

    def recommend(
        self,
        requirement: ExtractedRequirement,
        top_n: int = 5,
        relax_on_empty: bool = True,
    ) -> List[RankedProduct]:
        """
        Executes search and ranking according to user requirements.
        """
        # 1. Primary Strict Search
        candidates = self.searcher.search_by_requirements(requirement)

        # 2. Relax constraints if zero candidates found (Graceful Degradation)
        if not candidates and relax_on_empty:
            # Relax features first
            relaxed_req = requirement.model_copy(update={"required_features": []})
            candidates = self.searcher.search_by_requirements(relaxed_req)

            # If still empty, relax budget by 20%
            if not candidates and requirement.max_price:
                relaxed_budget_req = relaxed_req.model_copy(
                    update={"max_price": requirement.max_price * 1.20}
                )
                candidates = self.searcher.search_by_requirements(relaxed_budget_req)

        if not candidates:
            return []

        # 3. Multi-factor ranking
        return self.ranker.rank_products(candidates, requirement, top_n=top_n)


# Global recommender instance
recommender = Recommender()

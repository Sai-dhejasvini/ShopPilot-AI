"""
ShopPilot AI - Autonomous Agent Orchestration Engine
Plans and sequences tool execution based on user intent, validates parameters,
integrates session conversational memory, and coordinates grounded response generation.
"""

import re
from typing import List, Dict, Any, Optional
from backend.schema import (
    ChatRequest,
    ChatResponse,
    AgentToolCall,
    ExtractedRequirement,
    RankedProduct,
    ScoreBreakdown,
    Product,
)
from backend.llm import llm_client, LLMClient
from backend.tools import (
    search_products,
    filter_products,
    rank_products,
    get_extreme_product,
    get_multi_criteria_extrema,
    rank_for_gaming,
    rank_for_value,
    get_product_details,
    compare_products,
    generate_growth_insight,
)
from backend.memory import memory_manager, SessionMemoryManager
from backend.database import db
from backend.config import config


class ShopPilotAgent:
    """
    Autonomous AI Commerce Agent that understands goals, sequences tools,
    maintains conversational memory, and returns grounded shopping recommendations.
    """

    def __init__(
        self,
        llm: Optional[LLMClient] = None,
        memory: Optional[SessionMemoryManager] = None,
    ):
        self.llm = llm or llm_client
        self.memory = memory or memory_manager

    def process_message(
        self,
        request: ChatRequest,
        previous_candidates: Optional[List[RankedProduct]] = None,
    ) -> ChatResponse:
        """
        Main entry point for agentic goal planning, tool execution, and synthesis.
        """
        user_text = request.message.strip()
        session_id = request.session_id or "default_session"
        tools_executed: List[AgentToolCall] = []

        # Retrieve context from session memory
        context = self.memory.get_context(session_id)
        last_candidates: List[RankedProduct] = previous_candidates or context.get("last_candidates", [])
        last_req: Optional[ExtractedRequirement] = context.get("last_requirement")

        q_lower = user_text.lower()

        # Helper to ensure we have candidate products to evaluate
        def get_active_candidates() -> List[Product]:
            req = self.llm.extract_requirements(user_text)
            
            is_followup = False
            if last_candidates:
                # 1. Explicit follow-up phrases
                if any(phrase in q_lower for phrase in ["which one", "of these", "which is", "which laptop", "which smartphone", "among these", "from the list", "compare the"]):
                    is_followup = True
                # 2. Implicit follow-up (no new constraints)
                elif not req.category and not req.min_price and not req.max_price and not req.required_features:
                    is_followup = True
                # 3. Same category and no new constraints means follow-up
                elif req.category and last_candidates[0].product.category.lower() == req.category.lower() and not req.min_price and not req.max_price and not req.required_features:
                    is_followup = True
                
                # 4. Explicit fresh search overrides
                if "show me" in q_lower or "find" in q_lower or "search" in q_lower or "under" in q_lower or "with " in q_lower:
                    is_followup = False

                # Additional safety: if they are asking for a completely different category, it's fresh
                if is_followup and req.category and last_candidates[0].product.category.lower() != req.category.lower():
                    is_followup = False

            if is_followup:
                return [rp.product for rp in last_candidates]

            return search_products(
                category=req.category,
                min_price=req.min_price,
                max_price=req.max_price,
                brands=req.brand_preference,
                min_rating=req.min_rating,
                required_features=req.required_features,
                top_n=None,
            )

        # -------------------------------------------------------------
        # Branch 1: Comparison of Extremes (e.g. "compare cheapest and highest-rated")
        # -------------------------------------------------------------
        is_compare_extremes = (
            any(w in q_lower for w in ["compare", "vs", "versus", "difference between"])
            and any(w in q_lower for w in ["cheap", "lowest price", "affordable"])
            and any(w in q_lower for w in ["rating", "rated", "best", "expensive", "reviews", "popular"])
            and not re.search(r"\b(?:LAP|PHN|AUD|WAT|ACC)\d{3}\b", user_text, re.IGNORECASE)
        )
        if is_compare_extremes:
            candidates = get_active_candidates()
            res = self._handle_compare_extremes(user_text, session_id, tools_executed, candidates)
            self.memory.record_turn(session_id, user_text, res.reply, last_req, last_candidates)
            return res

        # -------------------------------------------------------------
        # Branch 2: Explicit Product ID / Named Comparison Intent
        # -------------------------------------------------------------
        if any(w in q_lower for w in ["compare", "vs", "versus"]) and not any(w in q_lower for w in ["insight", "analytics"]):
            res = self._handle_comparison(user_text, session_id, tools_executed, last_candidates)
            self.memory.record_turn(session_id, user_text, res.reply, last_req, last_candidates)
            return res

        # -------------------------------------------------------------
        # Branch 3: Growth Analytics Intent
        # -------------------------------------------------------------
        if any(w in q_lower for w in ["growth insight", "analytics", "trend", "demand gap"]):
            res = self._handle_growth_insights(session_id, tools_executed)
            self.memory.record_turn(session_id, user_text, res.reply, last_req, last_candidates)
            return res

        # -------------------------------------------------------------
        # Branch 4: Specific Product Detail Intent
        # -------------------------------------------------------------
        if ("detail" in q_lower or "spec" in q_lower) and re.search(r"\b(?:LAP|PHN|AUD|WAT|ACC)\d{3}\b", user_text, re.IGNORECASE):
            detail_res = self._handle_product_details(user_text, session_id, tools_executed)
            if detail_res:
                self.memory.record_turn(session_id, user_text, detail_res.reply, last_req, last_candidates)
                return detail_res

        # -------------------------------------------------------------
        # Branch 5: Multi-Criteria Factual Extrema (e.g. "lowest price and highest rating")
        # -------------------------------------------------------------
        has_min_price = any(w in q_lower for w in ["lowest price", "cheapest", "least expensive", "lowest cost", "min price", "low price"])
        has_max_rating = any(w in q_lower for w in ["highest rating", "best rating", "top rating", "rated best", "highest rated", "max rating", "top rated"])
        has_max_reviews = any(w in q_lower for w in ["most reviews", "highest reviews", "highest number of reviews", "most popular"])
        has_max_price = any(w in q_lower for w in ["most expensive", "highest price", "costs the most", "priciest", "highest cost"])

        extrema_criteria_count = sum([bool(has_min_price), bool(has_max_rating), bool(has_max_reviews), bool(has_max_price)])
        if extrema_criteria_count >= 2:
            candidates = get_active_candidates()
            res = self._handle_multi_criteria_extrema(user_text, session_id, tools_executed, candidates, has_min_price, has_max_rating, has_max_reviews, has_max_price)
            candidates_to_store = last_candidates if (last_candidates and len(last_candidates) > len(res.products or [])) else (res.products or last_candidates)
            self.memory.record_turn(session_id, user_text, res.reply, last_req, candidates_to_store)
            return res

        # -------------------------------------------------------------
        # Branch 6: Single Factual Extrema Query (Cheapest, Most Expensive, Highest Rating, Most Reviews)
        # -------------------------------------------------------------
        # A. Lowest Price / Cheapest
        if any(w in q_lower for w in ["cheapest", "lowest price", "least expensive", "lowest cost", "most affordable", "what's the cheapest", "which is cheapest"]):
            candidates = get_active_candidates()
            res = self._handle_single_extreme(user_text, session_id, tools_executed, candidates, metric="price", direction="min")
            candidates_to_store = last_candidates if (last_candidates and len(last_candidates) > len(res.products or [])) else (res.products or last_candidates)
            self.memory.record_turn(session_id, user_text, res.reply, last_req, candidates_to_store)
            return res

        # B. Most Expensive / Highest Price
        if any(w in q_lower for w in ["most expensive", "highest price", "costs the most", "priciest", "highest cost", "which is most expensive"]):
            candidates = get_active_candidates()
            res = self._handle_single_extreme(user_text, session_id, tools_executed, candidates, metric="price", direction="max")
            candidates_to_store = last_candidates if (last_candidates and len(last_candidates) > len(res.products or [])) else (res.products or last_candidates)
            self.memory.record_turn(session_id, user_text, res.reply, last_req, candidates_to_store)
            return res

        # C. Highest Rating
        if any(w in q_lower for w in ["highest rating", "best rating", "top rated", "rated best", "highest rated", "best rated", "most stars", "which has the highest rating", "which is rated best"]):
            candidates = get_active_candidates()
            res = self._handle_single_extreme(user_text, session_id, tools_executed, candidates, metric="rating", direction="max")
            candidates_to_store = last_candidates if (last_candidates and len(last_candidates) > len(res.products or [])) else (res.products or last_candidates)
            self.memory.record_turn(session_id, user_text, res.reply, last_req, candidates_to_store)
            return res

        # D. Most Reviews / Highest review count
        if any(w in q_lower for w in ["most reviews", "highest reviews", "highest number of reviews", "most reviewed", "highest review count", "which has the most reviews"]):
            candidates = get_active_candidates()
            res = self._handle_single_extreme(user_text, session_id, tools_executed, candidates, metric="reviews", direction="max")
            candidates_to_store = last_candidates if (last_candidates and len(last_candidates) > len(res.products or [])) else (res.products or last_candidates)
            self.memory.record_turn(session_id, user_text, res.reply, last_req, candidates_to_store)
            return res

        # E. Lowest Rating
        if any(w in q_lower for w in ["lowest rating", "worst rating", "lowest rated", "worst rated", "least stars", "which has the lowest rating"]):
            candidates = get_active_candidates()
            res = self._handle_single_extreme(user_text, session_id, tools_executed, candidates, metric="rating", direction="min")
            candidates_to_store = last_candidates if (last_candidates and len(last_candidates) > len(res.products or [])) else (res.products or last_candidates)
            self.memory.record_turn(session_id, user_text, res.reply, last_req, candidates_to_store)
            return res

        # F. Fewest Reviews / Lowest review count
        if any(w in q_lower for w in ["fewest reviews", "least reviews", "lowest reviews", "least reviewed", "which has the least reviews", "which has the fewest reviews"]):
            candidates = get_active_candidates()
            res = self._handle_single_extreme(user_text, session_id, tools_executed, candidates, metric="reviews", direction="min")
            candidates_to_store = last_candidates if (last_candidates and len(last_candidates) > len(res.products or [])) else (res.products or last_candidates)
            self.memory.record_turn(session_id, user_text, res.reply, last_req, candidates_to_store)
            return res

        # -------------------------------------------------------------
        # Branch 7: Gaming-Specific Query
        # -------------------------------------------------------------
        if any(w in q_lower for w in ["gaming", "games", "gameplay", "best for gaming", "gaming laptop", "gaming performance"]):
            candidates = get_active_candidates()
            res = self._handle_gaming(user_text, session_id, tools_executed, candidates)
            candidates_to_store = last_candidates if (last_candidates and len(last_candidates) > len(res.products or [])) else (res.products or last_candidates)
            self.memory.record_turn(session_id, user_text, res.reply, last_req, candidates_to_store)
            return res

        # -------------------------------------------------------------
        # Branch 8: Value for Money Query
        # -------------------------------------------------------------
        if any(w in q_lower for w in ["best value", "value for money", "bang for buck", "price to performance", "best value for money"]):
            candidates = get_active_candidates()
            res = self._handle_value(user_text, session_id, tools_executed, candidates)
            candidates_to_store = last_candidates if (last_candidates and len(last_candidates) > len(res.products or [])) else (res.products or last_candidates)
            self.memory.record_turn(session_id, user_text, res.reply, last_req, candidates_to_store)
            return res

        # -------------------------------------------------------------
        # Branch 9: General Follow-Up on Existing Candidates (Battery, RAM, Display, etc.)
        # -------------------------------------------------------------
        is_context_followup = bool(
            last_candidates
            and any(w in q_lower for w in ["which one", "which of these", "best battery", "more ram", "battery life", "display", "screen", "first one", "second one"])
        )
        if is_context_followup:
            candidates = [rp.product for rp in last_candidates]
            res = self._handle_feature_followup(user_text, session_id, tools_executed, candidates)
            candidates_to_store = last_candidates if (last_candidates and len(last_candidates) > len(res.products or [])) else (res.products or last_candidates)
            self.memory.record_turn(session_id, user_text, res.reply, last_req, candidates_to_store)
            return res

        # -------------------------------------------------------------
        # Branch 10: Primary Shopping Discovery & Recommendation Flow
        # -------------------------------------------------------------
        res = self._handle_recommendation(user_text, session_id, tools_executed)
        req = self.llm.extract_requirements(user_text)
        self.memory.record_turn(session_id, user_text, res.reply, req, res.products)
        return res

    def _handle_single_extreme(
        self,
        user_text: str,
        session_id: str,
        tools_executed: List[AgentToolCall],
        candidates: List[Product],
        metric: str,
        direction: str,
    ) -> ChatResponse:
        """Handles deterministic single-metric extrema selection (cheapest, most expensive, highest rating, most reviews)."""
        if not candidates:
            return ChatResponse(
                reply="I could not find candidate products to evaluate. Please search for a product category first.",
                session_id=session_id,
                tools_used=tools_executed,
            )

        metric_desc = {
            ("price", "min"): ("minimum price", "cheapest option"),
            ("price", "max"): ("maximum price", "most expensive option"),
            ("rating", "max"): ("maximum customer rating", "highest-rated option"),
            ("rating", "min"): ("minimum customer rating", "lowest-rated option"),
            ("reviews", "max"): ("maximum verified reviews", "most reviewed option"),
            ("reviews", "min"): ("minimum verified reviews", "least reviewed option"),
        }.get((metric, direction), (f"{direction} {metric}", f"{direction} {metric}"))

        tools_executed.append(
            AgentToolCall(
                tool_name="get_extreme_product",
                parameters={"metric": metric, "direction": direction, "candidate_count": len(candidates)},
                thought_process=f"Deterministically selecting the product with the {metric_desc[0]} from {len(candidates)} candidates.",
            )
        )

        extreme_prod = get_extreme_product(candidates, metric=metric, direction=direction)
        if not extreme_prod:
            return ChatResponse(reply="No product found matching that criterion.", session_id=session_id, tools_used=tools_executed)

        if metric == "price" and direction == "min":
            reply = (
                f"Among the previously discussed products, the cheapest option is the **{extreme_prod.product_name}** "
                f"at **{config.currency_symbol}{extreme_prod.price:,.0f}** "
                f"(Customer Rating: {extreme_prod.rating}★ with {extreme_prod.review_count:,} reviews)."
            )
            score_breakdown = ScoreBreakdown(
                budget_fit_score=1.0,
                rating_score=round(extreme_prod.rating / 5.0, 4),
                feature_match_score=1.0,
                popularity_score=0.9,
                availability_score=1.0 if extreme_prod.availability else 0.0,
                final_score=1.0,
                explanation=f"Lowest price in candidate set at {config.currency_symbol}{extreme_prod.price:,.0f}.",
            )
        elif metric == "price" and direction == "max":
            reply = (
                f"Among the previously discussed products, the most expensive option is the **{extreme_prod.product_name}** "
                f"at **{config.currency_symbol}{extreme_prod.price:,.0f}** "
                f"(Customer Rating: {extreme_prod.rating}★ with {extreme_prod.review_count:,} reviews)."
            )
            score_breakdown = ScoreBreakdown(
                budget_fit_score=0.8,
                rating_score=round(extreme_prod.rating / 5.0, 4),
                feature_match_score=1.0,
                popularity_score=0.9,
                availability_score=1.0 if extreme_prod.availability else 0.0,
                final_score=1.0,
                explanation=f"Highest price in candidate set at {config.currency_symbol}{extreme_prod.price:,.0f}.",
            )
        elif metric == "rating" and direction == "max":
            reply = (
                f"Among the previously discussed products, the highest-rated option is the **{extreme_prod.product_name}** "
                f"with a customer rating of **{extreme_prod.rating}★** "
                f"({extreme_prod.review_count:,} reviews, priced at {config.currency_symbol}{extreme_prod.price:,.0f})."
            )
            score_breakdown = ScoreBreakdown(
                budget_fit_score=0.9,
                rating_score=1.0,
                feature_match_score=1.0,
                popularity_score=0.9,
                availability_score=1.0 if extreme_prod.availability else 0.0,
                final_score=1.0,
                explanation=f"Highest customer satisfaction in candidate set at {extreme_prod.rating}★.",
            )
        elif metric == "rating" and direction == "min":
            reply = (
                f"Among the previously discussed products, the lowest-rated option is the **{extreme_prod.product_name}** "
                f"with a customer rating of **{extreme_prod.rating}★** "
                f"({extreme_prod.review_count:,} reviews, priced at {config.currency_symbol}{extreme_prod.price:,.0f})."
            )
            score_breakdown = ScoreBreakdown(
                budget_fit_score=0.9,
                rating_score=round(extreme_prod.rating / 5.0, 4),
                feature_match_score=1.0,
                popularity_score=0.9,
                availability_score=1.0 if extreme_prod.availability else 0.0,
                final_score=1.0,
                explanation=f"Lowest customer rating in candidate set at {extreme_prod.rating}★.",
            )
        elif metric == "reviews" and direction == "min":
            reply = (
                f"Among the previously discussed products, the option with the fewest reviews is the **{extreme_prod.product_name}** "
                f"with **{extreme_prod.review_count:,} verified customer reviews** "
                f"(Rating: {extreme_prod.rating}★, priced at {config.currency_symbol}{extreme_prod.price:,.0f})."
            )
            score_breakdown = ScoreBreakdown(
                budget_fit_score=0.9,
                rating_score=round(extreme_prod.rating / 5.0, 4),
                feature_match_score=1.0,
                popularity_score=round(min(1.0, extreme_prod.review_count / 10000.0), 4),
                availability_score=1.0 if extreme_prod.availability else 0.0,
                final_score=1.0,
                explanation=f"Fewest reviews in candidate set with {extreme_prod.review_count:,} verified reviews.",
            )
        else:  # reviews max
            reply = (
                f"Among the previously discussed products, the option with the most reviews is the **{extreme_prod.product_name}** "
                f"with **{extreme_prod.review_count:,} verified customer reviews** "
                f"(Rating: {extreme_prod.rating}★, priced at {config.currency_symbol}{extreme_prod.price:,.0f})."
            )
            score_breakdown = ScoreBreakdown(
                budget_fit_score=0.9,
                rating_score=round(extreme_prod.rating / 5.0, 4),
                feature_match_score=1.0,
                popularity_score=1.0,
                availability_score=1.0 if extreme_prod.availability else 0.0,
                final_score=1.0,
                explanation=f"Highest review volume in candidate set with {extreme_prod.review_count:,} verified reviews.",
            )

        # Sort candidates according to the metric and direction
        if metric == "price":
            sorted_candidates = sorted(candidates, key=lambda p: float(p.price), reverse=(direction == "max"))
        elif metric == "rating":
            sorted_candidates = sorted(candidates, key=lambda p: float(p.rating), reverse=(direction == "max"))
        else:  # reviews
            sorted_candidates = sorted(candidates, key=lambda p: int(p.review_count), reverse=(direction == "max"))

        ranked = []
        for idx, p in enumerate(sorted_candidates, start=1):
            if idx == 1:
                ranked.append(RankedProduct(product=p, rank=1, scores=score_breakdown))
            else:
                s_other = ScoreBreakdown(
                    budget_fit_score=1.0 if metric == "price" else round(min(1.0, 70000.0 / p.price), 4),
                    rating_score=round(p.rating / 5.0, 4),
                    feature_match_score=0.9,
                    popularity_score=round(min(1.0, p.review_count / 10000.0), 4),
                    availability_score=1.0 if p.availability else 0.0,
                    final_score=round(max(0.1, 1.0 - (idx - 1) * 0.05), 4),
                    explanation=f"Rank #{idx} in candidate set ({config.currency_symbol}{p.price:,.0f}, {p.rating}★).",
                )
                ranked.append(RankedProduct(product=p, rank=idx, scores=s_other))

        return ChatResponse(
            reply=reply,
            session_id=session_id,
            tools_used=tools_executed,
            products=ranked,
        )

    def _handle_multi_criteria_extrema(
        self,
        user_text: str,
        session_id: str,
        tools_executed: List[AgentToolCall],
        candidates: List[Product],
        has_min_price: bool,
        has_max_rating: bool,
        has_max_reviews: bool,
        has_max_price: bool,
    ) -> ChatResponse:
        """Handles deterministic resolution of multiple distinct extrema (e.g. lowest price AND highest rating)."""
        criteria = []
        if has_min_price:
            criteria.append("lowest_price")
        if has_max_rating:
            criteria.append("highest_rating")
        if has_max_reviews:
            criteria.append("most_reviews")
        if has_max_price:
            criteria.append("most_expensive")

        tools_executed.append(
            AgentToolCall(
                tool_name="get_multi_criteria_extrema",
                parameters={"criteria": criteria, "candidate_count": len(candidates)},
                thought_process=f"Deterministically evaluating candidate set for distinct criteria: {criteria}.",
            )
        )

        extrema_results = get_multi_criteria_extrema(candidates, criteria)
        cheapest = extrema_results.get("cheapest")
        highest_rated = extrema_results.get("highest_rated")
        most_reviewed = extrema_results.get("most_reviewed")

        ranked = []
        reply_lines = []

        if cheapest and highest_rated and cheapest.product_id == highest_rated.product_id:
            reply_lines.append(
                f"The **{cheapest.product_name}** uniquely satisfies both criteria: it offers the lowest price at "
                f"**{config.currency_symbol}{cheapest.price:,.0f}** and the highest customer rating at **{cheapest.rating}★** "
                f"({cheapest.review_count:,} reviews)."
            )
            ranked.append(RankedProduct(
                product=cheapest,
                rank=1,
                scores=ScoreBreakdown(
                    budget_fit_score=1.0,
                    rating_score=1.0,
                    feature_match_score=1.0,
                    popularity_score=0.9,
                    availability_score=1.0 if cheapest.availability else 0.0,
                    final_score=1.0,
                    explanation="Combines lowest price with highest rating.",
                )
            ))
        else:
            reply_lines.append("Among the previously discussed products, different options lead each criterion:")
            if cheapest:
                reply_lines.append(
                    f"- **Lowest Price (Cheapest):** {cheapest.product_name} at **{config.currency_symbol}{cheapest.price:,.0f}** ({cheapest.rating}★, {cheapest.review_count:,} reviews)"
                )
                ranked.append(RankedProduct(
                    product=cheapest,
                    rank=1,
                    scores=ScoreBreakdown(
                        budget_fit_score=1.0,
                        rating_score=round(cheapest.rating / 5.0, 4),
                        feature_match_score=0.9,
                        popularity_score=0.8,
                        availability_score=1.0 if cheapest.availability else 0.0,
                        final_score=0.95,
                        explanation=f"Lowest price in candidate set at {config.currency_symbol}{cheapest.price:,.0f}.",
                    )
                ))
            if highest_rated:
                reply_lines.append(
                    f"- **Highest Rating:** {highest_rated.product_name} at **{highest_rated.rating}★** ({config.currency_symbol}{highest_rated.price:,.0f}, {highest_rated.review_count:,} reviews)"
                )
                ranked.append(RankedProduct(
                    product=highest_rated,
                    rank=2,
                    scores=ScoreBreakdown(
                        budget_fit_score=0.85,
                        rating_score=1.0,
                        feature_match_score=1.0,
                        popularity_score=0.85,
                        availability_score=1.0 if highest_rated.availability else 0.0,
                        final_score=0.94,
                        explanation=f"Highest customer satisfaction in candidate set at {highest_rated.rating}★.",
                    )
                ))
            if most_reviewed and (not cheapest or most_reviewed.product_id != cheapest.product_id) and (not highest_rated or most_reviewed.product_id != highest_rated.product_id):
                reply_lines.append(
                    f"- **Most Reviews:** {most_reviewed.product_name} with **{most_reviewed.review_count:,} reviews** ({most_reviewed.rating}★, {config.currency_symbol}{most_reviewed.price:,.0f})"
                )

        return ChatResponse(
            reply="\n".join(reply_lines),
            session_id=session_id,
            tools_used=tools_executed,
            products=ranked,
        )

    def _handle_compare_extremes(
        self,
        user_text: str,
        session_id: str,
        tools_executed: List[AgentToolCall],
        candidates: List[Product],
    ) -> ChatResponse:
        """Deterministically extracts the cheapest and highest-rated products and feeds them into compare_products."""
        if not candidates or len(candidates) < 2:
            return ChatResponse(
                reply="Need at least 2 candidate products to generate an extreme comparison.",
                session_id=session_id,
                tools_used=tools_executed,
            )

        tools_executed.append(
            AgentToolCall(
                tool_name="get_extreme_product",
                parameters={"metric": "price", "direction": "min", "candidate_count": len(candidates)},
                thought_process="Deterministically finding the cheapest product among candidates.",
            )
        )
        cheapest = get_extreme_product(candidates, metric="price", direction="min")

        tools_executed.append(
            AgentToolCall(
                tool_name="get_extreme_product",
                parameters={"metric": "rating", "direction": "max", "candidate_count": len(candidates)},
                thought_process="Deterministically finding the highest-rated product among candidates.",
            )
        )
        highest_rated = get_extreme_product(candidates, metric="rating", direction="max")

        if not cheapest or not highest_rated:
            return ChatResponse(reply="Could not resolve extreme products for comparison.", session_id=session_id, tools_used=tools_executed)

        target_ids = [cheapest.product_id]
        if highest_rated.product_id != cheapest.product_id:
            target_ids.append(highest_rated.product_id)
        else:
            others = [p for p in candidates if p.product_id != cheapest.product_id]
            if others:
                target_ids.append(others[0].product_id)

        tools_executed.append(
            AgentToolCall(
                tool_name="compare_products",
                parameters={"product_ids": target_ids},
                thought_process=f"Generating side-by-side spec comparison between cheapest ({cheapest.product_id}) and highest-rated ({highest_rated.product_id}).",
            )
        )

        comp_data = compare_products(target_ids)
        trade_offs = comp_data.get("trade_off_summary", "")
        reply = (
            f"Here is the side-by-side comparison between the **Cheapest** ({cheapest.product_name} - {config.currency_symbol}{cheapest.price:,.0f}) "
            f"and the **Highest-Rated** ({highest_rated.product_name} - {highest_rated.rating}★):\n\n"
            f"{trade_offs}"
        )

        return ChatResponse(
            reply=reply,
            session_id=session_id,
            tools_used=tools_executed,
            comparison=comp_data,
        )

    def _handle_gaming(
        self,
        user_text: str,
        session_id: str,
        tools_executed: List[AgentToolCall],
        candidates: List[Product],
    ) -> ChatResponse:
        """Handles gaming-specific deterministic ranking based on GPU, refresh rate, and thermal performance."""
        tools_executed.append(
            AgentToolCall(
                tool_name="rank_for_gaming",
                parameters={"candidate_count": len(candidates), "top_n": 5},
                thought_process="Ranking candidate products based on dedicated GPU class, display refresh rate, high-TDP processor, and gaming thermal design.",
            )
        )
        ranked = rank_for_gaming(candidates, top_n=5)
        if not ranked:
            return ChatResponse(reply="No gaming-compatible products found.", session_id=session_id, tools_used=tools_executed)

        top = ranked[0].product
        top_scores = ranked[0].scores
        reply = (
            f"Among the candidate products, the **{top.product_name}** ({config.currency_symbol}{top.price:,.0f}, {top.rating}★) "
            f"is the best option for gaming. {top_scores.explanation}"
        )
        return ChatResponse(
            reply=reply,
            session_id=session_id,
            tools_used=tools_executed,
            products=ranked,
        )

    def _handle_value(
        self,
        user_text: str,
        session_id: str,
        tools_executed: List[AgentToolCall],
        candidates: List[Product],
    ) -> ChatResponse:
        """Handles value-for-money deterministic ranking balancing price efficiency with customer satisfaction."""
        tools_executed.append(
            AgentToolCall(
                tool_name="rank_for_value",
                parameters={"candidate_count": len(candidates), "top_n": 5},
                thought_process="Evaluating candidate products using multi-factor value-for-money scoring balancing price accessibility against customer ratings.",
            )
        )
        ranked = rank_for_value(candidates, top_n=5)
        if not ranked:
            return ChatResponse(reply="No products found to evaluate value.", session_id=session_id, tools_used=tools_executed)

        top = ranked[0].product
        top_scores = ranked[0].scores
        reply = (
            f"Among the candidate products, the **{top.product_name}** ({config.currency_symbol}{top.price:,.0f}, {top.rating}★) "
            f"offers the best value for money. {top_scores.explanation}"
        )
        return ChatResponse(
            reply=reply,
            session_id=session_id,
            tools_used=tools_executed,
            products=ranked,
        )

    def _handle_feature_followup(
        self,
        user_text: str,
        session_id: str,
        tools_executed: List[AgentToolCall],
        candidates: List[Product],
    ) -> ChatResponse:
        """Re-evaluates candidates on specific features like battery life, RAM, display, etc."""
        req = self.llm.extract_requirements(user_text)
        tools_executed.append(
            AgentToolCall(
                tool_name="rank_products",
                parameters={"context_products": len(candidates), "focus": user_text},
                thought_process=f"Re-evaluating previous {len(candidates)} candidates for follow-up criteria: '{user_text}'.",
            )
        )
        re_ranked = rank_products(candidates, req, top_n=len(candidates))
        top = re_ranked[0].product
        reply = (
            f"Among the products we previously discussed, the **{top.product_name}** ({config.currency_symbol}{top.price:,.0f}, {top.rating}★) "
            f"best matches your follow-up criteria. {re_ranked[0].scores.explanation}"
        )
        return ChatResponse(
            reply=reply,
            session_id=session_id,
            tools_used=tools_executed,
            products=re_ranked,
        )

    def _handle_recommendation(
        self,
        user_text: str,
        session_id: str,
        tools_executed: List[AgentToolCall],
    ) -> ChatResponse:
        """Executes full search -> rank -> grounded explanation workflow."""
        requirements = self.llm.extract_requirements(user_text)

        tools_executed.append(
            AgentToolCall(
                tool_name="search_products",
                parameters={
                    "category": requirements.category,
                    "min_price": requirements.min_price,
                    "max_price": requirements.max_price,
                    "brands": requirements.brand_preference,
                    "required_features": requirements.required_features,
                },
                thought_process=f"Searching catalog for category '{requirements.category}' under {requirements.max_price}.",
            )
        )
        candidates = search_products(
            category=requirements.category,
            min_price=requirements.min_price,
            max_price=requirements.max_price,
            brands=requirements.brand_preference,
            min_rating=requirements.min_rating,
            required_features=requirements.required_features,
            top_n=10,
        )

        if not candidates and requirements.required_features:
            candidates = search_products(
                category=requirements.category,
                min_price=requirements.min_price,
                max_price=requirements.max_price,
                brands=requirements.brand_preference,
                min_rating=requirements.min_rating,
                top_n=10,
            )

        tools_executed.append(
            AgentToolCall(
                tool_name="rank_products",
                parameters={"candidate_count": len(candidates), "top_n": 5},
                thought_process="Scoring and ranking candidates using multi-factor criteria.",
            )
        )
        ranked = rank_products(candidates, requirements, top_n=5)
        reply = self.llm.synthesize_response(user_text, ranked)

        try:
            db.log_interaction(
                session_id=session_id,
                user_query=user_text,
                extracted_category=requirements.category,
                extracted_budget_max=requirements.max_price,
                extracted_features=requirements.required_features,
                recommended_product_ids=[r.product.product_id for r in ranked],
            )
        except Exception:
            pass

        return ChatResponse(
            reply=reply,
            session_id=session_id,
            tools_used=tools_executed,
            products=ranked,
        )

    def _handle_comparison(
        self,
        user_text: str,
        session_id: str,
        tools_executed: List[AgentToolCall],
        previous_candidates: Optional[List[RankedProduct]] = None,
    ) -> ChatResponse:
        found_ids = re.findall(r"\b(?:LAP|PHN|AUD|WAT|ACC)\d{3}\b", user_text, re.IGNORECASE)
        found_ids = [fid.upper() for fid in found_ids]

        if not found_ids and previous_candidates and len(previous_candidates) >= 2:
            found_ids = [p.product.product_id for p in previous_candidates[:3]]

        if not found_ids:
            req = self.llm.extract_requirements(user_text)
            candidates = search_products(category=req.category, max_price=req.max_price, top_n=3)
            found_ids = [p.product_id for p in candidates[:2]]

        if not found_ids:
            return ChatResponse(
                reply="Please specify at least two products or search for items to compare.",
                session_id=session_id,
                tools_used=tools_executed,
            )

        tools_executed.append(
            AgentToolCall(
                tool_name="compare_products",
                parameters={"product_ids": found_ids},
                thought_process=f"Generating side-by-side comparison for: {found_ids}",
            )
        )
        comp_data = compare_products(found_ids)
        trade_offs = comp_data.get("trade_off_summary", "")
        reply = f"Here is the side-by-side comparison for **{', '.join(found_ids)}**:\n\n{trade_offs}"

        return ChatResponse(
            reply=reply,
            session_id=session_id,
            tools_used=tools_executed,
            comparison=comp_data,
        )

    def _handle_growth_insights(
        self, session_id: str, tools_executed: List[AgentToolCall]
    ) -> ChatResponse:
        tools_executed.append(
            AgentToolCall(
                tool_name="generate_growth_insight",
                parameters={"type": "general"},
                thought_process="Aggregating catalog demand distribution and customer preference trends.",
            )
        )
        insights = generate_growth_insight()
        reply = "Here are the latest **AI Commerce Growth Insights**:\n\n" + "\n\n".join(
            f"📈 **{ins.title}** ({ins.metric_value})\n{ins.description}\n*Recommendation:* {ins.actionable_recommendation}"
            for ins in insights
        )
        return ChatResponse(
            reply=reply,
            session_id=session_id,
            tools_used=tools_executed,
            insights=insights,
        )

    def _handle_product_details(
        self, user_text: str, session_id: str, tools_executed: List[AgentToolCall]
    ) -> Optional[ChatResponse]:
        found_ids = re.findall(r"\b(?:LAP|PHN|AUD|WAT|ACC)\d{3}\b", user_text, re.IGNORECASE)
        if not found_ids:
            return None

        target_id = found_ids[0].upper()
        tools_executed.append(
            AgentToolCall(
                tool_name="get_product_details",
                parameters={"product_id": target_id},
                thought_process=f"Retrieving full specifications for {target_id}",
            )
        )
        prod = get_product_details(target_id)
        if not prod:
            return None

        reply = (
            f"**{prod.product_name}** ({prod.brand})\n"
            f"- **Price:** {config.currency_symbol}{prod.price:,.0f}\n"
            f"- **Rating:** {prod.rating}★ ({prod.review_count:,} reviews)\n"
            f"- **Stock:** {'In Stock' if prod.availability else 'Out of Stock'}\n"
            f"- **Features:** {', '.join(prod.features)}\n"
            f"- **Overview:** {prod.description}"
        )
        return ChatResponse(
            reply=reply,
            session_id=session_id,
            tools_used=tools_executed,
        )


# Global agent instance
agent = ShopPilotAgent()

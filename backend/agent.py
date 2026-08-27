"""
ShopPilot AI - Autonomous Agent Orchestration Engine
Plans and sequences tool execution based on user intent, validates parameters,
and coordinates grounded response generation.
"""

import re
from typing import List, Dict, Any, Optional
from backend.schema import (
    ChatRequest,
    ChatResponse,
    AgentToolCall,
    ExtractedRequirement,
    RankedProduct,
    Product,
)
from backend.llm import llm_client, LLMClient
from backend.tools import (
    search_products,
    rank_products,
    get_product_details,
    compare_products,
    generate_growth_insight,
)
from backend.database import db


class ShopPilotAgent:
    """
    Autonomous AI Commerce Agent that understands goals, sequences tools,
    and returns grounded, explainable shopping recommendations.
    """

    def __init__(self, llm: Optional[LLMClient] = None):
        self.llm = llm or llm_client

    def process_message(self, request: ChatRequest, previous_candidates: Optional[List[RankedProduct]] = None) -> ChatResponse:
        """
        Main entry point for agentic goal planning, tool execution, and synthesis.
        """
        user_text = request.message.strip()
        session_id = request.session_id or "default_session"
        tools_executed: List[AgentToolCall] = []

        q_lower = user_text.lower()

        # Branch 1: Comparison Intent (e.g. "compare LAP001 and LAP004" or "compare MacBook and ThinkPad")
        if "compare" in q_lower or "vs" in q_lower or "versus" in q_lower:
            return self._handle_comparison(user_text, session_id, tools_executed, previous_candidates)

        # Branch 2: Growth Analytics Intent (e.g. "show growth insights", "trends")
        if any(w in q_lower for w in ["growth insight", "analytics", "trend", "demand gap"]):
            return self._handle_growth_insights(session_id, tools_executed)

        # Branch 3: Specific Product Detail Intent (e.g. "details for LAP001", "tell me about iPhone 15")
        if "detail" in q_lower or "spec" in q_lower:
            detail_res = self._handle_product_details(user_text, session_id, tools_executed)
            if detail_res:
                return detail_res

        # Branch 4: Primary Shopping Discovery & Recommendation Flow
        return self._handle_recommendation(user_text, session_id, tools_executed, previous_candidates)

    def _handle_recommendation(
        self,
        user_text: str,
        session_id: str,
        tools_executed: List[AgentToolCall],
        previous_candidates: Optional[List[RankedProduct]] = None,
    ) -> ChatResponse:
        """Executes full search -> rank -> grounded explanation workflow."""
        # 1. Requirement Extraction
        requirements = self.llm.extract_requirements(user_text)

        # 2. Tool Call: search_products
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
                thought_process=f"Extracted intent for category '{requirements.category}' and max budget {requirements.max_price}.",
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

        # Fallback search if empty (relax features first)
        if not candidates and requirements.required_features:
            candidates = search_products(
                category=requirements.category,
                min_price=requirements.min_price,
                max_price=requirements.max_price,
                brands=requirements.brand_preference,
                min_rating=requirements.min_rating,
                top_n=10,
            )

        # 3. Tool Call: rank_products
        tools_executed.append(
            AgentToolCall(
                tool_name="rank_products",
                parameters={"candidate_count": len(candidates), "top_n": 5},
                thought_process="Scoring candidates using multi-factor budget, rating, and feature overlap models.",
            )
        )
        ranked = rank_products(candidates, requirements, top_n=5)

        # 4. Grounded Synthesis
        reply = self.llm.synthesize_response(user_text, ranked)

        # 5. Log interaction to SQLite
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
        """Handles comparison requests between specific products or previous candidates."""
        # Find product IDs in text (e.g. LAP001, PHN002)
        found_ids = re.findall(r"\b(?:LAP|PHN|AUD|WAT|ACC)\d{3}\b", user_text, re.IGNORECASE)
        found_ids = [fid.upper() for fid in found_ids]

        # If no explicit IDs, use previous candidates from session memory
        if not found_ids and previous_candidates and len(previous_candidates) >= 2:
            found_ids = [p.product.product_id for p in previous_candidates[:3]]

        # If still no IDs, perform search and compare top 2
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
                thought_process=f"Extracting side-by-side comparison matrix for products: {found_ids}",
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
        """Handles business growth and commerce intelligence queries."""
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
        """Fetches and displays detailed specs for a specific product ID."""
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

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
        last_candidates = previous_candidates or context.get("last_candidates", [])
        last_req = context.get("last_requirement")

        q_lower = user_text.lower()

        # Branch 1: Follow-up question on previous candidates (e.g. "which of these has the best battery?", "what about RAM?")
        is_followup = bool(
            last_candidates
            and any(
                w in q_lower
                for w in ["which one", "which of these", "best battery", "more ram", "cheaper", "first one", "second one"]
            )
        )
        if is_followup:
            res = self._handle_followup(user_text, session_id, tools_executed, last_candidates)
            self.memory.record_turn(session_id, user_text, res.reply, last_req, res.products or last_candidates)
            return res

        # Branch 2: Comparison Intent (e.g. "compare LAP001 and LAP004" or "compare them")
        if "compare" in q_lower or "vs" in q_lower or "versus" in q_lower:
            res = self._handle_comparison(user_text, session_id, tools_executed, last_candidates)
            self.memory.record_turn(session_id, user_text, res.reply, last_req, last_candidates)
            return res

        # Branch 3: Growth Analytics Intent
        if any(w in q_lower for w in ["growth insight", "analytics", "trend", "demand gap"]):
            res = self._handle_growth_insights(session_id, tools_executed)
            self.memory.record_turn(session_id, user_text, res.reply, last_req, last_candidates)
            return res

        # Branch 4: Specific Product Detail Intent
        if "detail" in q_lower or "spec" in q_lower:
            detail_res = self._handle_product_details(user_text, session_id, tools_executed)
            if detail_res:
                self.memory.record_turn(session_id, user_text, detail_res.reply, last_req, last_candidates)
                return detail_res

        # Branch 5: Primary Shopping Discovery & Recommendation Flow
        res = self._handle_recommendation(user_text, session_id, tools_executed)
        req = self.llm.extract_requirements(user_text)
        self.memory.record_turn(session_id, user_text, res.reply, req, res.products)
        return res

    def _handle_followup(
        self,
        user_text: str,
        session_id: str,
        tools_executed: List[AgentToolCall],
        previous_candidates: List[RankedProduct],
    ) -> ChatResponse:
        """Resolves contextual follow-up query against previous candidate set."""
        tools_executed.append(
            AgentToolCall(
                tool_name="rank_products",
                parameters={"context_products": len(previous_candidates), "focus": user_text},
                thought_process=f"Re-evaluating previous {len(previous_candidates)} candidates for follow-up criteria: '{user_text}'.",
            )
        )
        prods = [rp.product for rp in previous_candidates]
        req = self.llm.extract_requirements(user_text)
        
        # If user asked about battery or specific feature, ensure feature match is prioritized
        re_ranked = rank_products(prods, req, top_n=len(prods))

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

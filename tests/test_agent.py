"""
ShopPilot AI - Agent & Tool Calling Test Suite
"""

import pytest
from backend.schema import ChatRequest
from backend.agent import ShopPilotAgent
from backend.tools import (
    search_products,
    rank_products,
    get_product_details,
    compare_products,
    generate_growth_insight,
)


@pytest.fixture
def agent_instance():
    return ShopPilotAgent()


def test_agent_tools_search_and_rank():
    """Verify tool functions return typed results."""
    prods = search_products(category="Laptop", max_price=75000.0)
    assert len(prods) > 0
    ranked = rank_products(prods)
    assert len(ranked) > 0
    assert ranked[0].scores.final_score > 0


def test_agent_tools_compare():
    """Verify comparison matrix generation."""
    comp = compare_products(["LAP001", "LAP004"])
    assert comp["products_count"] == 2
    assert "comparison_matrix" in comp
    assert len(comp["comparison_matrix"]) == 2
    assert "trade_off_summary" in comp


def test_agent_tools_details():
    """Verify single product spec lookup."""
    prod = get_product_details("LAP001")
    assert prod is not None
    assert prod.product_id == "LAP001"
    assert prod.category == "Laptop"


def test_agent_process_shopping_message(agent_instance):
    """Verify full agentic routing for shopping discovery."""
    req = ChatRequest(message="I need a laptop under ₹70,000 for programming")
    res = agent_instance.process_message(req)

    assert len(res.tools_used) >= 2
    tool_names = [t.tool_name for t in res.tools_used]
    assert "search_products" in tool_names
    assert "rank_products" in tool_names
    assert len(res.products) > 0
    assert len(res.reply) > 0


def test_agent_process_comparison_message(agent_instance):
    """Verify agentic routing for comparison intent."""
    req = ChatRequest(message="Compare LAP001 and LAP004")
    res = agent_instance.process_message(req)

    tool_names = [t.tool_name for t in res.tools_used]
    assert "compare_products" in tool_names
    assert res.comparison is not None


def test_agent_process_growth_insight_message(agent_instance):
    """Verify agentic routing for growth insights."""
    req = ChatRequest(message="Show me growth insights and trends")
    res = agent_instance.process_message(req)

    tool_names = [t.tool_name for t in res.tools_used]
    assert "generate_growth_insight" in tool_names
    assert res.insights is not None
    assert len(res.insights) > 0

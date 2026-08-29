"""
ShopPilot AI - Agent & Tool Calling Test Suite
"""

import pytest
from backend.schema import ChatRequest
from backend.agent import ShopPilotAgent
from backend.tools import (
    search_products,
    filter_products,
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


def test_agent_tools_filter():
    """Verify filter_products tool function isolates items from a candidate list."""
    prods = search_products(category="Laptop", max_price=100000.0)
    filtered = filter_products(prods, max_price=65000.0, min_rating=4.3)
    assert len(filtered) > 0
    for p in filtered:
        assert p.price <= 65000.0
        assert p.rating >= 4.3


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


def test_followup_cheapest_extrema(agent_instance):
    """Verify follow-up query 'Which one is cheapest?' deterministically selects minimum price."""
    session_id = "test_sess_cheapest"
    # Turn 1: Initial query
    t1 = ChatRequest(message="Show me laptops under ₹70,000 with 16GB RAM", session_id=session_id)
    r1 = agent_instance.process_message(t1)
    assert len(r1.products) >= 3

    # Turn 2: Follow-up cheapest
    t2 = ChatRequest(message="Which one is the cheapest?", session_id=session_id)
    r2 = agent_instance.process_message(t2)

    tool_names = [t.tool_name for t in r2.tools_used]
    assert "get_extreme_product" in tool_names
    assert r2.tools_used[0].parameters["metric"] == "price"
    assert r2.tools_used[0].parameters["direction"] == "min"
    # Verify lowest price laptop in candidate set is selected
    assert r2.products[0].product.product_id == "LAP007"  # Dell Inspiron 15 (₹53,490)
    assert r2.products[0].product.price == 53490.0
    assert "53,490" in r2.reply or "Dell" in r2.reply


def test_followup_most_expensive_extrema(agent_instance):
    """Verify follow-up query 'Which one is the most expensive?' deterministically selects maximum price."""
    session_id = "test_sess_expensive"
    t1 = ChatRequest(message="Show me laptops under ₹70,000 with 16GB RAM", session_id=session_id)
    agent_instance.process_message(t1)

    t2 = ChatRequest(message="Which one is the most expensive?", session_id=session_id)
    r2 = agent_instance.process_message(t2)

    tool_names = [t.tool_name for t in r2.tools_used]
    assert "get_extreme_product" in tool_names
    assert r2.tools_used[0].parameters["metric"] == "price"
    assert r2.tools_used[0].parameters["direction"] == "max"
    assert r2.products[0].product.product_id == "LAP006"  # Acer Nitro V Gaming (₹68,990)
    assert r2.products[0].product.price == 68990.0


def test_followup_highest_rating_extrema(agent_instance):
    """Verify follow-up query 'Which has the highest rating?' deterministically selects maximum rating."""
    session_id = "test_sess_rating"
    t1 = ChatRequest(message="Show me laptops under ₹70,000 with 16GB RAM", session_id=session_id)
    agent_instance.process_message(t1)

    t2 = ChatRequest(message="Which one has the highest rating?", session_id=session_id)
    r2 = agent_instance.process_message(t2)

    tool_names = [t.tool_name for t in r2.tools_used]
    assert "get_extreme_product" in tool_names
    assert r2.tools_used[0].parameters["metric"] == "rating"
    assert r2.tools_used[0].parameters["direction"] == "max"
    assert r2.products[0].product.product_id == "LAP004"  # Lenovo ThinkPad E14 (4.4★)
    assert r2.products[0].product.rating == 4.4


def test_followup_most_reviews_extrema(agent_instance):
    """Verify follow-up query 'Which has the most reviews?' deterministically selects maximum review_count."""
    session_id = "test_sess_reviews"
    t1 = ChatRequest(message="Show me laptops under ₹70,000 with 16GB RAM", session_id=session_id)
    agent_instance.process_message(t1)

    t2 = ChatRequest(message="Which one has the most reviews?", session_id=session_id)
    r2 = agent_instance.process_message(t2)

    tool_names = [t.tool_name for t in r2.tools_used]
    assert "get_extreme_product" in tool_names
    assert r2.tools_used[0].parameters["metric"] == "reviews"
    assert r2.tools_used[0].parameters["direction"] == "max"
    assert r2.products[0].product.product_id == "LAP008"  # Lenovo IdeaPad Gaming 3 (3,200 reviews)
    assert r2.products[0].product.review_count == 3200


def test_followup_multi_criteria_extrema(agent_instance):
    """Verify multi-criteria query 'lowest price and highest rating' reports both criteria winners."""
    session_id = "test_sess_multi"
    t1 = ChatRequest(message="Show me laptops under ₹70,000 with 16GB RAM", session_id=session_id)
    agent_instance.process_message(t1)

    t2 = ChatRequest(message="Which one has the lowest price and highest rating?", session_id=session_id)
    r2 = agent_instance.process_message(t2)

    tool_names = [t.tool_name for t in r2.tools_used]
    assert "get_multi_criteria_extrema" in tool_names
    assert "Dell" in r2.reply or "LAP007" in r2.reply
    assert "Lenovo ThinkPad" in r2.reply or "LAP004" in r2.reply


def test_followup_compare_extremes(agent_instance):
    """Verify 'Compare the cheapest and the highest-rated laptop' resolves extrema and passes them to compare_products."""
    session_id = "test_sess_comp_ext"
    t1 = ChatRequest(message="Show me laptops under ₹70,000 with 16GB RAM", session_id=session_id)
    agent_instance.process_message(t1)

    t2 = ChatRequest(message="Compare the cheapest and the highest-rated laptop", session_id=session_id)
    r2 = agent_instance.process_message(t2)

    tool_names = [t.tool_name for t in r2.tools_used]
    assert "get_extreme_product" in tool_names
    assert "compare_products" in tool_names
    assert r2.comparison is not None
    comp_ids = [m["product_id"] for m in r2.comparison["comparison_matrix"]]
    assert "LAP007" in comp_ids  # Dell (Cheapest)
    assert "LAP004" in comp_ids  # Lenovo ThinkPad (Highest-rated)


def test_followup_best_for_gaming(agent_instance):
    """Verify 'Which one is the best for gaming?' uses gaming ranking considering GPU and refresh rate."""
    session_id = "test_sess_gaming"
    t1 = ChatRequest(message="Show me laptops under ₹70,000 with 16GB RAM", session_id=session_id)
    agent_instance.process_message(t1)

    t2 = ChatRequest(message="Which one is the best for gaming?", session_id=session_id)
    r2 = agent_instance.process_message(t2)

    tool_names = [t.tool_name for t in r2.tools_used]
    assert "rank_for_gaming" in tool_names
    # Top pick must have dedicated gaming GPU (Acer Nitro V RTX 4050 or Lenovo IdeaPad RTX 3050)
    top_prod = r2.products[0].product
    assert top_prod.product_id in ["LAP006", "LAP008"]
    assert "gaming" in r2.products[0].scores.explanation.lower() or "rtx" in r2.products[0].scores.explanation.lower()


def test_followup_best_value_for_money(agent_instance):
    """Verify 'Which one is the best value for money?' uses value ranking logic."""
    session_id = "test_sess_val"
    t1 = ChatRequest(message="Show me laptops under ₹70,000 with 16GB RAM", session_id=session_id)
    agent_instance.process_message(t1)

    t2 = ChatRequest(message="Which one is the best value for money?", session_id=session_id)
    r2 = agent_instance.process_message(t2)

    tool_names = [t.tool_name for t in r2.tools_used]
    assert "rank_for_value" in tool_names
    assert len(r2.products) > 0
    assert "value" in r2.products[0].scores.explanation.lower()


def test_memory_preserves_previous_candidate_set(agent_instance):
    """Verify consecutive follow-ups stay locked to the same candidate set without re-searching."""
    session_id = "test_sess_preserve"
    t1 = ChatRequest(message="Show me laptops under ₹70,000 with 16GB RAM", session_id=session_id)
    r1 = agent_instance.process_message(t1)
    original_ids = {p.product.product_id for p in r1.products}

    # Follow-up 1
    t2 = ChatRequest(message="Which one is the cheapest?", session_id=session_id)
    r2 = agent_instance.process_message(t2)
    assert r2.products[0].product.product_id in original_ids

    # Follow-up 2
    t3 = ChatRequest(message="Which one has the highest rating?", session_id=session_id)
    r3 = agent_instance.process_message(t3)
    assert r3.products[0].product.product_id in original_ids

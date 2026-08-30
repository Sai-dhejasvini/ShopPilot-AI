from backend.schema import ChatRequest
from backend.agent import ShopPilotAgent
import pytest

@pytest.fixture
def agent_instance():
    return ShopPilotAgent()

def test_cheapest_smartphone_extrema(agent_instance):
    """Verify 'show me the cheapest smartphone' evaluates all smartphones and returns the cheapest."""
    req = ChatRequest(message="show me the cheapest smartphone", session_id="test_sess_smartphone")
    res = agent_instance.process_message(req)
    tool_names = [t.tool_name for t in res.tools_used]
    assert "get_extreme_product" in tool_names
    assert res.products[0].product.category == "Smartphone"
    assert res.products[0].product.product_id == "PHN015"
    assert res.products[0].product.price == 16499.0

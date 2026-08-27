"""
ShopPilot AI - Conversational Session Memory Test Suite
"""

import pytest
from backend.schema import ChatRequest
from backend.memory import SessionMemoryManager
from backend.agent import ShopPilotAgent


def test_session_memory_recording():
    """Verify storing turns and retrieving context."""
    mem = SessionMemoryManager()
    session_id = "test_session_1"

    mem.record_turn(session_id, "Find laptops", "Here are 3 laptops", candidates=[])
    ctx = mem.get_context(session_id)

    assert ctx["session_id"] == session_id
    assert ctx["turns_count"] == 1


def test_agent_multi_turn_followup():
    """Verify follow-up queries resolve against previous candidates."""
    agent = ShopPilotAgent()
    session_id = "test_multi_turn"

    # Turn 1: Initial search
    req1 = ChatRequest(message="Show me laptops under 70k", session_id=session_id)
    res1 = agent.process_message(req1)
    assert len(res1.products) > 0

    # Turn 2: Follow-up question ("which of these has the best battery?")
    req2 = ChatRequest(message="Which of these has the best battery life?", session_id=session_id)
    res2 = agent.process_message(req2)

    assert "previously discussed" in res2.reply or "Rank #" in res2.reply or len(res2.products) > 0
    assert len(res2.tools_used) > 0

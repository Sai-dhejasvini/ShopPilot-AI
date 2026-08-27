"""
ShopPilot AI - Conversational Session Memory
Maintains session-based dialogue state and tracks candidate product sets
across conversation turns for context-aware follow-up queries.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import time
from backend.schema import RankedProduct, ExtractedRequirement


@dataclass
class ConversationTurn:
    user_message: str
    agent_reply: str
    timestamp: float = field(default_factory=time.time)
    extracted_requirement: Optional[ExtractedRequirement] = None
    candidate_products: List[RankedProduct] = field(default_factory=list)


@dataclass
class SessionState:
    session_id: str
    turns: List[ConversationTurn] = field(default_factory=list)
    last_active: float = field(default_factory=time.time)

    def add_turn(
        self,
        user_msg: str,
        agent_reply: str,
        requirements: Optional[ExtractedRequirement] = None,
        candidates: Optional[List[RankedProduct]] = None,
    ):
        self.turns.append(
            ConversationTurn(
                user_message=user_msg,
                agent_reply=agent_reply,
                extracted_requirement=requirements,
                candidate_products=candidates or [],
            )
        )
        self.last_active = time.time()

    def get_last_candidates(self) -> List[RankedProduct]:
        """Returns the most recent candidate products from the last turn."""
        for turn in reversed(self.turns):
            if turn.candidate_products:
                return turn.candidate_products
        return []

    def get_last_requirement(self) -> Optional[ExtractedRequirement]:
        """Returns the most recent requirement schema."""
        for turn in reversed(self.turns):
            if turn.extracted_requirement:
                return turn.extracted_requirement
        return None


class SessionMemoryManager:
    """
    In-memory session manager for multi-turn shopping context.
    No personally identifiable information is stored.
    """

    def __init__(self, ttl_seconds: int = 3600):
        self._sessions: Dict[str, SessionState] = {}
        self.ttl_seconds = ttl_seconds

    def get_or_create_session(self, session_id: str) -> SessionState:
        self._cleanup_expired()
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionState(session_id=session_id)
        return self._sessions[session_id]

    def record_turn(
        self,
        session_id: str,
        user_msg: str,
        agent_reply: str,
        requirements: Optional[ExtractedRequirement] = None,
        candidates: Optional[List[RankedProduct]] = None,
    ):
        session = self.get_or_create_session(session_id)
        session.add_turn(user_msg, agent_reply, requirements, candidates)

    def get_context(self, session_id: str) -> Dict[str, Any]:
        session = self.get_or_create_session(session_id)
        return {
            "session_id": session_id,
            "turns_count": len(session.turns),
            "last_candidates": session.get_last_candidates(),
            "last_requirement": session.get_last_requirement(),
        }

    def clear_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]

    def _cleanup_expired(self):
        now = time.time()
        expired = [
            sid for sid, s in self._sessions.items()
            if now - s.last_active > self.ttl_seconds
        ]
        for sid in expired:
            del self._sessions[sid]


# Global session memory manager
memory_manager = SessionMemoryManager()

"""LangGraph state definition for the debate workflow."""

from typing import TypedDict, Annotated, List, Optional
import operator


class AgentOutput(TypedDict):
    """Output from a single agent's speech in the debate."""
    role: str  # "pro" | "con" | "teacher"
    content: str
    round_num: int
    tools_used: List[str]


class RoundEvalEntry(TypedDict):
    """Per-round evaluation scores for both sides."""
    round: int
    pro_scores: dict
    con_scores: dict


class DebateState(TypedDict):
    """Shared state for the entire debate workflow."""
    topic: str
    max_rounds: int
    current_round: int
    conversation_history: Annotated[List[AgentOutput], operator.add]
    round_scores: List[RoundEvalEntry]
    scores: Optional[dict]
    winner: Optional[str]
    teacher_summary: Optional[str]

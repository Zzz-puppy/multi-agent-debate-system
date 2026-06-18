"""Short-term memory using LangGraph State management."""

from typing import List, Optional
from graph.state import AgentOutput


class ShortTermMemory:
    """Maintains the current debate session's conversation history."""

    def __init__(self):
        self._messages: List[AgentOutput] = []
        self._tool_cache: dict = {}

    def add_message(self, message: AgentOutput) -> None:
        self._messages.append(message)

    def get_history(self, max_messages: Optional[int] = None) -> List[AgentOutput]:
        if max_messages:
            return self._messages[-max_messages:]
        return self._messages

    def get_round_messages(self, round_num: int) -> List[AgentOutput]:
        return [m for m in self._messages if m["round_num"] == round_num]

    def cache_tool_result(self, tool_name: str, result: str) -> None:
        self._tool_cache[tool_name] = result

    def get_tool_result(self, tool_name: str) -> Optional[str]:
        return self._tool_cache.get(tool_name)

    def clear(self) -> None:
        self._messages.clear()
        self._tool_cache.clear()

    def get_latest_opponent_message(self, my_role: str) -> Optional[AgentOutput]:
        for msg in reversed(self._messages):
            if msg["role"] != my_role:
                return msg
        return None

    def get_latest_teacher_feedback(self) -> str:
        for msg in reversed(self._messages):
            if msg["role"] == "teacher":
                return msg["content"]
        return ""

    @property
    def all_messages(self) -> List[AgentOutput]:
        return self._messages

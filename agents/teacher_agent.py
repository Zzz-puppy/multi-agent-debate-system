"""Teacher agent — hosts, evaluates, and summarizes the debate."""

from graph.state import AgentOutput
from memory.short_term import ShortTermMemory
from memory.long_term_rag import LongTermRAGMemory
from tools.argument_evaluator import ArgumentEvaluatorTool
from agents.prompts import TEACHER_SYSTEM_PROMPT
from utils.llm_manager import get_llm


class TeacherAgent:
    """Teacher agent for debate moderation and evaluation."""

    def __init__(self, llm=None, evaluator=None, long_term=None):
        self.llm = llm or get_llm(temperature=0.3)
        self.evaluator = evaluator or ArgumentEvaluatorTool()
        self.long_term = long_term or LongTermRAGMemory()

    def opening_speech(self, topic: str, max_rounds: int) -> AgentOutput:
        prompt = (
            f"{TEACHER_SYSTEM_PROMPT}\n\n"
            f"请为辩题「{topic}」作简短开场致辞（200字左右），介绍辩论规则（共{max_rounds}轮），"
            f"强调评分标准（逻辑性、论据质量、反驳能力、语言表达），"
            f"然后宣布辩论正式开始。"
        )
        response = self.llm.invoke(prompt)
        return AgentOutput(
            role="teacher", content=response.content.strip(),
            round_num=0, tools_used=[],
        )

    def evaluate_round(
        self, round_num: int, pro_speech: str, con_speech: str,
        short_term: ShortTermMemory, is_last_round: bool = False,
    ) -> tuple[AgentOutput, dict, dict]:
        pro_eval = self.evaluator.evaluate(pro_speech)
        con_eval = self.evaluator.evaluate(con_speech)

        round_hint = ""
        if is_last_round:
            round_hint = "这是最后一轮，直接点评总结本轮表现即可。"
        else:
            round_hint = "请给出简短改进建议供下一轮参考。"

        prompt = (
            f"{TEACHER_SYSTEM_PROMPT}\n\n"
            f"第{round_num}轮辩论结束。\n"
            f"正方发言: {pro_speech}\n"
            f"反方发言: {con_speech}\n\n"
            f"请用200字以内点评双方本轮表现，指出亮点和不足。{round_hint}"
        )
        response = self.llm.invoke(prompt)

        output = AgentOutput(
            role="teacher",
            content=response.content.strip(),
            round_num=round_num,
            tools_used=["argument_evaluator"],
        )
        return output, pro_eval, con_eval

    def summarize_debate(
        self, topic: str, max_rounds: int, history: list,
        pro_score: int, con_score: int, winner: str,
    ) -> str:
        history_text = "\n".join(
            f"[{m['role']}] 第{m['round_num']}轮: {m['content'][:80]}..."
            for m in history
        )
        winner_text = {"pro": "正方", "con": "反方", "平局": "平局"}.get(winner, winner)
        prompt = (
            f"{TEACHER_SYSTEM_PROMPT}\n\n"
            f"辩论已结束。\n"
            f"辩题: {topic}\n"
            f"共{max_rounds}轮\n"
            f"最终比分: 正方 {pro_score} 分, 反方 {con_score} 分\n"
            f"获胜方: {winner_text}\n\n"
            f"辩论过程摘要:\n{history_text}\n\n"
            f"请写一段200字以内的总结，点评双方整体表现，"
            f"给出改进建议。不需要再给出评分。"
        )
        response = self.llm.invoke(prompt)
        return response.content.strip()

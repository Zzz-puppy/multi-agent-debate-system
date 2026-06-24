"""Teacher agent — hosts, evaluates, and summarizes the debate."""
from graph.state import AgentOutput
from memory.short_term import ShortTermMemory
from memory.long_term_rag import LongTermRAGMemory
from tools.argument_evaluator import ArgumentEvaluatorTool
from agents.prompts import TEACHER_SYSTEM_PROMPT
from utils.llm_manager import get_llm


class TeacherAgent:
    def __init__(self, llm=None, evaluator=None, long_term=None):
        self.llm = llm or get_llm(temperature=0.3)
        self.evaluator = evaluator or ArgumentEvaluatorTool()
        self.long_term = long_term or LongTermRAGMemory()

    def opening_speech(self, topic: str, max_rounds: int) -> AgentOutput:
        return AgentOutput(role="teacher",
            content=self.llm.invoke(f"{TEACHER_SYSTEM_PROMPT}\n\n请为辩题「{topic}」作简短开场致辞（200字左右），介绍辩论规则（共{max_rounds}轮），强调评分标准，宣布辩论正式开始。").content.strip(),
            round_num=0, tools_used=[])

    def evaluate_round(self, round_num: int, pro_speech: str, con_speech: str, short_term: ShortTermMemory, is_last_round: bool = False) -> tuple[AgentOutput, dict, dict]:
        pro_eval = self.evaluator.evaluate(pro_speech)
        con_eval = self.evaluator.evaluate(con_speech)
        hint = "这是最后一轮，直接点评总结。" if is_last_round else "请给出简短改进建议。"
        prompt = f"{TEACHER_SYSTEM_PROMPT}\n\n第{round_num}轮辩论结束。\n正方发言: {pro_speech}\n反方发言: {con_speech}\n\n请用200字以内点评双方本轮表现，指出亮点和不足。{hint}"
        return AgentOutput(role="teacher", content=self.llm.invoke(prompt).content.strip(), round_num=round_num, tools_used=["argument_evaluator"]), pro_eval, con_eval

    def summarize_debate(self, topic: str, max_rounds: int, history: list, pro_score: int, con_score: int, winner: str) -> str:
        winner_text = {"pro": "正方", "con": "反方", "平局": "平局"}.get(winner, winner)
        history_text = "\n".join(f"[{m['role']}] 第{m['round_num']}轮: {m['content'][:80]}..." for m in history)
        prompt = f"{TEACHER_SYSTEM_PROMPT}\n\n辩论已结束。辩题: {topic} 共{max_rounds}轮 最终比分: 正方{pro_score}分, 反方{con_score}分 获胜方: {winner_text}\n\n辩论过程摘要:\n{history_text}\n\n请写一段200字以内的总结，点评双方整体表现，给出改进建议。不需要再给出评分。"
        return self.llm.invoke(prompt).content.strip()

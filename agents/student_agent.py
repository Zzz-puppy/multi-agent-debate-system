"""Student agent for debate — pro or con side."""

from graph.state import AgentOutput
from memory.short_term import ShortTermMemory
from memory.personal_profile import PersonalProfile
from memory.long_term_rag import LongTermRAGMemory
from tools.web_search import WebSearchTool
from tools.strategy_recommender import StrategyRecommenderTool
from utils.llm_manager import get_llm
from agents.prompts import PRO_SYSTEM_PROMPT, CON_SYSTEM_PROMPT, PREPARE_PROMPT


class StudentAgent:
    """Debate student agent with ReAct+Review loop and preparation phase."""

    def __init__(self, role: str, llm=None, profile=None,
                 web_search=None, rag_retrieval=None, strategy=None):
        self.role = role
        self.llm = llm or get_llm(temperature=0.7)
        self.profile = profile or PersonalProfile(role)
        self.web_search = web_search or WebSearchTool()
        self.long_term_memory = rag_retrieval or LongTermRAGMemory()
        self.strategy = strategy or StrategyRecommenderTool()
        self.system_prompt = PRO_SYSTEM_PROMPT if role == "pro" else CON_SYSTEM_PROMPT

    def prepare(self, topic: str) -> str:
        search_results = self.web_search.search_web(topic, num_results=5)
        historical = self.long_term_memory.search_similar(topic, n_results=3)
        recommended_strategy = self.strategy.recommend(self.role)
        strategy_advice = self.profile.get_strategy_advice()

        prep_prompt = (
            f"{self.system_prompt}\n\n"
            f"你正在为辩论做准备。辩题: {topic}\n\n"
            f"搜索到的资料:\n{search_results}\n\n"
            f"历史相关辩论:\n{historical}\n\n"
            f"推荐策略:\n{recommended_strategy}\n\n"
            f"个人经验:\n{strategy_advice}\n\n"
            f"{PREPARE_PROMPT}"
        )
        response = self.llm.invoke(prep_prompt)
        return response.content.strip()

    def speak(self, round_num: int, short_term: ShortTermMemory, topic: str) -> AgentOutput:
        opponent_msg = short_term.get_latest_opponent_message(self.role)
        opponent_content = opponent_msg["content"] if opponent_msg else "暂无"
        teacher_feedback = short_term.get_latest_teacher_feedback()
        strategy_advice = self.profile.get_strategy_advice()

        teacher_advice_section = ""
        if round_num > 1 and teacher_feedback:
            teacher_advice_section = f"教师上轮点评与建议: {teacher_feedback}\n"

        search_results = self.web_search.search_web(topic, num_results=3)
        historical = self.long_term_memory.search_similar(topic, n_results=2)
        recommended_strategy = self.strategy.recommend(self.role)

        combined_prompt = (
            f"{self.system_prompt}\n\n"
            f"辩题: {topic}\n"
            f"第{round_num}轮\n"
            f"对方上一轮发言: {opponent_content}\n"
            f"{teacher_advice_section}"
            f"个人经验: {strategy_advice}\n\n"
            f"搜索到的参考资料:\n{search_results}\n\n"
            f"历史辩论经验:\n{historical}\n\n"
            f"推荐策略:\n{recommended_strategy}\n\n"
            f"内部流程（自行完成，不要输出）：\n"
            f"1. 思考：基于以上资料，确定本轮核心论点\n"
            f"2. 自查：检查论据可靠性、相关性、逻辑自洽性\n"
            f"3. 如果自查发现问题，自行修正后再输出\n\n"
            f"请直接给出你的正式发言（200字以内，条理清晰）:"
        )
        answer = self.llm.invoke(combined_prompt)
        tools_used = ["web_search", "rag_retrieval", "strategy_recommender"]

        return AgentOutput(
            role=self.role,
            content=answer.content.strip(),
            round_num=round_num,
            tools_used=tools_used,
        )

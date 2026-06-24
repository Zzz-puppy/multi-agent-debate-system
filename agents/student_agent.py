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
    def __init__(self, role: str, llm=None, profile=None, web_search=None, rag_retrieval=None, strategy=None):
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
        prep_prompt = f"{self.system_prompt}\n\n你正在为辩论做准备。辩题: {topic}\n\n搜索到的资料:\n{search_results}\n\n历史相关辩论:\n{historical}\n\n推荐策略:\n{recommended_strategy}\n\n{PREPARE_PROMPT}"
        return self.llm.invoke(prep_prompt).content.strip()

    def speak(self, round_num: int, short_term: ShortTermMemory, topic: str) -> AgentOutput:
        opponent_msg = short_term.get_latest_opponent_message(self.role)
        opponent_content = opponent_msg["content"] if opponent_msg else "暂无"
        teacher_feedback = short_term.get_latest_teacher_feedback()
        search_results = self.web_search.search_web(topic, num_results=3)
        historical = self.long_term_memory.search_similar(topic, n_results=2)
        recommended_strategy = self.strategy.recommend(self.role)
        teacher_advice = f"教师上轮点评与建议: {teacher_feedback}\n" if round_num > 1 and teacher_feedback else ""
        prompt = (
            f"{self.system_prompt}\n\n辩题: {topic}\n第{round_num}轮\n对方上一轮发言: {opponent_content}\n"
            f"{teacher_advice}搜索到的参考资料:\n{search_results}\n\n历史辩论经验:\n{historical}\n\n"
            f"推荐策略:\n{recommended_strategy}\n\n内部流程：1.思考核心论点 2.自查可靠性 3.修正后输出\n\n请直接给出正式发言（200字以内）:"
        )
        return AgentOutput(role=self.role, content=self.llm.invoke(prompt).content.strip(), round_num=round_num, tools_used=["web_search","rag_retrieval","strategy_recommender"])

"""Debate strategy recommendation tool."""

STRATEGIES = {
    "pro": [
        "正面立论: 先给出明确的核心主张，再用数据和案例支撑",
        "反驳策略: 抓住对方论据漏洞，用更强的证据反击",
        "类比论证: 用通俗的类比解释复杂观点",
        "价值升华: 将具体论点上升到价值观层面",
    ],
    "con": [
        "质疑前提: 质疑对方立论的基础假设",
        "反例攻击: 举出对方论点无法解释的反例",
        "利弊分析: 展示正方方案的潜在风险和代价",
        "替代方案: 提出比正方案更优的替代选择",
    ],
}


class StrategyRecommenderTool:
    """Recommends debate strategies based on current context."""

    def recommend(self, role: str) -> str:
        role_key = "pro" if role in ("pro", "正方") else "con"
        strategies = STRATEGIES.get(role_key, [])
        return "推荐辩论策略:\n" + "\n".join(f"- {s}" for s in strategies)

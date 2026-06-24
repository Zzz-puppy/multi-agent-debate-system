"""Argument quality evaluation tool using LLM-as-a-Judge."""

import json
from utils.llm_manager import get_llm


EVALUATION_PROMPT = """你是一位辩论评审专家。请从以下四个维度评估这段辩论论点，每个维度1-10分：

1. **逻辑性**: 论点结构是否清晰，推理是否严谨
2. **论据质量**: 证据是否充分、数据是否可靠、来源是否可信
3. **反驳能力**: 是否能有效回应对方质疑、抓住对方漏洞
4. **语言表达**: 表达是否清晰、有说服力、有感染力

论点: {argument}

请以JSON格式输出评分和简短评语:
{{"logic_score": int, "evidence_score": int, "rebuttal_score": int, "expression_score": int, "comment": "..."}}
"""


class ArgumentEvaluatorTool:
    def __init__(self, llm=None):
        self.llm = llm or get_llm(temperature=0.0)

    def evaluate(self, argument: str) -> dict:
        try:
            response = self.llm.invoke(EVALUATION_PROMPT.format(argument=argument))
            content = response.content.strip()
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            result = json.loads(content.strip())
            result["total_score"] = sum(result.get(k, 0) * 0.25 for k in ["logic_score","evidence_score","rebuttal_score","expression_score"])
            return result
        except Exception as e:
            return {"logic_score": 0, "evidence_score": 0, "rebuttal_score": 0, "expression_score": 0, "total_score": 0, "comment": f"评估失败: {str(e)}"}

"""Independent scoring system — standardized criteria, rules, and aggregation."""
from __future__ import annotations
from typing import TypedDict

class RoundScore(TypedDict):
    logic_score: int; evidence_score: int; rebuttal_score: int; expression_score: int

class RoundEval(TypedDict):
    round: int; pro: RoundScore; con: RoundScore

CRITERIA = [{"key":"logic_score","name":"逻辑性","weight":0.25},{"key":"evidence_score","name":"论据质量","weight":0.25},{"key":"rebuttal_score","name":"反驳能力","weight":0.25},{"key":"expression_score","name":"语言表达","weight":0.25}]

def format_criteria() -> str:
    return "\n".join(["## 评分标准（每项1-10分）"] + [f"- **{c['name']}**: 1-10分" for c in CRITERIA])

def compute_total(scores: RoundScore) -> float:
    return sum(scores[k] * 0.25 for k in ["logic_score","evidence_score","rebuttal_score","expression_score"])

CRITERIA_KEYS = ["logic_score","evidence_score","rebuttal_score","expression_score"]

def aggregate(rounds: list[RoundEval]) -> dict:
    if not rounds:
        return {"pro_score":0,"con_score":0,"winner":"平局","pro_details":{},"con_details":{}}
    def _avg(k):
        return {key: round(sum(r[k].get(key,0) for r in rounds)/len(rounds), 1) for key in CRITERIA_KEYS}
    pro_score, con_score = round(sum(compute_total(r["pro_scores"]) for r in rounds)/len(rounds)), round(sum(compute_total(r["con_scores"]) for r in rounds)/len(rounds))
    return {"pro_score":pro_score,"con_score":con_score,"winner":"pro" if pro_score>con_score else "con" if con_score>pro_score else "平局","pro_details":_avg("pro_scores"),"con_details":_avg("con_scores")}

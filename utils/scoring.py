"""Independent scoring system — standardized criteria, rules, and aggregation."""

from __future__ import annotations
from typing import TypedDict


class RoundScore(TypedDict):
    logic_score: int
    evidence_score: int
    rebuttal_score: int
    expression_score: int


class RoundEval(TypedDict):
    round: int
    pro: RoundScore
    con: RoundScore


CRITERIA = [
    {"key": "logic_score", "name": "逻辑性", "weight": 0.25, "description": "论点结构是否清晰、论证是否层层递进"},
    {"key": "evidence_score", "name": "论据质量", "weight": 0.25, "description": "证据是否充分、数据是否可靠、来源是否可信"},
    {"key": "rebuttal_score", "name": "反驳能力", "weight": 0.25, "description": "是否能有效回应对方质疑、抓住对方漏洞"},
    {"key": "expression_score", "name": "语言表达", "weight": 0.25, "description": "表达是否清晰、有说服力、有感染力"},
]


def format_criteria() -> str:
    lines = ["## 评分标准（每项1-10分）"]
    for c in CRITERIA:
        lines.append(f"- **{c['name']}**: {c['description']}")
    return "\n".join(lines)


def compute_total(scores: RoundScore) -> float:
    return (
        scores["logic_score"] * 0.25
        + scores["evidence_score"] * 0.25
        + scores["rebuttal_score"] * 0.25
        + scores["expression_score"] * 0.25
    )


CRITERIA_KEYS = ["logic_score", "evidence_score", "rebuttal_score", "expression_score"]


def aggregate(rounds: list[RoundEval]) -> dict:
    if not rounds:
        return {"pro_score": 0, "con_score": 0, "winner": "平局", "pro_details": {}, "con_details": {}}

    pro_totals = [compute_total(r["pro_scores"]) for r in rounds]
    con_totals = [compute_total(r["con_scores"]) for r in rounds]

    pro_avg = sum(pro_totals) / len(pro_totals)
    con_avg = sum(con_totals) / len(con_totals)

    def _avg_criteria(side_key: str) -> dict:
        avgs = {}
        for key in CRITERIA_KEYS:
            vals = [r[side_key].get(key, 0) for r in rounds]
            avgs[key] = round(sum(vals) / len(vals), 1)
        return avgs

    pro_details = _avg_criteria("pro_scores")
    con_details = _avg_criteria("con_scores")

    pro_score = round(pro_avg)
    con_score = round(con_avg)

    if pro_score > con_score:
        winner = "pro"
    elif con_score > pro_score:
        winner = "con"
    else:
        winner = "平局"

    return {
        "pro_score": pro_score,
        "con_score": con_score,
        "winner": winner,
        "pro_details": pro_details,
        "con_details": con_details,
    }

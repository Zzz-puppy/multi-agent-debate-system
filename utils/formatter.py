"""Debate output formatter — generates markdown debate records."""

import os
from datetime import datetime

from graph.state import DebateState

ROLE_NAMES = {"pro": "正方学生", "con": "反方学生", "teacher": "教师"}


def format_debate_output(state: DebateState) -> str:
    lines = []
    lines.append("# 多智能体课堂辩论记录\n")
    lines.append(f"**辩题**: {state['topic']}\n")
    lines.append(f"**辩论轮数**: {state['max_rounds']}\n")
    lines.append(f"**日期**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    lines.append("---\n")

    for msg in state["conversation_history"]:
        role_name = ROLE_NAMES.get(msg["role"], msg["role"])
        round_label = f"第{msg['round_num']}轮" if msg["round_num"] > 0 else "开场"
        lines.append(f"### {role_name} ({round_label})\n")
        if msg["tools_used"]:
            lines.append(f"*使用工具: {', '.join(msg['tools_used'])}*\n")
        lines.append(f"{msg['content']}\n")
        lines.append("---\n")

    if state["scores"]:
        lines.append("## 最终评分\n")
        lines.append("| 角色 | 得分 |\n|------|------|\n")
        lines.append(f"| 正方 | {state['scores'].get('pro', 'N/A')} |\n")
        lines.append(f"| 反方 | {state['scores'].get('con', 'N/A')} |\n")
        lines.append(f"\n**获胜方**: {ROLE_NAMES.get(state['winner'], state['winner'])}\n")

    if state["teacher_summary"]:
        lines.append(f"\n## 教师总结\n\n{state['teacher_summary']}\n")

    return "\n".join(lines)


def save_debate_record(state: DebateState, output_dir: str = "output") -> str:
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"debate_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)
    content = format_debate_output(state)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath

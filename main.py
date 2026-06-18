"""Multi-Agent Classroom Debate System — Main Entry Point."""

import os
import json
from dotenv import load_dotenv

from utils.llm_manager import get_llm

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


def validate_topic(topic: str) -> tuple[bool, str]:
    """Use AI to check if the input is a valid debate topic."""
    llm = get_llm(temperature=0.1)
    prompt = (
        "你是一个辩题验证系统。请判断以下输入是否是一个有效的辩论辩题。\n\n"
        "有效辩题的标准：\n"
        "1. 它应该是一个有争议的问题，存在至少两个对立的观点\n"
        "2. 它不是简单的知识性问题或事实陈述\n"
        "3. 它不涉及违法违规或不道德的内容\n"
        "4. 它适合在课堂环境中展开辩论\n\n"
        f"输入: {topic}\n\n"
        "请用JSON格式回答：\n"
        '{"valid": true/false, "reason": "如果有效则返回有效辩题，否则写明拒绝原因"}'
    )
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        result = json.loads(content.strip())
        return result.get("valid", True), result.get("reason", "有效辩题")
    except Exception:
        return True, "有效辩题"


def main():
    print("=" * 50)
    print("  多智能体课堂辩论系统")
    print("=" * 50)

    if not DEEPSEEK_API_KEY:
        print("错误: 请设置 DEEPSEEK_API_KEY 环境变量")
        print("提示: 在 .env 文件中添加 DEEPSEEK_API_KEY=your_key")
        print("       (复制 .env.example 为 .env 并填入你的 DeepSeek API Key)")
        return

    while True:
        topic_input = input("\n请输入辩题（或输入 'preset' 选择预设辩题）: ").strip()
        if topic_input.lower() == "preset":
            topic = select_preset_topic()
            break
        elif topic_input:
            print("  正在验证辩题...", end="", flush=True)
            valid, reason = validate_topic(topic_input)
            print(f"\r  {'✓' if valid else '✗'} {reason}")
            if valid:
                topic = topic_input
                break
            print("  请重新输入一个有效的辩论辩题。")
        else:
            topic = "人工智能是否应该被广泛应用于教育领域？"
            break

    rounds_input = input("请输入辩论轮数（默认 3 轮，最大 10 轮）: ").strip()
    try:
        max_rounds = min(max(1, int(rounds_input)), 10)
    except ValueError:
        max_rounds = 3

    print(f"\n{'=' * 50}")
    print(f"辩题: {topic}")
    print(f"轮次: {max_rounds} 轮")
    print(f"{'=' * 50}\n")

    from graph.debate_graph import DebateOrchestrator
    from utils.formatter import save_debate_record

    orchestrator = DebateOrchestrator()
    print("辩论开始...\n")
    result = orchestrator.run_debate(topic, max_rounds)

    filepath = save_debate_record(result)
    print(f"\n辩论记录已保存到: {filepath}")

    print(f"\n{'=' * 50}")
    print("  辩论结束")
    print(f"{'=' * 50}")
    if result["scores"]:
        winner_text = {"pro": "正方", "con": "反方", "平局": "平局"}.get(result["winner"], result["winner"])
        print(f"正方得分: {result['scores'].get('pro', 'N/A')}")
        print(f"反方得分: {result['scores'].get('con', 'N/A')}")
        print(f"获胜方: {winner_text}")
    print(f"\n完整记录已保存至: {filepath}")
    print(f"可打开该 .md 文件查看详细的辩论过程")


def select_preset_topic() -> str:
    from data.preset_topics import list_topics, get_topic_by_index
    print("\n预设辩题:")
    print(list_topics())
    try:
        choice = int(input("请选择辩题编号: ").strip())
        return get_topic_by_index(choice - 1)
    except (ValueError, IndexError):
        print("无效选择，使用默认辩题")
        return "人工智能是否应该被广泛应用于教育领域？"


if __name__ == "__main__":
    main()

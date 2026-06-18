"""LangGraph debate workflow definition."""

from graph.state import DebateState, AgentOutput, RoundEvalEntry
from memory.short_term import ShortTermMemory
from agents.student_agent import StudentAgent
from agents.teacher_agent import TeacherAgent
from utils.scoring import aggregate


class DebateOrchestrator:
    """Manages the debate workflow with preparation phase."""

    def __init__(self):
        self.pro_agent = StudentAgent(role="pro")
        self.con_agent = StudentAgent(role="con")
        self.teacher = TeacherAgent()
        self.short_term = ShortTermMemory()

    def run_debate(self, topic: str, max_rounds: int = 3) -> DebateState:
        state: DebateState = {
            "topic": topic,
            "max_rounds": max_rounds,
            "current_round": 0,
            "conversation_history": [],
            "round_scores": [],
            "scores": None,
            "winner": None,
            "teacher_summary": None,
        }

        # Phase 1: Opening
        print(f"\n[教师开场]")
        opening = self.teacher.opening_speech(topic, max_rounds)
        state["conversation_history"].append(opening)
        self.short_term.add_message(opening)
        print(f"{opening['content']}\n")

        # Phase 2: Preparation
        print(f"[正方准备中]", end="", flush=True)
        self.pro_agent.prepare(topic)
        print(f" ✓")
        print(f"[反方准备中]", end="", flush=True)
        self.con_agent.prepare(topic)
        print(f" ✓\n")

        # Phase 3: Debate rounds
        for round_num in range(1, max_rounds + 1):
            state["current_round"] = round_num
            print(f"\n{'='*20} 第{round_num}轮 {'='*20}")

            print(f"[正方发言]")
            pro_output = self.pro_agent.speak(round_num, self.short_term, topic)
            state["conversation_history"].append(pro_output)
            self.short_term.add_message(pro_output)
            print(f"{pro_output['content']}\n")

            print(f"[反方发言]")
            con_output = self.con_agent.speak(round_num, self.short_term, topic)
            state["conversation_history"].append(con_output)
            self.short_term.add_message(con_output)
            print(f"{con_output['content']}\n")

            is_last_round = (round_num == max_rounds)
            print(f"[教师点评]")
            teacher_output, pro_eval, con_eval = self.teacher.evaluate_round(
                round_num, pro_output["content"], con_output["content"],
                self.short_term, is_last_round=is_last_round,
            )
            state["conversation_history"].append(teacher_output)
            self.short_term.add_message(teacher_output)
            print(f"{teacher_output['content']}\n")

            state["round_scores"].append(RoundEvalEntry(
                round=round_num,
                pro_scores=pro_eval,
                con_scores=con_eval,
            ))

        # Phase 4: Summary
        print(f"\n[教师总结]")
        final_scores = aggregate(state["round_scores"])
        state["scores"] = {
            "pro": final_scores["pro_score"],
            "con": final_scores["con_score"],
        }
        state["winner"] = final_scores["winner"]

        summary = self.teacher.summarize_debate(
            topic, max_rounds, state["conversation_history"],
            final_scores["pro_score"], final_scores["con_score"],
            final_scores["winner"],
        )
        state["teacher_summary"] = summary
        winner_text = {"pro": "正方", "con": "反方", "平局": "平局"}.get(
            final_scores["winner"], final_scores["winner"]
        )

        CRITERIA_LABELS = {
            "logic_score": "逻辑性",
            "evidence_score": "论据质量",
            "rebuttal_score": "反驳能力",
            "expression_score": "语言表达",
        }
        print(f"\n{'='*50}")
        print(f"  最终评分")
        print(f"{'='*50}")
        for side, label in [("pro_details", "正方"), ("con_details", "反方")]:
            details = final_scores[side]
            print(f"  {label}:")
            for key, cname in CRITERIA_LABELS.items():
                print(f"    {cname}: {details.get(key, 0)}/10")
            total = sum(details.get(k, 0) for k in CRITERIA_LABELS) * 0.25
            print(f"    总分: {total:.1f}")
        print(f"\n  正方: {final_scores['pro_score']}分 | 反方: {final_scores['con_score']}分")
        print(f"  获胜方: {winner_text}")
        print(f"{'='*50}\n")

        # Phase 5: Archive
        self._archive_debate(state)

        # Phase 6: Update profiles
        self.pro_agent.profile.update_after_debate(
            topic, final_scores["pro_score"], summary, [], [],
        )
        self.con_agent.profile.update_after_debate(
            topic, final_scores["con_score"], summary, [], [],
        )

        return state

    def _archive_debate(self, state: DebateState) -> None:
        pro_args = [m["content"] for m in state["conversation_history"] if m["role"] == "pro"]
        con_args = [m["content"] for m in state["conversation_history"] if m["role"] == "con"]
        self.teacher.long_term.store_debate(
            topic=state["topic"],
            summary=state["teacher_summary"] or "",
            pro_arguments=pro_args,
            con_arguments=con_args,
            teacher_score={
                "pro": state["scores"]["pro"],
                "con": state["scores"]["con"],
                "winner": state["winner"],
            },
            teacher_comment=state["teacher_summary"] or "",
        )

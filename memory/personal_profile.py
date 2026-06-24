"""Personal profile memory for each agent — JSON-based persistent memory."""

import json
import os

DEFAULT_PROFILE = {"debate_count":0,"strong_topics":[],"weak_topics":[],"last_feedback":"","improvement_suggestions":[]}


class PersonalProfile:
    def __init__(self, role: str, profile_dir: str = "data/profiles"):
        self.role = role
        self.profile_path = os.path.join(profile_dir, f"{role}.json")
        self.data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.profile_path):
            with open(self.profile_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {**DEFAULT_PROFILE, "role": self.role}

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.profile_path), exist_ok=True)
        with open(self.profile_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def update_after_debate(self, topic: str, score: float, feedback: str, strengths: list, weaknesses: list) -> None:
        self.data["debate_count"] += 1
        self.data["last_feedback"] = feedback
        (self.data["strong_topics"] if score >= 7 else self.data["weak_topics"]).append(topic)
        if weaknesses:
            self.data["improvement_suggestions"].extend(weaknesses)
        for k in ["strong_topics","weak_topics","improvement_suggestions"]:
            self.data[k] = self.data[k][-10:]
        self.save()

    def get_strategy_advice(self) -> str:
        advice = []
        if self.data["strong_topics"]:
            advice.append(f"你擅长的辩题类型: {', '.join(self.data['strong_topics'][-3:])}")
        if self.data["improvement_suggestions"]:
            advice.append(f"改进建议: {self.data['improvement_suggestions'][-1]}")
        return "\n".join(advice) if advice else "暂无历史经验记录。"

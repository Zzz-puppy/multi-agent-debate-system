"""Preset debate topics."""

PRESET_TOPICS = [
    "人工智能是否应该被广泛应用于教育领域？",
    "当代社会中，性别对立问题的主要责任在于社会结构还是个人观念？",
    "大学生毕业后应该选择就业还是读研？",
]


def get_topic_by_index(index: int) -> str:
    if 0 <= index < len(PRESET_TOPICS):
        return PRESET_TOPICS[index]
    raise IndexError(f"Invalid topic index {index}. Choose 0-{len(PRESET_TOPICS) - 1}")


def list_topics() -> str:
    return "\n".join(f"{i + 1}. {t}" for i, t in enumerate(PRESET_TOPICS))

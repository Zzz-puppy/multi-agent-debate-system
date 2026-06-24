"""LLM Manager — centralized ChatOpenAI instance management with caching."""
import os
from langchain_openai import ChatOpenAI

_instances: dict = {}

def get_llm(temperature: float = 0.3, model: str | None = None) -> ChatOpenAI:
    key = (temperature, model or "deepseek-v4-flash")
    if key not in _instances:
        _instances[key] = ChatOpenAI(model=model or "deepseek-v4-flash", openai_api_key=os.getenv("DEEPSEEK_API_KEY"), openai_api_base="https://api.deepseek.com", temperature=temperature)
    return _instances[key]

def clear_cache() -> None:
    _instances.clear()

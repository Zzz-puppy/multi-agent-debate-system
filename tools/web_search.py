"""Web search tool using DuckDuckGo (free, no API key required)."""

from typing import List

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper


class WebSearchTool:
    """Search the web for real-time information to support arguments."""

    def __init__(self):
        wrapper = DuckDuckGoSearchAPIWrapper(
            max_results=5,
            region="cn-zh",
            source="web",
        )
        self.search = DuckDuckGoSearchRun(api_wrapper=wrapper)

    def search_web(self, query: str, num_results: int = 5) -> List[dict]:
        try:
            result_text = self.search.run(query)
            snippets = [s.strip() for s in result_text.split("\n") if s.strip()]
            results = []
            for i, snippet in enumerate(snippets[:num_results]):
                results.append({
                    "title": f"结果 {i + 1}",
                    "content": snippet,
                    "url": "",
                })
            return results if results else [
                {"title": "提示", "content": "搜索未返回结果，请尝试调整查询词", "url": ""}
            ]
        except Exception as e:
            return [
                {"title": "Error", "content": f"搜索失败: {str(e)}", "url": ""}
            ]

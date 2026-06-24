"""Web search tool using DuckDuckGo (free, no API key required)."""

from typing import List
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper


class WebSearchTool:
    def __init__(self):
        wrapper = DuckDuckGoSearchAPIWrapper(max_results=5, region="cn-zh", source="web")
        self.search = DuckDuckGoSearchRun(api_wrapper=wrapper)

    def search_web(self, query: str, num_results: int = 5) -> List[dict]:
        try:
            snippets = [s.strip() for s in self.search.run(query).split("\n") if s.strip()]
            return [{"title": f"结果 {i+1}", "content": s, "url": ""} for i, s in enumerate(snippets[:num_results])] or [{"title":"提示","content":"搜索未返回结果","url":""}]
        except Exception as e:
            return [{"title":"Error","content":f"搜索失败: {str(e)}","url":""}]

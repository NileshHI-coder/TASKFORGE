import os
import time
from tavily import TavilyClient

class TavilyService:
    """Backend-only Tavily adapter with bounded retries and normalized evidence."""
    def __init__(self):
        key = os.getenv("TAVILY_API_KEY")
        if not key:
            raise ValueError("TAVILY_API_KEY is not configured in the project .env file.")
        self.client = TavilyClient(api_key=key)

    def search(self, query, max_results=6, search_depth="advanced", topic="general", include_domains=None, exclude_domains=None):
        if not isinstance(query, str) or not query.strip():
            raise ValueError("A non-empty research query is required.")
        kwargs = {"query": query.strip(), "max_results": max(1, min(int(max_results), 10)),
                  "search_depth": search_depth if search_depth in {"basic", "advanced"} else "advanced",
                  "topic": topic if topic in {"general", "news", "finance"} else "general"}
        if include_domains:
            kwargs["include_domains"] = include_domains[:10]
        if exclude_domains:
            kwargs["exclude_domains"] = exclude_domains[:10]
        last_error = None
        for attempt in range(3):
            try:
                response = self.client.search(**kwargs)
                results = response.get("results", [])
                return [{"title": item.get("title") or "Untitled source", "url": item.get("url"),
                         "content": item.get("content") or "", "published_date": item.get("published_date"),
                         "score": item.get("score")} for item in results if item.get("url")]
            except Exception as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(0.7 * (attempt + 1))
        raise RuntimeError(f"Tavily search failed after 3 attempts: {last_error}")

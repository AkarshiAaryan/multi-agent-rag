"""Tool implementations for the multi-agent research assistant."""

from __future__ import annotations

import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_core.tools import tool
from tavily import TavilyClient

load_dotenv()


def get_tavily_client() -> TavilyClient | None:
    """Create a Tavily client from the environment when a key is available."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return None
    return TavilyClient(api_key=api_key)


@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Returns titles, URLs, and snippets."""
    client = get_tavily_client()
    if client is None:
        return "Tavily API key is missing. Add TAVILY_API_KEY to your .env file."

    try:
        response = client.search(query=query, max_results=5)
        results = response.get("results", [])

        if not results:
            return "No web results were returned for this query."

        blocks: list[str] = []
        for item in results:
            title = item.get("title", "Untitled")
            url = item.get("url", "")
            snippet = (item.get("content") or "").strip()
            if len(snippet) > 300:
                snippet = snippet[:297] + "..."

            block = f"Title: {title}\nURL: {url}\nSnippet: {snippet}"
            blocks.append(block)

        return "\n---\n".join(blocks)
    except Exception as exc:  # pragma: no cover - defensive error handling
        return f"Web search failed: {exc}"


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    if not url:
        return "No URL provided for scraping."

    try:
        response = requests.get(
            url,
            timeout=8,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        text = soup.get_text(separator=" ")
        text = " ".join(text.split())

        if len(text) > 3000:
            text = text[:2997] + "..."

        return text or "No readable text was found on this page."
    except Exception as exc:  # pragma: no cover - defensive error handling
        return f"Failed to scrape {url}: {exc}"

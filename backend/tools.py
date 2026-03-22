# FILE: tools.py
# Async tool implementations for web search using Tavily

import os
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "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")

# Initialize Tavily client
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)


async def brave_search(query: str, count: int = 5) -> list[dict]:
    """
    Search the web using Tavily Search API.

    Args:
        query: The search query string
        count: Number of results to return (default 5)

    Returns:
        List of dicts with title, url, and snippet for each result
    """
    try:
        # Tavily is synchronous, run in executor
        import asyncio
        response = await asyncio.to_thread(
            tavily_client.search,
            query=query,
            search_depth="advanced",
            max_results=count,
            include_answer=False
        )

        results = []
        for item in response.get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", "")[:500],  # Tavily provides full content, truncate for snippet
            })

        return results

    except Exception as e:
        print(f"Error in tavily_search: {e}")
        return []


async def scrape_page(url: str) -> str:
    """
    Fetch and extract clean text content from a web page.

    Args:
        url: The URL to scrape

    Returns:
        Clean text content (max 3000 characters) from the page
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove unwanted tags
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            # Try to find the main content area
            content = soup.find("article")
            if not content:
                content = soup.find("main")
            if not content:
                content = soup.find("body")

            if content:
                text = content.get_text(separator="\n", strip=True)
                # Clean up whitespace
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                text = "\n".join(lines)
                # Return first 3000 characters
                return text[:3000]

            return ""

    except Exception as e:
        print(f"Error in scrape_page: {e}")
        return ""

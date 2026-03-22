# FILE: tools.py
# Async tool implementations for web search and page scraping

import os
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")


async def brave_search(query: str, count: int = 5) -> list[dict]:
    """
    Search the web using Brave Search API.

    Args:
        query: The search query string
        count: Number of results to return (default 5)

    Returns:
        List of dicts with title, url, and snippet for each result
    """
    try:
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": BRAVE_API_KEY,
        }
        params = {"q": query, "count": count}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("web", {}).get("results", []):
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("description", ""),
                    }
                )

            return results

    except Exception as e:
        print(f"Error in brave_search: {e}")
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

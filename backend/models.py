# FILE: models.py
# Pydantic models for request/response validation in the AI Research Agent

from pydantic import BaseModel
from typing import List, Optional


class ResearchRequest(BaseModel):
    """Model for incoming research query requests from the frontend."""

    query: str


class SearchResult(BaseModel):
    """Model representing a single search result from Brave Search API."""

    title: str
    url: str
    snippet: str


class AgentMessage(BaseModel):
    """Model representing a message in the conversation between user and agent."""

    role: str
    content: str
    sources: Optional[List[SearchResult]] = None

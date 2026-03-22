# FILE: models.py
# Pydantic models for request/response validation in the AI Research Agent

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


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


class SessionInfo(BaseModel):
    """Model for session summary (without full response)."""

    id: int
    query: str
    status: str
    created_at: str
    updated_at: Optional[str] = None


class SessionSearchResult(BaseModel):
    """Model for search results stored in a session."""

    id: int
    query: str
    results: List[dict]
    created_at: str


class SessionScrapedPage(BaseModel):
    """Model for scraped pages stored in a session."""

    id: int
    url: str
    content: str
    created_at: str


class SessionResponse(BaseModel):
    """Model for full session details response."""

    id: int
    query: str
    response: Optional[str] = None
    status: str
    created_at: str
    updated_at: Optional[str] = None
    search_results: List[SessionSearchResult] = []
    scraped_pages: List[SessionScrapedPage] = []


class SessionListResponse(BaseModel):
    """Model for list of sessions response."""

    sessions: List[SessionInfo]

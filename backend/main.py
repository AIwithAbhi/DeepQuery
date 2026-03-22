# FILE: main.py
# FastAPI application for the AI Research Agent backend

import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from typing import Optional

from models import ResearchRequest, SessionResponse, SessionListResponse
from pydantic import BaseModel
from agent import run_agent
from database import (
    create_session,
    update_session,
    get_session,
    get_all_sessions,
    delete_session,
    get_session_search_results,
    get_session_scraped_pages,
)

load_dotenv()

app = FastAPI(title="AI Research Agent API")

# Configure CORS for frontend running on localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "ok"}


@app.post("/research")
async def research(request: ResearchRequest):
    """
    Research endpoint that accepts a query and streams back the agent's response.
    Also saves the session and response to the database.

    Returns a Server-Sent Events (SSE) stream with the following message types:
    - type: "status" - Status updates during tool execution
    - type: "text" - Chunks of the final response text
    - type: "done" - Signal that the response is complete with session_id
    - type: "error" - Error messages if something goes wrong
    """
    # Create a new session
    session_id = create_session(request.query)

    async def event_generator():
        full_response = []
        try:
            async for chunk in run_agent(request.query):
                data = chunk.replace("data: ", "").strip()
                if data:
                    try:
                        parsed = json.loads(data)
                        if parsed.get("type") == "text":
                            full_response.append(parsed.get("text", ""))
                    except json.JSONDecodeError:
                        pass
                yield chunk

            # Save the complete response to database
            complete_response = "".join(full_response)
            update_session(session_id, complete_response, "completed")

            # Yield the session_id with done message
            done_msg = {"type": "done", "session_id": session_id}
            yield f"data: {json.dumps(done_msg)}\n\n"

        except Exception as e:
            error_msg = {"type": "error", "text": str(e)}
            update_session(session_id, str(e), "error")
            yield f"data: {json.dumps(error_msg)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


class CloseSessionRequest(BaseModel):
    """Model for closing a session request."""
    messages: list = []
    query: str = ""


@app.post("/sessions/{session_id}/close")
async def close_session_endpoint(session_id: int, request: CloseSessionRequest):
    """
    Close/save a session manually with full conversation data.

    This endpoint allows users to explicitly save and close a session,
    storing all messages and conversation context to the database.
    """
    # Check if session exists
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Compile full conversation as response
        if request.messages:
            conversation_text = json.dumps(request.messages, indent=2)
        else:
            conversation_text = session.get("response", "")

        # Update session with closed status
        update_session(session_id, conversation_text, "closed")

        return {
            "message": "Session closed and saved successfully",
            "session_id": session_id,
            "status": "closed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error closing session: {str(e)}")


@app.get("/sessions", response_model=SessionListResponse)
async def list_sessions(limit: int = 50):
    """Get all research sessions."""
    sessions = get_all_sessions(limit)
    return {"sessions": sessions}


@app.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session_by_id(session_id: int):
    """Get a specific research session with all details."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    search_results = get_session_search_results(session_id)
    scraped_pages = get_session_scraped_pages(session_id)

    return {
        "id": session["id"],
        "query": session["query"],
        "response": session["response"],
        "status": session["status"],
        "created_at": session["created_at"],
        "updated_at": session["updated_at"],
        "search_results": search_results,
        "scraped_pages": scraped_pages,
    }


@app.delete("/sessions/{session_id}")
async def delete_session_by_id(session_id: int):
    """Delete a research session."""
    success = delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

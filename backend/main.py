# FILE: main.py
# FastAPI application for the AI Research Agent backend

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

from models import ResearchRequest
from agent import run_agent

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

    Returns a Server-Sent Events (SSE) stream with the following message types:
    - type: "status" - Status updates during tool execution
    - type: "text" - Chunks of the final response text
    - type: "done" - Signal that the response is complete
    - type: "error" - Error messages if something goes wrong
    """

    async def event_generator():
        async for chunk in run_agent(request.query):
            yield chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# FILE: agent.py
# Core agent logic implementing the research loop with Kimi via NVIDIA API

import os
import json
import asyncio
from typing import AsyncGenerator
import httpx
from dotenv import load_dotenv

from prompts import SYSTEM_PROMPT
from tools import brave_search, scrape_page

load_dotenv()

# NVIDIA API Configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
MODEL_NAME = "moonshotai/kimi-k2.5"


def get_tools_list():
    """Returns the list of available tools in OpenAI-compatible format."""
    return [
        {
            "type": "function",
            "function": {
                "name": "brave_search",
                "description": "Search the web using Brave Search API",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query"},
                        "count": {
                            "type": "integer",
                            "description": "Number of results to return (default 5)",
                            "default": 5,
                        },
                    },
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "scrape_page",
                "description": "Fetch and extract clean text from a web page URL",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "The URL to scrape"}
                    },
                    "required": ["url"],
                },
            },
        },
    ]


async def call_nvidia_api(messages: list, tools: list, stream: bool = False) -> dict:
    """
    Call NVIDIA API for chat completions.

    Args:
        messages: List of message dicts with role and content
        tools: List of available tools
        stream: Whether to stream the response

    Returns:
        API response as dict
    """
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": 4096,
        "temperature": 0.7,
        "top_p": 1.0,
        "stream": stream,
        "tools": tools,
        "tool_choice": "auto",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{NVIDIA_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        return response.json()


async def run_agent(query: str) -> AsyncGenerator[str, None]:
    """
    Run the research agent with the given query.

    Implements an agentic loop that:
    1. Sends query to Kimi via NVIDIA API with available tools
    2. Handles tool calls (search, scrape)
    3. Streams back status updates and final response

    Args:
        query: The user's research question

    Yields:
        SSE-formatted JSON strings for stream consumption
    """
    try:
        tools_list = get_tools_list()
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]
        max_iterations = 10

        for iteration in range(max_iterations):
            # Call the model via NVIDIA API
            response = await call_nvidia_api(messages, tools_list)

            choice = response.get("choices", [{}])[0]
            message = choice.get("message", {})
            finish_reason = choice.get("finish_reason", "")
            tool_calls = message.get("tool_calls", [])

            if tool_calls and finish_reason == "tool_calls":
                # Add assistant message with tool calls
                messages.append(message)

                # Execute each tool call
                for tool_call in tool_calls:
                    function = tool_call.get("function", {})
                    tool_name = function.get("name", "")
                    tool_inputs = json.loads(function.get("arguments", "{}"))
                    tool_call_id = tool_call.get("id", "")

                    # Yield status update
                    search_target = tool_inputs.get("query") or tool_inputs.get(
                        "url", ""
                    )
                    status_msg = {
                        "type": "status",
                        "text": f"🔎 Searching: {search_target[:50]}{'...' if len(search_target) > 50 else ''}",
                    }
                    yield f"data: {json.dumps(status_msg)}\n\n"

                    # Execute the tool
                    if tool_name == "brave_search":
                        result = await brave_search(
                            query=tool_inputs["query"],
                            count=tool_inputs.get("count", 5),
                        )
                    elif tool_name == "scrape_page":
                        result = await scrape_page(url=tool_inputs["url"])
                        result = {"content": result}  # Wrap in dict for consistency
                    else:
                        result = {"error": f"Unknown tool: {tool_name}"}

                    # Add tool result to messages
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "content": json.dumps(result),
                        }
                    )

                # Continue to next iteration
                continue

            elif finish_reason == "stop":
                # Extract the final text response
                final_text = message.get("content", "")

                # Stream the response word by word
                words = final_text.split(" ")
                for word in words:
                    text_msg = {"type": "text", "text": word + " "}
                    yield f"data: {json.dumps(text_msg)}\n\n"
                    await asyncio.sleep(0.03)

                # Signal completion
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                break

            else:
                # Unexpected stop reason
                error_msg = {
                    "type": "error",
                    "text": f"Unexpected finish reason: {finish_reason}",
                }
                yield f"data: {json.dumps(error_msg)}\n\n"
                break

    except Exception as e:
        error_msg = {"type": "error", "text": str(e)}
        yield f"data: {json.dumps(error_msg)}\n\n"

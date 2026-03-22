# FILE: agent.py
# Core agent logic implementing the research loop with Claude/Kimi via OpenRouter

import os
import json
import asyncio
from typing import AsyncGenerator
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

from prompts import SYSTEM_PROMPT
from tools import brave_search, scrape_page

load_dotenv()

# Configure Anthropic client for OpenRouter
client = AsyncAnthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
)

# Model name for Kimi K2.5 via OpenRouter
MODEL_NAME = "moonshotai/kimi-k2.5"


def get_tools_list():
    """Returns the list of available tools in Anthropic tool_use format."""
    return [
        {
            "name": "brave_search",
            "description": "Search the web using Brave Search API",
            "input_schema": {
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
        {
            "name": "scrape_page",
            "description": "Fetch and extract clean text from a web page URL",
            "input_schema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to scrape"}
                },
                "required": ["url"],
            },
        },
    ]


async def run_agent(query: str) -> AsyncGenerator[str, None]:
    """
    Run the research agent with the given query.

    Implements an agentic loop that:
    1. Sends query to Claude/Kimi with available tools
    2. Handles tool calls (search, scrape)
    3. Streams back status updates and final response

    Args:
        query: The user's research question

    Yields:
        SSE-formatted JSON strings for stream consumption
    """
    try:
        tools_list = get_tools_list()
        messages = [{"role": "user", "content": query}]
        max_iterations = 10

        for iteration in range(max_iterations):
            # Call the model
            response = await client.messages.create(
                model=MODEL_NAME,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=tools_list,
                messages=messages,
                stream=False,
            )

            if response.stop_reason == "tool_use":
                # Extract tool use blocks
                tool_use_blocks = []
                text_content = ""

                for block in response.content:
                    if block.type == "tool_use":
                        tool_use_blocks.append(block)
                    elif block.type == "text":
                        text_content += block.text

                # Add assistant message to history
                messages.append({"role": "assistant", "content": response.content})

                # Execute each tool call
                for tool_block in tool_use_blocks:
                    tool_name = tool_block.name
                    tool_inputs = tool_block.input
                    tool_use_id = tool_block.id

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
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_use_id,
                                    "content": json.dumps(result),
                                }
                            ],
                        }
                    )

                # Continue to next iteration
                continue

            elif response.stop_reason == "end_turn":
                # Extract the final text response
                final_text = ""
                for block in response.content:
                    if block.type == "text":
                        final_text += block.text

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
                    "text": f"Unexpected stop reason: {response.stop_reason}",
                }
                yield f"data: {json.dumps(error_msg)}\n\n"
                break

    except Exception as e:
        error_msg = {"type": "error", "text": str(e)}
        yield f"data: {json.dumps(error_msg)}\n\n"

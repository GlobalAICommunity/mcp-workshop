"""Module 3, part B — STARTER FILE. Write the agent loop yourself.

Follow docs/03-raw-client.md. Solution: src/solution/agent_raw.py

Run:

    .venv/bin/python src/starter/agent_raw.py "What is the weather in Tokyo?"
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp import Client

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp_client import server_transport  # noqa: E402
from model_config import describe, get_openai_client  # noqa: E402

MAX_TURNS = 6

SYSTEM_PROMPT = (
    "You are a concise travel assistant. Use the provided tools to answer "
    "questions about weather and flights. Only the cities returned by "
    "list_destinations are supported. When you have enough information, answer "
    "in plain prose — do not describe the tool calls you made."
)


def mcp_tools_to_openai(tools) -> list[dict]:
    """Translate MCP tool definitions into OpenAI `tools` entries.

    Each entry looks like:
        {"type": "function",
         "function": {"name": ..., "description": ..., "parameters": <json schema>}}
    """
    # TODO 1: Build and return that list from the MCP tools.
    #         Careful: the attribute is `tool.input_schema` (snake_case) in
    #         SDK v2 — it was `inputSchema` in v1.
    return []


async def run(question: str) -> str:
    llm, model_name = get_openai_client()

    async with Client(server_transport()) as mcp:
        listing = await mcp.list_tools()
        tools = mcp_tools_to_openai(listing.tools)

        messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]

        for _turn in range(MAX_TURNS):
            response = await llm.chat.completions.create(
                model=model_name,
                messages=messages,
                tools=tools,
            )
            reply = response.choices[0].message

            # TODO 2: Append the assistant's reply to `messages`, including any
            #         tool_calls it made. If you drop the tool_calls the model
            #         forgets what it asked for and will loop forever.

            # TODO 3: If there are no tool calls, we are done — return the text.

            # TODO 4: For each tool call: parse the JSON arguments, run it with
            #         `await mcp.call_tool(name, args)`, and append a message
            #         with role "tool", the matching `tool_call_id`, and the
            #         text content of the result.
            #
            #         Bonus: small models sometimes emit invalid JSON. Catch
            #         json.JSONDecodeError and feed the error back as the tool
            #         result instead of crashing.
            raise NotImplementedError("Finish TODOs 2-4")

        return "Gave up after too many tool-calling turns."


async def main() -> None:
    question = " ".join(sys.argv[1:]) or "What is the weather in Amsterdam?"
    print(f"[{describe()}]")
    print(f"Q: {question}\n")
    answer = await run(question)
    print(f"\nA: {answer}")


if __name__ == "__main__":
    asyncio.run(main())

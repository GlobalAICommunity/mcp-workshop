"""Module 3, part B — a complete agent loop, written by hand.

This is the whole trick behind every "AI agent" framework, in about forty lines:

    1. Ask the MCP server what tools exist.
    2. Translate those tool schemas into the shape the model API expects.
    3. Send the conversation plus the tool list to the model.
    4. If the model asked for tools, run them through MCP and append the results.
    5. Go back to step 3. If it did not, you have your answer.

Every provider this workshop supports speaks the OpenAI Chat Completions API, so
this same file works against Ollama, Google, Grok and Microsoft Foundry — the
only thing that changes is `.env`.

Run it:

    .venv/bin/python src/solution/agent_raw.py "What should I pack for Tokyo?"
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

    This is the only real 'glue' in the whole loop. Note `input_schema` is
    snake_case: that is an SDK v2 change, it was `inputSchema` in v1. The JSON on
    the wire is still camelCase.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.input_schema,
            },
        }
        for tool in tools
    ]


async def run(question: str) -> str:
    llm, model_name = get_openai_client()

    async with Client(server_transport()) as mcp:
        listing = await mcp.list_tools()
        tools = mcp_tools_to_openai(listing.tools)

        messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]

        for turn in range(MAX_TURNS):
            response = await llm.chat.completions.create(
                model=model_name,
                messages=messages,
                tools=tools,
            )
            reply = response.choices[0].message

            # Keep the assistant turn in the transcript verbatim, including any
            # tool calls, or the model loses track of what it just asked for.
            messages.append(
                {
                    "role": "assistant",
                    "content": reply.content or "",
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": "function",
                            "function": {
                                "name": call.function.name,
                                "arguments": call.function.arguments,
                            },
                        }
                        for call in (reply.tool_calls or [])
                    ],
                }
            )

            if not reply.tool_calls:
                return reply.content or "(no answer)"

            for call in reply.tool_calls:
                name = call.function.name
                try:
                    args = json.loads(call.function.arguments or "{}")
                except json.JSONDecodeError:
                    # Small models occasionally emit malformed JSON. Tell the
                    # model instead of crashing, and let it try again.
                    args = None

                if args is None:
                    output = "Error: arguments were not valid JSON. Try again."
                else:
                    print(f"  -> calling {name}({args})")
                    result = await mcp.call_tool(name, args)
                    output = "\n".join(
                        block.text for block in result.content if hasattr(block, "text")
                    )

                messages.append(
                    {"role": "tool", "tool_call_id": call.id, "content": output}
                )

        return "Gave up after too many tool-calling turns."


async def main() -> None:
    question = " ".join(sys.argv[1:]) or "What is the weather in Amsterdam?"
    print(f"[{describe()}]")
    print(f"Q: {question}\n")
    answer = await run(question)
    print(f"\nA: {answer}")


if __name__ == "__main__":
    asyncio.run(main())

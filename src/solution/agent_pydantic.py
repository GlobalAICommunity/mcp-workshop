"""Module 4 — the same agent as module 3, using Pydantic AI.

Compare this file with `agent_raw.py`. The loop, the schema translation, the
transcript bookkeeping and the retry handling are all still happening — you just
are not the one writing them any more.

One detail worth noticing: this runs in a *different virtualenv* from the server.
Pydantic AI talks MCP through FastMCP, which currently pins `mcp<2`, while our
server uses the official `mcp` 2.0 SDK. They cannot share an environment — and
they do not need to, because they are separate processes talking a protocol.
That is the entire point of MCP, demonstrated by accident.

Run it:

    .venv-agent/bin/python src/solution/agent_pydantic.py "What should I pack for Tokyo?"
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from fastmcp.client.transports import StdioTransport
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from model_config import describe, get_pydantic_model  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVER = REPO_ROOT / "src" / "solution" / "travel_server.py"
SERVER_PYTHON = REPO_ROOT / ".venv" / "bin" / "python"

INSTRUCTIONS = (
    "You are a concise travel assistant. Use the provided tools to answer "
    "questions about weather and flights. Only the cities returned by "
    "list_destinations are supported."
)


def build_agent() -> Agent:
    """Wire the MCP server up as a toolset on a Pydantic AI agent."""
    toolset = MCPToolset(
        StdioTransport(
            command=str(SERVER_PYTHON if SERVER_PYTHON.exists() else sys.executable),
            args=[str(SERVER)],
        )
    )
    return Agent(get_pydantic_model(), instructions=INSTRUCTIONS, toolsets=[toolset])


async def main() -> None:
    question = " ".join(sys.argv[1:]) or "What is the weather in Amsterdam?"
    print(f"[{describe()}]")
    print(f"Q: {question}\n")

    agent = build_agent()
    async with agent:
        result = await agent.run(question)

    for message in result.all_messages():
        for part in message.parts:
            if part.part_kind == "tool-call":
                print(f"  -> called {part.tool_name}({part.args})")

    print(f"\nA: {result.output}")


if __name__ == "__main__":
    asyncio.run(main())

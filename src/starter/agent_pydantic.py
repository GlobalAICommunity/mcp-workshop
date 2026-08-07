"""Module 4 — STARTER FILE. The same agent, using Pydantic AI.

Follow docs/04-pydantic-ai.md. Solution: src/solution/agent_pydantic.py

Note this one runs in the *agent* virtualenv:

    .venv-agent/bin/python src/starter/agent_pydantic.py "Plan a trip to Tokyo"
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
SERVER = REPO_ROOT / "src" / "starter" / "travel_server.py"
# The server runs in the *other* virtualenv, which has the official mcp 2.0 SDK.
SERVER_PYTHON = REPO_ROOT / ".venv" / "bin" / "python"

INSTRUCTIONS = (
    "You are a concise travel assistant. Use the provided tools to answer "
    "questions about weather and flights. Only the cities returned by "
    "list_destinations are supported."
)


def build_agent() -> Agent:
    """Wire the MCP server up as a toolset on a Pydantic AI agent."""
    # TODO 1: Build an MCPToolset around a StdioTransport that launches the
    #         server with SERVER_PYTHON and SERVER.
    toolset = ...

    # TODO 2: Return an Agent using get_pydantic_model(), the INSTRUCTIONS
    #         above, and toolsets=[toolset].
    ...


async def main() -> None:
    question = " ".join(sys.argv[1:]) or "What is the weather in Amsterdam?"
    print(f"[{describe()}]")
    print(f"Q: {question}\n")

    agent = build_agent()
    async with agent:
        result = await agent.run(question)

    # TODO 3: Print the tool calls the model made, so you can compare them with
    #         what your hand-written loop did in module 3.
    #         Hint: iterate result.all_messages(), then message.parts, and look
    #         for parts where part.part_kind == "tool-call".

    print(f"\nA: {result.output}")


if __name__ == "__main__":
    asyncio.run(main())

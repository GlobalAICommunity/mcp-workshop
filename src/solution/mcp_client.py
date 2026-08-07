"""Module 3, part A — talk to the MCP server with no LLM involved.

Before adding a model to the picture, it is worth seeing that an MCP client is a
completely ordinary program: it starts the server, asks what it can do, and calls
things. No intelligence required.

This uses the `Client` class from the official SDK v2. In v1 this took three
nested layers (a transport context manager, a `ClientSession` wrapped around it,
and a manual `await session.initialize()`); v2 collapses that into one object.

Run it:

    .venv/bin/python src/solution/mcp_client.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters, stdio_client

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVER = REPO_ROOT / "src" / "solution" / "travel_server.py"


def server_transport():
    """Launch our travel server as a subprocess and talk to it over stdio."""
    return stdio_client(
        StdioServerParameters(command=sys.executable, args=[str(SERVER)])
    )


async def main() -> None:
    async with Client(server_transport()) as client:
        print(f"Connected. Protocol revision: {client.protocol_version}\n")

        # 1. Discover what the server offers.
        listing = await client.list_tools()
        print("Tools:")
        for tool in listing.tools:
            print(f"  - {tool.name}: {tool.description}")
        print()

        # 2. Call a tool. Arguments are a plain dict matching its input schema.
        weather = await client.call_tool("get_weather", {"city": "Amsterdam"})
        print("get_weather('Amsterdam')")
        print("  structured:", weather.structured_content)
        print("  text      :", weather.content[0].text)
        print()

        # 3. Tool failures come back as a result with is_error set, not as an
        #    exception. That is deliberate: the model is meant to read the error
        #    and try again.
        oops = await client.call_tool("get_weather", {"city": "Atlantis"})
        print("get_weather('Atlantis')")
        print("  is_error:", oops.is_error)
        print("  text    :", oops.content[0].text)
        print()

        # 4. Resources are application-controlled context, not model-called tools.
        resources = await client.list_resources()
        print("Resources:", [str(r.uri) for r in resources.resources])
        catalog = await client.read_resource("travel://destinations")
        print(catalog.contents[0].text)
        print()

        # 5. Prompts are user-selected, reusable workflows.
        prompts = await client.list_prompts()
        print("Prompts:", [p.name for p in prompts.prompts])
        prompt = await client.get_prompt("plan_a_trip", {"city": "Tokyo", "nights": "4"})
        print(json.dumps(prompt.messages[0].content.text, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

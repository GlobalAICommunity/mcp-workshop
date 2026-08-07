"""Module 3, part A — STARTER FILE. Talk to the MCP server with no LLM.

Follow docs/03-raw-client.md. Solution: src/solution/mcp_client.py

Run:

    .venv/bin/python src/starter/mcp_client.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters, stdio_client

REPO_ROOT = Path(__file__).resolve().parents[2]
# Point this at your own server. Swap to src/solution/travel_server.py if your
# starter server is not finished yet.
SERVER = REPO_ROOT / "src" / "starter" / "travel_server.py"


def server_transport():
    """Launch the travel server as a subprocess and talk to it over stdio."""
    return stdio_client(
        StdioServerParameters(command=sys.executable, args=[str(SERVER)])
    )


async def main() -> None:
    async with Client(server_transport()) as client:
        print(f"Connected. Protocol revision: {client.protocol_version}\n")

        # TODO 1: List the tools and print each name + description.
        #         Hint: (await client.list_tools()).tools

        # TODO 2: Call get_weather for a city and print `.structured_content`.
        #         Hint: await client.call_tool("get_weather", {"city": "Amsterdam"})

        # TODO 3: Call get_weather with a city that does not exist.
        #         Look at `.is_error` — note it is a *result*, not an exception.

        # TODO 4: Read the "travel://destinations" resource and print it.
        #         Hint: await client.read_resource(...) then .contents[0].text

        # TODO 5: Fetch the "plan_a_trip" prompt and print the message text.
        #         Hint: await client.get_prompt("plan_a_trip", {"city": "Tokyo"})
        ...


if __name__ == "__main__":
    asyncio.run(main())

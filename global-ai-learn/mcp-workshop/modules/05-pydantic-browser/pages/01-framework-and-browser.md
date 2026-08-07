---
id: framework-and-browser
title: Move from a raw loop to a browser app
order: 1
estimatedMinutes: 30
---

You will create the framework agent and web application from empty files. This
module uses `.venv-agent`, while the server you built still runs through `.venv`.

## Part 1, step 1: Create the Pydantic AI file

Start clean:

```bash
mkdir -p src/starter
: > src/starter/agent_pydantic.py
```

Add imports and paths:

```python
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from fastmcp.client.transports import StdioTransport
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from model_config import describe, get_pydantic_model

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVER = Path(__file__).with_name("travel_server.py")
SERVER_PYTHON = REPO_ROOT / ".venv" / "bin" / "python"

INSTRUCTIONS = (
    "You are a concise travel assistant. Use the available tools for weather "
    "and flight questions. Use list_destinations when a city is uncertain."
)
```

The client and server deliberately use different environments. They do not need
the same SDK package because they communicate through MCP.

## Part 1, step 2: Build the agent

Append the factory function:

```python
def build_agent() -> Agent:
    toolset = MCPToolset(
        StdioTransport(
            command=str(SERVER_PYTHON),
            args=[str(SERVER)],
        )
    )
    return Agent(
        get_pydantic_model(),
        instructions=INSTRUCTIONS,
        toolsets=[toolset],
    )
```

`MCPToolset` performs the schema conversion and tool execution that you wrote by
hand in the previous module.

## Part 1, step 3: Add a command-line program

Append the runnable portion:

```python
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
```

Compile and run the file you wrote:

```bash
.venv-agent/bin/python -m py_compile src/starter/agent_pydantic.py
.venv-agent/bin/python src/starter/agent_pydantic.py \
  "What should I pack for a trip to Tokyo?"
```

The result should match the raw agent's behavior with much less application
code. The framework now owns the loop, message bookkeeping, retries, and tool id
matching. You can still inspect every tool call.

## Part 2, step 1: Create the browser file

Start the web application from an empty file:

```bash
: > src/starter/web.py
```

Add imports, locate the offline assets, and construct the application:

```python
from __future__ import annotations

import sys
from pathlib import Path

from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_pydantic import build_agent

REPO_ROOT = Path(__file__).resolve().parents[2]
CACHED_UI = REPO_ROOT / "vendor" / "pydantic-ai-ui.html"
ASSET_DIR = REPO_ROOT / "vendor" / "assets"

agent = build_agent()

if CACHED_UI.exists():
    app = agent.to_web(html_source=str(CACHED_UI))
    if ASSET_DIR.is_dir():
        app.routes.insert(
            0,
            Mount("/static", app=StaticFiles(directory=str(ASSET_DIR))),
        )
else:
    app = agent.to_web()
```

The downloaded HTML still references JavaScript and CSS assets. The static mount
must be inserted first because the chat UI's `/{id}` route would otherwise claim
requests under `/static/`.

## Part 2, step 2: Launch your application

Compile the file, then tell Uvicorn to import `web` from your starter directory:

```bash
.venv-agent/bin/python -m py_compile src/starter/web.py
.venv-agent/bin/uvicorn --app-dir src/starter web:app --port 7932
```

Open `http://127.0.0.1:7932` and ask a question that requires multiple tools.
Tool calls appear in the message thread while the model works.

You can switch providers without changing either file:

```bash
MCP_WORKSHOP_PROVIDER=google .venv-agent/bin/python \
  src/starter/agent_pydantic.py "Weather in Tokyo?"
```

For tools that delete, send, pay, deploy, or otherwise have irreversible effects,
require explicit human approval before execution.
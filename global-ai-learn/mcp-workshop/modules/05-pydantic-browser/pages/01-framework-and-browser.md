---
id: framework-and-browser
title: Move from a raw loop to a browser app
order: 1
estimatedMinutes: 25
---

Work in `src/starter/agent_pydantic.py` and `src/starter/web.py`. This module uses
the `.venv-agent` environment because Pydantic AI reaches MCP through FastMCP.

## Build the framework agent

The framework version keeps the model, instructions, and MCP toolset visible
while hiding loop bookkeeping:

```python
from fastmcp.client.transports import StdioTransport
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

toolset = MCPToolset(StdioTransport(command=SERVER_PYTHON, args=[SERVER]))
agent = Agent(get_pydantic_model(), instructions=INSTRUCTIONS, toolsets=[toolset])

async with agent:
    result = await agent.run("What should I pack for Tokyo?")

print(result.output)
```

Run it with:

```bash
make pydantic Q="What should I pack for a trip to Tokyo?"
```

Compared with the raw loop, `MCPToolset` now converts schemas, runs the turn
loop, preserves assistant messages, matches tool call ids, and handles malformed
arguments. Frameworks also provide features such as retries, streaming, typed
outputs, usage tracking, and tracing.

Use a framework when those capabilities matter enough to justify the dependency.
A small custom loop remains reasonable when you need minimal dependencies and
complete control. Understanding the raw loop lets you diagnose whether a failure
comes from the model, a tool description, or the framework.

## Observe protocol interoperability

The client and server use separate environments and incompatible SDK versions:

| Side | Environment | MCP implementation |
|---|---|---|
| Server | `.venv` | Official `mcp` 2.0 |
| Client | `.venv-agent` | FastMCP with `mcp` 1.x |

They still communicate because the protocol is their shared contract. You can
also change model providers without modifying the server:

```bash
MCP_WORKSHOP_PROVIDER=google make pydantic Q="Weather in Tokyo?"
```

## Put the agent in a browser

Pydantic AI can expose the agent as a chat application:

```python
from agent_pydantic import build_agent

agent = build_agent()
app = agent.to_web()
```

Run `make web`, open `http://127.0.0.1:7932`, and ask a question that needs
several tools. Tool calls appear in the conversation while the model works.

## Keep the UI offline

The repository vendors the UI assets so the demonstration does not depend on a
CDN. Point the web app at the cached HTML and mount rewritten assets before the
UI's catch-all route:

```python
app = agent.to_web(html_source=str(CACHED_UI))
app.routes.insert(0, Mount("/static", app=StaticFiles(directory=str(ASSET_DIR))))
```

Route order matters because the UI route `/{id}` would otherwise capture
requests for `/static/...`.

For tools that delete, send, pay, deploy, or otherwise have irreversible effects,
require explicit human approval. The browser UI can present approve and reject
controls before such a tool runs.
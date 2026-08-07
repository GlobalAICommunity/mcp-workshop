# Cheatsheet

One page. Written against MCP `2026-07-28` / Python SDK `mcp` 2.0.

---

## Commands

```bash
make setup                          # create both venvs + vendor the web UI
make check                          # verify this machine is ready
make server                         # run the MCP server over stdio
make client                         # module 3a — client, no LLM
make agent Q="..."                  # module 3b — the hand-written loop
make pydantic Q="..."               # module 4  — Pydantic AI
make web                            # module 4  — browser UI on :7932
make inspector                      # MCP Inspector (needs Node 22.19+)
make jsonrpc METHOD=tools/list      # raw JSON-RPC

./scripts/raw_jsonrpc.sh tools/call '{"name":"get_weather","arguments":{"city":"Tokyo"}}'
```

Two virtualenvs: **`.venv`** = server + raw client (`mcp` 2.0) ·
**`.venv-agent`** = Pydantic AI + web UI (FastMCP, `mcp` 1.x).

---

## Server

```python
from typing import Annotated, Literal
from mcp.server import MCPServer
from pydantic import BaseModel, Field

mcp = MCPServer("travel", instructions="What this server is for.")

class Weather(BaseModel):                       # -> outputSchema
    city: str
    temperature_c: int = Field(description="Degrees Celsius.")

@mcp.tool()                                     # model-controlled
def get_weather(
    city: Annotated[str, Field(description='City name, e.g. "Tokyo".')],
    days: Annotated[int, Field(ge=1, le=7)] = 3,
    units: Literal["celsius", "fahrenheit"] = "celsius",
) -> Weather:
    """Description the model reads when choosing this tool."""
    raise ValueError("Readable message")        # -> isError result, not a crash

@mcp.resource("travel://destinations")          # app-controlled
def catalog() -> str: ...

@mcp.prompt()                                   # user-controlled
def plan_a_trip(city: str, nights: int = 3) -> str: ...

mcp.run(transport="stdio")                      # or "streamable-http"
```

Docstring `Args:` sections do **not** become parameter descriptions — use
`Annotated[..., Field(description=...)]`.

## Client

```python
from mcp import Client, StdioServerParameters, stdio_client

async with Client(stdio_client(StdioServerParameters(command=..., args=[...]))) as c:
    c.protocol_version                          # "2026-07-28"
    tools = (await c.list_tools()).tools
    r = await c.call_tool("get_weather", {"city": "Tokyo"})
    r.structured_content                        # typed dict
    r.content[0].text                           # text block
    r.is_error                                  # errors are results
    await c.read_resource("travel://destinations")
    await c.get_prompt("plan_a_trip", {"city": "Tokyo", "nights": "4"})
```

## MCP tools → OpenAI tools

```python
[{"type": "function",
  "function": {"name": t.name,
               "description": t.description or "",
               "parameters": t.input_schema}}   # snake_case in v2
 for t in tools]
```

## Pydantic AI

```python
from fastmcp.client.transports import StdioTransport
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

agent = Agent(model, instructions=..., toolsets=[MCPToolset(StdioTransport(...))])
async with agent:
    result = await agent.run("...")
result.output
[p for m in result.all_messages() for p in m.parts if p.part_kind == "tool-call"]

app = agent.to_web(html_source=CACHED_UI)       # browser chat UI
```

---

## v1 → v2

| v1 | v2 |
|---|---|
| `from mcp.server.fastmcp import FastMCP` | `from mcp.server import MCPServer` |
| `stdio_client` + `ClientSession` + `initialize()` | `Client(...)` |
| `tool.inputSchema` / `result.isError` | `tool.input_schema` / `result.is_error` |
| `initialize` handshake | none — `_meta` on every request |
| server → client `sampling` / `roots` | MRTR (`resultType: "input_required"`) |
| HTTP+SSE transport | Streamable HTTP |

## Raw JSON-RPC envelope

```json
{"jsonrpc": "2.0", "id": 1, "method": "tools/list",
 "params": {"_meta": {
   "io.modelcontextprotocol/protocolVersion": "2026-07-28",
   "io.modelcontextprotocol/clientCapabilities": {}
 }}}
```

Methods: `server/discover` · `tools/list` · `tools/call` · `resources/list` ·
`resources/read` · `prompts/list` · `prompts/get`

## Primitives

| | Controlled by | Like |
|---|---|---|
| Tools | the model | POST |
| Resources | the application | GET |
| Prompts | the user | a slash command |

# 02 — Build a server

*~30 minutes. This is the hands-on core of the workshop.*

You are going to build a fake travel service: weather, forecasts and flights.
Fake, because the point is MCP, not calling a weather API — and because it works
with the wifi off and gives the same answer every time you demo it.

- **Work in**: `src/starter/travel_server.py` (follow the numbered `TODO`s)
- **Stuck?**: `src/solution/travel_server.py` is the finished version

---

## Step 1 — A server object

```python
from mcp.server import MCPServer

mcp = MCPServer(
    "travel",
    instructions="A fake travel assistant backend. Use get_weather for ...",
)

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

`instructions` is not decoration — it is sent to the client and ends up in the
model's context. It is your chance to explain what this server is for.

> **Note the import.** In SDK v1 this was `from mcp.server.fastmcp import FastMCP`.
> In v2 it is `MCPServer`, and the old path was removed rather than deprecated.

## Step 2 — Your first tool

```python
@mcp.tool()
def get_weather(city: str) -> str:
    """Get today's weather for a city."""
    ...
```

That decorator does a surprising amount:

- the **function name** becomes the tool name,
- the **docstring** becomes the description the model reads,
- the **type hints** become the JSON Schema for the arguments.

Check it with `./scripts/raw_jsonrpc.sh tools/list`.

### Descriptions matter more than you think

The model chooses tools based *entirely* on these strings. Vague descriptions
produce a model that guesses.

One trap worth knowing: a `Args:` section in your docstring does **not** become
per-parameter descriptions in `mcp` 2.0. Use `Annotated` instead:

```python
from typing import Annotated
from pydantic import Field

@mcp.tool()
def get_weather(
    city: Annotated[str, Field(description='City name, e.g. "Amsterdam".')],
) -> Weather:
```

## Step 3 — Structured output

Return a Pydantic model and you get an `outputSchema` and machine-readable
`structuredContent` alongside the text:

```python
class Weather(BaseModel):
    city: str
    temperature_c: int = Field(description="Temperature in degrees Celsius.")
    condition: str
    humidity_pct: int = Field(ge=0, le=100)
```

The client now gets real typed data, not a string it has to parse. Call it and
look at both `content` and `structuredContent` in the response.

## Step 4 — Validation and constraints

```python
days: Annotated[int, Field(ge=1, le=7, description="Days ahead to forecast.")] = 3,
units: Annotated[Literal["celsius", "fahrenheit"], Field(...)] = "celsius",
```

`ge`/`le` become `minimum`/`maximum` in the schema, and `Literal` becomes an
`enum`. The model reads all of it, so constraints reduce bad calls — and defaults
mean the model can ignore arguments it does not care about.

## Step 5 — A tool worth chaining

```python
@mcp.tool()
def search_flights(origin: str, destination: str, max_results: int = 3) -> list[Flight]:
```

Two required arguments and a different domain. This is the one that makes module
3 interesting, because "what should I pack for Tokyo and how do I get there"
forces the model to make *several* calls and combine them.

## Step 6 — Errors are results, not crashes

```python
raise ValueError(f"Unknown city {city!r}. Known cities are: {known}.")
```

The SDK turns that into a normal response with `isError: true` and your message
in the content. It does **not** propagate as an exception into the client.

That is deliberate: the error is *for the model*. A good message ("known cities
are: ...") lets it correct itself on the next turn. Try
`get_weather('Atlantis')` and watch it recover in module 3.

## Step 7 — A resource

```python
@mcp.resource("travel://destinations")
def destinations_catalog() -> str:
    """The full destination catalogue as human-readable text."""
```

Resources are **application-controlled**: the host decides to include them, the
model does not call them. Reference data, file contents, a schema dump.

## Step 8 — A prompt

```python
@mcp.prompt()
def plan_a_trip(city: str, nights: int = 3) -> str:
    """Draft a short trip plan for a city."""
```

Prompts are **user-controlled** — they show up as slash commands or menu items in
a host like VS Code. This is how you ship an expert workflow rather than making
each user reinvent the prompt.

---

## Try it out

```bash
make jsonrpc METHOD=tools/list
```

### With the MCP Inspector *(optional, needs Node 22.19+)*

```bash
make inspector
```

A browser UI for poking at your server: browse tools, fill in arguments, see raw
protocol traffic. Genuinely the fastest way to debug a server. Skip it if you are
offline — nothing later depends on it.

### In VS Code Copilot *(bonus)*

`.vscode/mcp.json` is already wired up:

```json
{
  "servers": {
    "travel": {
      "type": "stdio",
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["${workspaceFolder}/src/solution/travel_server.py"]
    }
  }
}
```

Open Copilot in agent mode and ask it about the weather in Tokyo. Your server,
in a real host, with a frontier model driving it.

---

## Checkpoint

You should have 4 tools, 1 resource and 1 prompt, and `make check` should say
`MCP server — 4 tools, protocol 2026-07-28`.

Next: [03 — A client, and an agent loop](03-raw-client.md)

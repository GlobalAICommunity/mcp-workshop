---
id: server-capabilities
title: Tools, resources, prompts, and errors
order: 1
estimatedMinutes: 30
---

Work in `src/starter/travel_server.py` and follow its numbered TODOs. You can
compare your work with `src/solution/travel_server.py` when needed.

## Create the server

Start with an MCP server that uses stdio:

```python
from mcp.server import MCPServer

mcp = MCPServer(
    "travel",
    instructions=(
        "A fake travel assistant backend. Use the weather and flight tools "
        "to answer travel questions."
    ),
)

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

The server instructions help clients and models understand the server as a
whole. `stdio` means the server waits for JSON-RPC over stdin and writes protocol
responses to stdout. A silent server after `make server` is working as expected.

## Define a typed tool

Decorate a regular Python function:

```python
@mcp.tool()
def get_weather(city: str) -> str:
    """Get today's weather for a city."""
    ...
```

The function name becomes the tool name, the docstring becomes the description,
and type hints become JSON Schema. Inspect the generated schema:

```bash
./scripts/raw_jsonrpc.sh tools/list
```

Descriptions affect model behavior. Explain when to call the tool, its limits,
and how to recover when input is uncertain. For parameter descriptions, use
`Annotated` with Pydantic `Field`; an `Args:` docstring section does not create
parameter descriptions in `mcp` 2.0.

```python
city: Annotated[str, Field(description='City name, e.g. "Amsterdam".')]
```

## Return structured output

Replace the string result with a Pydantic model:

```python
class Weather(BaseModel):
    """Current weather for a city."""

    city: str
    temperature_c: int = Field(description="Temperature in degrees Celsius.")
    condition: str = Field(description="Short human-readable sky condition.")
    humidity_pct: int = Field(ge=0, le=100)
```

The SDK now publishes an `outputSchema` and returns `structuredContent` alongside
text. Dashboards, tests, and workflows can consume that structure without parsing
model-facing prose.

Use constraints and defaults to guide calls:

```python
days: Annotated[int, Field(ge=1, le=7)] = 3
units: Literal["celsius", "fahrenheit"] = "celsius"
```

Constraints reduce invalid requests, while defaults let the model omit details
that do not matter. Still validate inputs in the function because schema guidance
is not authorization or a complete trust boundary.

## Make errors recoverable

The SDK converts tool exceptions into results with `isError: true`. Write errors
for the model that receives them:

```python
raise ValueError(f"Unknown city {city!r}. Known cities are: {known}.")
```

This message gives the model enough information to correct the call. A generic
`City not found` message creates a dead end.

## Add a resource and prompt

Expose application-controlled reference data as a resource:

```python
@mcp.resource("travel://destinations")
def destinations_catalog() -> str:
    """The full destination catalogue as human-readable text."""
    ...
```

Expose a user-controlled workflow as a prompt:

```python
@mcp.prompt()
def plan_a_trip(city: str, nights: int = 3) -> str:
    """Draft a short trip plan for a city."""
    return f"Check weather and flights, then plan {nights} nights in {city}."
```

Prompts package expert sequencing so users do not need to reconstruct the right
workflow each time.

## Check the server

Call a tool directly and run the repository checks:

```bash
./scripts/raw_jsonrpc.sh tools/call '{"name":"search_flights","arguments":{"origin":"Amsterdam","destination":"Tokyo"}}'
make check
```

Your finished server should expose four tools, one resource, and one prompt.
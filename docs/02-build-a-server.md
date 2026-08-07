# 02 — Build a server

*~30 minutes. This is the hands-on core of the workshop.*

You are going to build a fake travel service: weather, forecasts and flights.

**Fake on purpose.** Real APIs mean signups, keys, rate limits and one attendee
whose corporate proxy blocks the domain — none of which teaches you anything about
MCP. The data here is generated deterministically from a hash of the city name and
today's date, so it needs no network, and the same question always gives the same
answer. That last property matters more than it sounds: it means you can rehearse
a demo and trust it.

(It also means the weather is often nonsense. Reykjavik at 22°C is normal. This is
fine — it keeps attention on the protocol.)

- **Work in**: `src/starter/travel_server.py` (follow the numbered `TODO`s)
- **Stuck or behind?**: `src/solution/travel_server.py` is the finished version,
  and using it is completely fine

---

## Step 1 — A server object

```python
from mcp.server import MCPServer

mcp = MCPServer(
    "travel",
    instructions=(
        "A fake travel assistant backend. Use get_weather and get_forecast for "
        "weather questions, search_flights to find flights between two cities, "
        "and list_destinations to see which cities are supported."
    ),
)

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Two things here are more significant than they look.

**`instructions` is not decoration.** It is sent to the client and typically ends
up in the model's context. It is your one chance to explain, at the server level,
what this thing is for and when to reach for it. Servers that skip it are harder
for models to use well.

**`transport="stdio"`** means this server is launched as a subprocess and talks
over stdin/stdout. Change one string to `"streamable-http"` and the same server is
a web service — the tool code does not change at all. That separation is the point
of a transport layer.

> **Note the import.** In SDK v1 this was `from mcp.server.fastmcp import FastMCP`.
> In v2 it is `MCPServer`, and the old path was removed rather than deprecated. If
> you find a tutorial using `FastMCP` from `mcp.server.fastmcp`, it predates the
> current SDK.

Run it now: `make server`. It will sit there silently, because it is waiting for
JSON-RPC on stdin. That is correct, and it is the first thing everyone worries
about.

## Step 2 — Your first tool

```python
@mcp.tool()
def get_weather(city: str) -> str:
    """Get today's weather for a city."""
    ...
```

That decorator does a surprising amount of work:

- the **function name** becomes the tool name,
- the **docstring** becomes the description the model reads,
- the **type hints** become the JSON Schema for the arguments.

Check what you produced:

```bash
./scripts/raw_jsonrpc.sh tools/list
```

Look at the `inputSchema` in that output. **You did not write it — your type hints
became it.** And that schema is handed verbatim to the model. This is the moment
the whole thing tends to click.

### Descriptions are behaviour, not documentation

The model chooses which tool to call based *entirely* on the name and description.
Not on your implementation, not on your intentions. Vague descriptions produce a
model that guesses, and a model that guesses looks like a broken product.

Compare:

```python
"""Gets data."""                                    # useless
"""Get today's weather for a city."""               # fine
"""Get today's weather for a city. Only supported
   destinations work — call list_destinations first
   if unsure."""                                    # actively helpful
```

The third one tells the model how to recover from its own mistakes. That is worth
more than most prompt engineering.

**A trap worth knowing**: an `Args:` section in your docstring does **not** become
per-parameter descriptions in `mcp` 2.0. Many people assume it does. Use
`Annotated` instead:

```python
from typing import Annotated
from pydantic import Field

@mcp.tool()
def get_weather(
    city: Annotated[str, Field(description='City name, e.g. "Amsterdam".')],
) -> Weather:
```

The `e.g.` matters. Models are much better at formatting arguments correctly when
shown an example.

## Step 3 — Structured output

Return a Pydantic model instead of a string:

```python
class Weather(BaseModel):
    """Current weather for a city."""

    city: str
    temperature_c: int = Field(description="Temperature in degrees Celsius.")
    condition: str = Field(description="Short human-readable sky condition.")
    humidity_pct: int = Field(ge=0, le=100)
```

Now you get an `outputSchema`, and results carry machine-readable
`structuredContent` alongside the text. Call the tool and look at both.

Why bother, when the model reads text anyway? Because **not every consumer is a
model**. A dashboard, a test, a workflow step or another program can use the
structured form without parsing prose. Returning a bare string throws that away
for no benefit.

## Step 4 — Validation and constraints

```python
days: Annotated[int, Field(ge=1, le=7, description="Days ahead to forecast.")] = 3,
units: Annotated[
    Literal["celsius", "fahrenheit"], Field(description="Temperature units.")
] = "celsius",
```

`ge`/`le` become `minimum`/`maximum` in the schema. `Literal` becomes an `enum`.
The model reads all of it.

Two benefits, and the second is the interesting one:

1. **Constraints reduce bad calls.** A model that can see `maximum: 7` mostly does
   not ask for 30 days.
2. **Defaults let the model ignore what it does not care about.** With
   `days: int = 3`, "what's the weather like in Tokyo this week" works without the
   model having to reason about a parameter it has no opinion on. Every required
   argument is one more thing that can go wrong.

Validate anyway, in the body. Schemas guide the model; they do not bind it.

## Step 5 — A tool worth chaining

```python
@mcp.tool()
def search_flights(
    origin: Annotated[str, Field(description='City to depart from.')],
    destination: Annotated[str, Field(description='City to fly to.')],
    max_results: Annotated[int, Field(ge=1, le=5)] = 3,
) -> list[Flight]:
```

Two required arguments, and a completely different domain from weather.

This is the tool that makes module 3 interesting. A question like *"find me a
flight to Barcelona and tell me if I need a coat"* cannot be answered with one
call — the model has to pick two different tools, call both, and combine the
results. That is the difference between a lookup and an agent, and you want to be
able to demo it.

## Step 6 — Errors are results, not crashes

```python
raise ValueError(f"Unknown city {city!r}. Known cities are: {known}.")
```

The SDK turns that into a normal response with `isError: true` and your message in
the content. It does **not** propagate as an exception into the client.

This surprises people, and it is deliberate: **the error message is for the model,
not for a human operator.** A model that receives "Unknown city 'Atlantis'. Known
cities are: amsterdam, barcelona, ..." can correct itself on the very next turn.
One that receives `KeyError` cannot.

So write error messages the way you would write a hint:

```python
raise ValueError("City not found")                      # dead end
raise ValueError(f"Unknown city {city!r}. Known cities are: {known}.")  # recoverable
```

You will watch this pay off in module 3, where asking for the weather in Atlantis
causes the model to go and look up the valid list by itself.

## Step 7 — A resource

```python
@mcp.resource("travel://destinations")
def destinations_catalog() -> str:
    """The full destination catalogue as human-readable text."""
```

Resources are **application-controlled**: the host decides to include them; the
model does not call them. Reference data, file contents, a schema dump — things
that inform the model rather than actions it takes.

The URI scheme is yours to choose. `travel://destinations` is arbitrary; use
whatever is meaningful.

If you catch yourself wanting the model to fetch a resource on demand, what you
actually want is a tool. That is the whole distinction.

## Step 8 — A prompt

```python
@mcp.prompt()
def plan_a_trip(city: str, nights: int = 3) -> str:
    """Draft a short trip plan for a city."""
    return (
        f"Plan a {nights}-night trip to {city}.\n\n"
        "Steps:\n"
        f"1. Check the weather forecast for {city}.\n"
        f"2. Find flights from Amsterdam to {city}.\n"
        "3. Recommend what to pack, and suggest an itinerary.\n"
    )
```

Prompts are **user-controlled** — they surface as slash commands or menu items in a
host like VS Code.

This is the most underused primitive in MCP. It is how you ship *expertise*: you
know the right way to sequence your tools, so encode it once instead of hoping
each user works it out. Notice this prompt does not just ask a question — it
prescribes the steps.

---

## Try it out

```bash
make jsonrpc METHOD=tools/list
./scripts/raw_jsonrpc.sh tools/call '{"name":"search_flights","arguments":{"origin":"Amsterdam","destination":"Tokyo"}}'
```

### With the MCP Inspector *(optional, needs Node 22.19+)*

```bash
make inspector
```

A browser UI for poking at your server: browse tools, fill in arguments, watch raw
protocol traffic. Genuinely the fastest way to debug a server, and worth knowing
about even though nothing later depends on it. Skip it if you are offline.

### In VS Code Copilot *(bonus, and the most fun)*

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

Open Copilot in agent mode and ask about the weather in Tokyo. That is *your*
server, in a real host, driven by a frontier model — with no code written on
either side to make them meet. That is the M+N argument from module 1, delivered
rather than asserted.

---

## Exercises

If you finish early, in rough order of value:

1. **Add a `get_time(city)` tool** returning the local time. Then ask the agent in
   module 3 something that needs it.
2. **Make a description worse** — change one to `"""Gets data."""` — and watch the
   model in module 3 stop choosing it correctly. This is the fastest way to
   internalise that descriptions are behaviour.
3. **Add a `budget_eur` filter to `search_flights`** and see whether the model
   passes it when you mention a budget in plain language.
4. **Add a second resource**, e.g. `travel://packing-tips`.
5. **Return a deliberately huge list** and think about what that does to the
   model's context window. Real servers need pagination and limits; this is why
   `max_results` exists.

---

## Checkpoint

You should have **4 tools, 1 resource and 1 prompt**, and:

```bash
make check
# [  ok  ] MCP server — 4 tools, protocol 2026-07-28
```

You have now written the part that most people never write — the boring bit that
makes a model useful. The rest of the workshop is about consuming it.

Next: [03 — A client, and an agent loop](03-raw-client.md)

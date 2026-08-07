# 04 — Pydantic AI, and a browser

*~25 minutes. The payoff.*

Same agent as module 3. Roughly ten lines. Then we put it in a browser and let the
room talk to it.

- **Create**: empty `src/starter/agent_pydantic.py` and `src/starter/web.py` files
- **Solutions**: the matching files in `src/solution/`
- **Note**: this module runs in the **other** virtualenv, `.venv-agent`

---

## Part A — the same agent, ten lines

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

```bash
make pydantic Q="What should I pack for a trip to Tokyo?"
```

Put this next to `agent_raw.py` and ask what disappeared:

| You wrote by hand | Now |
|---|---|
| `mcp_tools_to_openai()` | gone — `MCPToolset` does it |
| the `for turn in range(MAX_TURNS)` loop | gone |
| appending assistant turns verbatim | gone |
| `tool_call_id` bookkeeping | gone |
| malformed-JSON handling | gone |

All of it is still happening. You are just not maintaining it any more — and you
additionally get retries, streaming, typed outputs, usage tracking and tracing
that you never wrote.

You can still see the calls:

```python
for message in result.all_messages():
    for part in message.parts:
        if part.part_kind == "tool-call":
            print(f"  -> called {part.tool_name}({part.args})")
```

### So should you use a framework?

The honest answer is "usually, eventually" — but you are now equipped to decide,
which is the actual point of doing module 3 first.

**A framework earns its place when** you need streaming, retries with backoff,
tracing and observability, structured/validated outputs, conversation persistence,
or several agents composed together. Writing all of that yourself is a real project,
and it is not *your* project.

**Rolling your own is fine when** you have one loop, a small number of tools, and
you want zero dependencies and total predictability. Forty lines you fully
understand beats a dependency you do not, especially in something long-lived.

**The trap is adopting one before understanding the loop.** Then every failure is
opaque: you cannot tell whether the model, your tool descriptions, or the framework
is at fault, and you end up cargo-culting fixes. You have avoided that trap by
doing this in the reverse order.

### The accidental lesson

Look at what actually just happened:

| | Server | Client |
|---|---|---|
| virtualenv | `.venv` | `.venv-agent` |
| MCP SDK | official `mcp` **2.0** | FastMCP (`mcp` **1.29**) |
| vendor | modelcontextprotocol | Pydantic / Prefect |
| protocol era | `2026-07-28` | pre-`2026-07-28` |

Different environments, different SDKs, from different vendors, on different sides
of a breaking protocol revision — and it works.

This was not staged. Those two packages genuinely cannot be installed together,
which is why the repo has two virtualenvs. But it is the best possible
demonstration of the point: **they only ever had to agree on the protocol.** Not a
language version, not a library, not a release cadence, not a vendor.

If you want one slide to justify MCP to colleagues, it is this table. A REST
integration between two teams on incompatible library versions is a meeting; this
was a subprocess call.

### Swap the model live

`model_config.py` reads `.env`, so:

```bash
MCP_WORKSHOP_PROVIDER=google make pydantic Q="Weather in Tokyo?"
```

Same server, same tools, same code — different model vendor entirely. Nothing on
the server side is aware anything changed. See [models.md](models.md).

---

## Part B — put it in a browser

*`src/starter/web.py`*

```python
from agent_pydantic import build_agent

agent = build_agent()
app = agent.to_web()
```

That is a complete chat application. Run it:

```bash
make web
```

Open <http://127.0.0.1:7932> and talk to your travel agent. Tool calls render live
in the message thread, so you can watch the model decide to call `get_forecast`,
receive the data, and reason about it — the same loop from module 3, now visible
to someone who has never seen a terminal.

Good things to type:

- *"What should I pack for Tokyo?"*
- *"Compare the weather in Reykjavik and Cape Town"*
- *"Find me a flight to Barcelona and tell me if I need a coat"*

Worth appreciating what this is: a local model, your own MCP server, and a browser
UI, with no cloud service involved anywhere and no API key. Turn the wifi off and
it still works.

### Making it work offline

That last claim takes a little effort. By default the UI pulls its HTML — plus a
~2 MB JavaScript bundle, CSS and icons — from a CDN. In a room with bad wifi that
is a broken finale.

`make setup` already vendored all of it into `vendor/`, and the solution serves it
locally:

```python
app = agent.to_web(html_source=str(CACHED_UI))

# The chat UI registers a catch-all "/{id}" route that would otherwise swallow
# "/static/...", so this mount has to be matched first.
app.routes.insert(0, Mount("/static", app=StaticFiles(directory=str(ASSET_DIR))))
```

Two gotchas, both of which will cost you an afternoon if you meet them cold:

1. **`html_source` alone is not enough.** The HTML it gives you still points at the
   CDN for the actual JavaScript. `scripts/download_web_ui.py` downloads every
   referenced asset and rewrites the references.
2. **The mount must be `insert(0, ...)`, not appended.** Starlette matches routes
   in order, and the UI's `/{id}` catch-all will happily claim `/static/app.js`.

### Optional flourish: human approval

Mark a tool as requiring approval and the UI grows approve/reject buttons before it
will run.

Worth demoing even briefly, because it makes the next module's security discussion
concrete: you have just built a system where a language model decides which
functions to execute, and *some functions should not run unattended*. The UI
control is one answer; the questions it raises are module 5.

---

## Exercises

1. **Add a system prompt with personality** via `instructions` and watch tone
   change without touching a tool.
2. **Give the agent a typed output** — `Agent(..., output_type=TripPlan)` with a
   Pydantic model — and get validated structured data instead of prose.
3. **Compare token usage** between the raw loop and Pydantic AI for the same
   question (`result.usage()`).
4. **Connect a second MCP server** — pass two toolsets and see the model choose
   across both. This is where M+N stops being theoretical.
5. **Deploy it**: switch the server to `transport="streamable-http"` and point the
   client at a URL instead of a subprocess.

---

Next: [05 — Where to go next](05-where-next.md)

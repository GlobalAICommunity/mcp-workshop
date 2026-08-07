# 04 — Pydantic AI, and a browser

*~25 minutes. The payoff.*

Same agent as module 3. Roughly ten lines. Then we put it in a browser.

- **Work in**: `src/starter/agent_pydantic.py`, then `src/starter/web.py`
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

Put it side by side with `agent_raw.py`. Everything you wrote is still happening —
schema translation, the loop, transcript bookkeeping, tool-call IDs, error
handling — you are just not maintaining it any more. You also get retries,
streaming, typed outputs and tracing thrown in.

That is the honest trade: a framework is worth it *once you know what it is
doing*. Which you now do.

You can still see the calls:

```python
for message in result.all_messages():
    for part in message.parts:
        if part.part_kind == "tool-call":
            print(f"  -> called {part.tool_name}({part.args})")
```

### The accidental lesson

Look at what just happened:

| | Server | Client |
|---|---|---|
| virtualenv | `.venv` | `.venv-agent` |
| MCP SDK | official `mcp` **2.0** | FastMCP (`mcp` **1.29**) |
| vendor | modelcontextprotocol | Pydantic / Prefect |
| protocol era | `2026-07-28` | pre-`2026-07-28` |

Different environments, different SDKs, different vendors, different protocol
eras — and it works, because they only ever agreed on the protocol.

If you want one slide to justify MCP to your colleagues, it is this table.

### Swap the model live

`model_config.py` reads `.env`, so:

```bash
MCP_WORKSHOP_PROVIDER=google make pydantic Q="Weather in Tokyo?"
```

Same server, same tools, same code, different model vendor. See
[models.md](models.md).

---

## Part B — put it in a browser

*`src/starter/web.py`*

```python
from agent_pydantic import build_agent

agent = build_agent()
app = agent.to_web()
```

```bash
make web
```

Open <http://127.0.0.1:7932> and talk to your travel agent. Tool calls render
live in the thread, so the room can watch the model decide to call
`get_forecast`, get the data back, and reason about it.

Good things to type:

- *"What should I pack for Tokyo?"*
- *"Compare the weather in Reykjavik and Cape Town"*
- *"Find me a flight to Barcelona and tell me if I need a coat"*

### Making it work offline

By default the UI pulls its HTML — and a ~2 MB JavaScript bundle, some CSS and
some icons — from a CDN. In a room with bad wifi, that is a broken finale.

`make setup` already vendored all of it into `vendor/`, and the solution serves
it locally:

```python
app = agent.to_web(html_source=str(CACHED_UI))

# The chat UI registers a catch-all "/{id}" route that would otherwise swallow
# "/static/...", so this mount has to be matched first.
app.routes.insert(0, Mount("/static", app=StaticFiles(directory=str(ASSET_DIR))))
```

Two gotchas, both of which will cost you an afternoon if you hit them cold:
`html_source` on its own is **not** enough — the HTML it gives you still points at
the CDN — and the mount really does have to be `insert(0, ...)` rather than
appended.

### Optional flourish: human approval

Mark a tool as requiring approval and the UI grows approve/reject buttons before
it will run. Which is a natural cue for the security conversation in module 5:
you are about to let a language model call functions, and some functions should
not run unattended.

---

Next: [05 — Where to go next](05-where-next.md)

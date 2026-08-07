# 00 — Setup

**Do this before the workshop starts.** It involves a few hundred megabytes of
downloads, and doing it in the room on shared wifi is how workshops lose their
first twenty minutes.

Budget about 15 minutes.

---

## 1. Prerequisites

| Thing | Version | Check |
|---|---|---|
| Python | 3.10 or newer | `python3 --version` |
| git | any | `git --version` |
| Node (optional) | 22.19+ | `node --version` |

Node is only needed for the MCP Inspector in module 2, which is a nice-to-have.
Everything else works without it.

## 2. Get the code

```bash
git clone https://github.com/GlobalAICommunity/mcp-workshop.git
cd mcp-workshop
```

## 3. Install

```bash
make setup
```

That creates two virtualenvs and downloads the browser chat UI for module 4.
If you do not have `make`, run the commands from the [Makefile](../Makefile) by hand.

### Why two virtualenvs?

Because the Python MCP ecosystem is mid-migration, and pretending otherwise would
make the workshop fail in a confusing way:

- **`.venv`** — the server and the raw client. Uses the official **`mcp` 2.0** SDK.
- **`.venv-agent`** — Pydantic AI and the web UI. Pydantic AI talks MCP through
  **FastMCP**, which still pins `mcp<2.0`.

Those two pins are incompatible, so `pip` cannot satisfy both in one environment.

This turns out to be a *useful* accident. In module 4 your agent will happily
drive your server while the two processes run different Python environments and
different MCP SDK versions from different vendors. That is what a protocol is
for. If you took one thing away from this workshop, it could reasonably be this.

## 4. Pick a model

The workshop needs a model that can call tools. The default is **Ollama**, which
runs locally, needs no account, and works with the wifi off.

```bash
# install from https://ollama.com, then:
ollama pull qwen3:4b
```

That is ~2.6 GB. If you have a machine with some room, `ollama pull qwen3:8b` is
noticeably more reliable at chaining tool calls.

Prefer a hosted model, or can't run one locally? The workshop supports **Google
Gemini**, **xAI Grok** and **Microsoft Foundry** as one-line swaps. See
[models.md](models.md) — Gemini has a usable free tier and is the easiest
non-local option.

Then configure it:

```bash
cp .env.example .env
# edit .env if you are not using Ollama
```

## 5. Check everything

```bash
make check
```

You want all green:

```
[  ok  ] Python version — 3.13
[  ok  ] Server virtualenv — mcp 2.0.0
[  ok  ] Agent virtualenv — pydantic-ai-slim 2.24.0
[  ok  ] MCP server — 4 tools, protocol 2026-07-28
[  ok  ] Offline chat UI — vendored
[  ok  ] Model provider — ollama / qwen3:4b — model available
```

Every failure prints what to do about it. If you are still stuck, see
[troubleshooting.md](troubleshooting.md).

---

Next: [01 — MCP basics](01-mcp-basics.md)

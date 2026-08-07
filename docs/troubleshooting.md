# Troubleshooting

Start with `make check` — it diagnoses most of this and tells you the fix.

---

## Setup

**`make setup` fails resolving dependencies**

Check `python3 --version` is 3.10+. If `pip` complains about a conflict *within*
one of the two requirements files, that is a real problem — but a conflict
*between* `mcp` 2.0 and `pydantic-ai` is expected and is exactly why there are
two virtualenvs. Never install both requirements files into one environment.

**`ModuleNotFoundError: No module named 'mcp'`**

You are using the wrong interpreter. Modules 1–3 run in `.venv`, module 4 runs in
`.venv-agent`. Use the `make` targets and this cannot happen.

**`ModuleNotFoundError: No module named 'pydantic_ai'`**

Same thing in reverse — that one lives in `.venv-agent`.

---

## The server

**`Invalid request parameters` from a hand-written JSON-RPC call**

Your `_meta` envelope is incomplete. Since `2026-07-28` every request must carry
the protocol version *and* client capabilities:

```json
"_meta": {
  "io.modelcontextprotocol/protocolVersion": "2026-07-28",
  "io.modelcontextprotocol/clientCapabilities": {}
}
```

The error message names the key you are missing. Note it is
`protocolVersion` — camelCase, even though the SDK's Python attributes are snake_case.

**Raw `tools/call` returns nothing**

The server exits when stdin closes, sometimes before the tool finishes. Hold the
pipe open:

```bash
{ echo "$REQUEST"; sleep 2; } | .venv/bin/python src/solution/travel_server.py
```

`scripts/raw_jsonrpc.sh` already does this.

**`ImportError: cannot import name 'FastMCP'`**

You are following a v1-era tutorial. It is `from mcp.server import MCPServer` now.

**The server prints nothing when I run it**

Correct. It is waiting for JSON-RPC on stdin. Use `make client` or `make jsonrpc`.

**Never `print()` in a stdio server** — stdout *is* the protocol channel. Use
`logging` to stderr instead. This produces gloriously confusing failures.

---

## Models

**`Ollama is not running`**

```bash
ollama serve
```

**`model not pulled`**

```bash
ollama pull qwen3:4b
```

`make check` prints which models you do have.

**The model ignores the tools, or invents ones that don't exist**

Almost always model capability. In rough order:

1. `ollama pull qwen3:8b` and set `MCP_WORKSHOP_MODEL=qwen3:8b`
2. Improve your tool descriptions — the model chooses based only on those
3. Switch to a hosted provider ([models.md](models.md))

Sub-4B models are not reliable at tool calling. Do not fight this.

**`arguments were not valid JSON`**

A small model produced malformed tool arguments. The workshop code catches this
and tells the model to retry. If it happens constantly, use a bigger model.

**Hosted provider returns 401 / 404**

- 401 — key not set, or set in the shell but not in `.env`
- 404 — usually the model name. For Foundry, `MCP_WORKSHOP_MODEL` must be your
  **deployment** name, not the model name.

Model defaults age quickly; check the provider's current list.

---

## The web UI

**Blank page, or unstyled**

The JavaScript bundle did not load. Run, while online:

```bash
.venv-agent/bin/python scripts/download_web_ui.py
```

Then check `/static/` returns 200 in your browser's network tab. If `/static/`
404s, the `StaticFiles` mount is being swallowed by the UI's catch-all `/{id}`
route — it must be `app.routes.insert(0, ...)`, not appended.

**Port already in use**

```bash
lsof -ti :7932 | xargs kill
```

or use another port: `.venv-agent/bin/uvicorn --app-dir src/solution web:app --port 7933`

---

## MCP Inspector

**`npx` fails or Node is too old**

Needs Node 22.19+. It is entirely optional — nothing in the workshop depends on
it. Use `make jsonrpc` instead.

---

Still stuck? Compare your file against the matching one in `src/solution/`.

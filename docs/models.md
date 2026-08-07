# Model providers

The workshop needs a model that can **call tools**. Everything is behind one
switch in `.env`:

```bash
MCP_WORKSHOP_PROVIDER=ollama   # ollama | google | grok | foundry
MCP_WORKSHOP_MODEL=            # optional override
```

The code lives in [`src/model_config.py`](../src/model_config.py). Switching
providers changes nothing else — which is a nice thing to demo, because it shows
your MCP server neither knows nor cares which model is on the other end.

---

## Which should I pick?

| | Cost | Setup | Offline | Tool calling |
|---|---|---|---|---|
| **Ollama** *(default)* | free | 2.6 GB download | ✅ | good |
| **Google Gemini** | free tier | API key | ❌ | excellent |
| **xAI Grok** | paid | API key | ❌ | excellent |
| **Microsoft Foundry** | paid / Azure credits | deployment + key | ❌ | excellent |

**Short version**: use Ollama if your laptop can take it — no account, no key, no
wifi needed. Use **Google** if it cannot; the free tier is enough for a workshop
and setup is one key.

---

## Ollama — local, free, offline

```bash
# install from https://ollama.com
ollama pull qwen3:4b
```

```bash
MCP_WORKSHOP_PROVIDER=ollama
```

| Model | Size | Notes |
|---|---|---|
| `qwen3:4b` | ~2.6 GB | The default. Good tool calling for its size. |
| `qwen3:8b` | ~5 GB | Noticeably more reliable at chaining calls. Use it if you can. |
| `llama3.1:8b` | ~4.7 GB | Solid alternative. |

Anything under 4B is unreliable at tool calling — it will produce plausible-looking
JSON for tools that do not exist. Don't.

Ollama serves an OpenAI-compatible API at `http://localhost:11434/v1`, which is
why the raw loop in module 3 works against it unchanged. Override with
`OLLAMA_BASE_URL` if you run it elsewhere.

**In practice it holds up well.** Across the workshop's demo questions `qwen3:4b`
picked the right tool every time, including a two-tool chain and recovering from
an unknown-city error. But it is a 4B model, so occasional skipped tools or
mangled arguments are possible — the workshop code handles that, and it is an
honest illustration of why production agents need retries. If it does wobble in
front of people, move to `qwen3:8b` or a hosted provider.

## Google Gemini — the easiest hosted option

Free key: <https://aistudio.google.com/api-keys>

```bash
MCP_WORKSHOP_PROVIDER=google
GOOGLE_API_KEY=...
```

Default model `gemini-flash-latest`. The free tier is rate-limited but fine for a
workshop. Best fallback if Ollama is not an option.

## xAI Grok

Key: <https://console.x.ai>

```bash
MCP_WORKSHOP_PROVIDER=grok
XAI_API_KEY=...
```

Default model `grok-4-fast`. Paid, no meaningful free tier.

We route Grok through its OpenAI-compatible endpoint rather than Pydantic AI's
native `XaiProvider`, purely to avoid pulling in the extra `xai-sdk` dependency.

## Microsoft Foundry (Azure AI Foundry)

Create a deployment at <https://ai.azure.com>, then:

```bash
MCP_WORKSHOP_PROVIDER=foundry
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/openai/v1/
AZURE_OPENAI_API_VERSION=2024-10-21
MCP_WORKSHOP_MODEL=<your-deployment-name>
```

**`MCP_WORKSHOP_MODEL` must be your *deployment* name**, not the underlying model
name. This trips everyone up at least once.

---

## Honesty about what has been tested

- **Ollama / `qwen3:4b`** — the recommended path, and **verified end to end** on
  an Apple Silicon Mac: single tool calls, multi-step chains, error recovery, the
  Pydantic AI path and the web UI all worked first time. Timings below.
- **Google, Grok, Foundry** — wired against current provider documentation and
  verified to construct the right client and model objects, but **not exercised
  with live credentials** by the workshop author. If one misbehaves, the model
  name or API version is the first thing to check.

### Rough timings with `qwen3:4b`

Measured on an Apple Silicon laptop with nothing else loaded:

| Question | Tools called | Time |
|---|---|---|
| "Weather in Amsterdam?" | 1 | ~10 s |
| "Weather in Atlantis?" | 1, then recovers | ~17 s |
| "What should I pack for Tokyo?" | 1 | ~40–55 s |
| "Flight to Barcelona + weather there" | 2 | ~75 s |

Slower hardware will be slower. Budget about a minute per question when demoing
live, and **warm the model up with one throwaway query before the session** — the
first call after a pull is noticeably the slowest.

Model names in particular move fast. All of them are overridable with
`MCP_WORKSHOP_MODEL`, and if a default has been retired by the time you read
this, that is the fix.

---

## Adding your own

Anything with an OpenAI-compatible endpoint takes about five lines in
`src/model_config.py`: add it to `PROVIDERS`, give it a default model, a base
URL and an API key variable. Nothing else in the workshop needs to change.

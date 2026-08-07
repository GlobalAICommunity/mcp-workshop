# Facilitator guide

Everything you need to run this workshop, including the bits that are not in the
attendee docs: what to say, what to skip, what breaks, and what people always ask.

If you are attending rather than running the workshop, you can ignore this file —
though the "questions people ask" section is worth a skim.

---

## The shape of it

The workshop has one narrative arc, and it is worth keeping in your head because
it tells you what to cut when you run late:

> **Here is a protocol → here is a server that speaks it → here is what it takes
> to actually use one → here is what a framework does for you.**

Module 3 is the intellectual peak: attendees write an agent loop by hand and
discover it is forty lines. Everything before it builds to that, and module 4
pays it off by showing the same thing in ten lines. Protect module 3 above all.

## Timing

| Module | Planned | Minimum | Notes |
|---|---|---|---|
| 0 Setup | 5 | 0 | Zero if pre-work actually got done |
| 1 Basics | 25 | 15 | Cut the deep protocol history first |
| 2 Server | 30 | 20 | Cut resources + prompts to a demo |
| 3 Raw client + loop | 25 | 25 | **Do not cut this** |
| 4 Pydantic AI + web | 25 | 15 | Cut to a demo if needed |
| 5 Wrap-up | 10 | 5 | Security slide is the one to keep |
| **Total** | **115** | **80** | |

**If you have 90 minutes**: trim module 1 to 15 (skip the MRTR/Tasks detail),
demo the resource and prompt in module 2 rather than having people type them, and
present module 4 rather than having people build it.

**If you have 120+**: let people do the module 2 and 3 exercises, and spend real
time on the security discussion in module 5 — it is the part most likely to
matter to them next week.

## Before the session

**Send the setup instructions at least two days ahead.** This is the single
biggest thing you can do. `make setup` downloads a few hundred MB and
`ollama pull qwen3:4b` is another 2.6 GB. A room of thirty people doing that
simultaneously on conference wifi will not work.

Your own checklist on the day:

- [ ] `make check` green on your machine
- [ ] **Warm the model up** — `ollama run qwen3:4b "hi"`. The first call after a
      pull is by far the slowest, and you do not want that to be your first demo.
- [ ] `make web` starts and answers a question
- [ ] Terminal font large enough to read from the back
- [ ] A pre-cloned repo with the solutions ready, in case you need to bail out
- [ ] Know your fallback if wifi dies (everything works offline once set up — this
      is why the workshop uses a local model and vendored web assets)

## Live demo notes

**Local models take 10–75 seconds per question.** This is the main thing that
will affect your pacing. Do not stand in silence waiting. Start a question, then
talk over it — explain what the loop is doing while it runs. The tool-call lines
printing to the terminal give you something to narrate.

**The fake data is deterministic.** `get_weather("Tokyo")` returns the same thing
every time on a given day, so you can rehearse a demo and trust it. It is derived
from a hash of the city name and the date — which also means the "weather" is
often absurd. Reykjavik at 22°C and rainy is normal. Lean into it; it reminds
people the data is fake and keeps attention on the protocol.

**Type, do not paste.** For the first tool in module 2 especially. People follow
typing; they do not follow a wall of pasted code.

---

## Module-by-module

### 0 — Setup (5 min)

Ask for a show of hands: who has green from `make check`? If more than a couple
of people are red, pair them with someone who is green rather than debugging live.
Nobody needs their own working environment to follow modules 1 and 2.

### 1 — Basics (25 min)

**Goal**: they leave understanding that MCP is a protocol, not a product, and
that it is boring in the good way.

The M×N framing is the one that lands. Ask the room how many AI tools they use
and how many internal systems they wish those tools could reach; multiply out
loud. LSP is the killer analogy for anyone who has used a code editor in the last
decade — same problem, same shape of solution, and MCP is explicitly modelled on it.

**Spend real time on the primitives table** (tools / resources / prompts, and who
controls each). This is the single most commonly misunderstood part of MCP, and
getting it right early saves confusion for the rest of the session.

**The `2026-07-28` section is your differentiator.** Most people in the room will
have read a blog post about MCP that is now wrong. Telling them the handshake was
removed and the protocol went stateless is genuinely useful news. If anyone is
following an older tutorial, this explains why nothing matches.

**Always run the raw JSON-RPC demo.** `./scripts/raw_jsonrpc.sh` is thirty
seconds and it demystifies the whole thing — one line of JSON in, structured
response out, no SDK, no handshake. Several people usually visibly relax here.

### 2 — Build a server (30 min)

**Goal**: they build something real, and see the schema the model will read.

Work through steps 1–3 together at your pace, then let them run ahead on 4–8.
Announce that `src/solution/` exists and that using it is fine — people who fall
behind and feel stuck stop learning entirely.

After the first tool works, immediately run
`./scripts/raw_jsonrpc.sh tools/list` and show them the generated schema. The
moment where they realise their docstring and type hints *became* the thing the
model reads is the point of the module.

**The docstring `Args:` trap is worth calling out explicitly** — it does not
produce parameter descriptions in `mcp` 2.0. People will hit it.

If Node is available, the Inspector is a nice five-minute detour. Skip it without
guilt if you are behind.

### 3 — Raw client and the agent loop (25 min)

**Goal**: agents stop being magic. This is the module people remember.

Part A is short — an MCP client with no LLM, which reframes "client" as an
ordinary program rather than something mysterious.

For part B, **draw the loop on a whiteboard before showing code**. Five boxes:
list tools → send to model → did it ask for a tool? → call it, append result →
back to the model. Then show that the code is that drawing.

Land these three points:

1. The `input_schema` passes straight through to the model API untouched. There
   is no clever translation. This is *why* MCP tools work with any model.
2. Errors go back to the model as text, and it recovers. Run the Atlantis
   example — it is the most convincing thing in the workshop.
3. The loop is forty lines. Say the sentence out loud: *"that's the whole thing
   every agent framework is doing."*

### 4 — Pydantic AI and the web UI (25 min)

**Goal**: a fair comparison, not a magic trick — plus a memorable finish.

Show `agent_pydantic.py` and `agent_raw.py` side by side. Ask what disappeared.
The answer is "everything you just wrote", and because they wrote it, they know
exactly what the framework is doing rather than trusting it blindly.

**The two-virtualenv table is your best slide.** Different Python environments,
different MCP SDKs from different vendors, different protocol eras — and it
works. If you only get one architectural point across, make it this one.

Finish with `make web`. Let someone from the room pick the question. Watching
tool calls appear live in a browser is the note to end on.

### 5 — Wrap-up (10 min)

Keep the security section even when you are out of time. Prompt injection via
tool descriptions and the confused-deputy problem are things people need to hear
*before* they wire an MCP server into their company's systems, and this may be
their only chance to hear it.

End on "build a server for something you actually use". The people who do that
in the following week are the ones for whom the workshop worked.

---

## Questions people always ask

**"Is this just OpenAI function calling with extra steps?"**
No — they solve different problems and compose well. Function calling is how one
model API accepts tool definitions. MCP is how tools are *published and
discovered*, independent of any model vendor. Module 3 makes this concrete: MCP
gives you the tools, function calling delivers them to the model. Write a server
once and it works with every model and every host.

**"Why not just use a REST API?"**
You could, and for a single integration you probably should. MCP adds discovery
(the client asks what exists at runtime rather than being coded against it),
model-readable descriptions and schemas, and one consistent shape across every
tool. The value shows up at the *N-th* integration, not the first.

**"Does the model see my whole database / filesystem?"**
Only what your server exposes. That is the point of writing the server: it is the
boundary. Which is also why the confused-deputy warning matters — your server
acts with *its* credentials, so scope them narrowly.

**"Can a server call the model back?"**
It used to be able to, via sampling. As of `2026-07-28` that is deprecated in
favour of MRTR: the server returns `resultType: "input_required"` and the client
handles it. Same outcome, no server-initiated requests, and much simpler to deploy.

**"Which languages have SDKs?"**
Python, TypeScript, C#, Java, Kotlin, Go, Rust, Ruby, PHP, Swift. This workshop is
Python but the concepts port directly — the protocol is the same JSON either way.

**"Is it production ready?"**
The protocol is stable and governed under the Linux Foundation, and it is shipping
in real products. The *Python ecosystem* is mid-migration, which you will see
first-hand in module 4. Check which `mcp` version a library pins before you build
an architecture on it.

**"How do I do auth?"**
OAuth 2.1, with servers advertising their authorisation server via RFC 9728. Do
not invent your own. Statelessness in the new revision makes this considerably
easier to scale.

**"What about cost / can I use GPT-4 instead?"**
Yes — set one variable in `.env`. The workshop defaults to a local model so that
nobody is blocked on an API key, not because it is the best model. See
[models.md](models.md).

---

## When things break

**Someone's `make check` is red mid-session.** Pair them with a neighbour. Do not
debug one laptop while thirty people watch.

**Ollama is slow or wedged.** Restart it (`ollama serve`), or switch that person
to a hosted provider if you have a spare key. A shared key you can hand out for
the session is a very effective backup plan.

**The model ignores tools.** Almost always a too-small model. `qwen3:8b` if they
have the RAM, otherwise a hosted provider.

**Your own demo fails live.** Fall back to `make client` — it needs no model at
all and still shows the protocol working. Failing that, talk through
`src/solution/` and promise the repo link.

**The wifi dies entirely.** Everything works offline: local model, vendored web
assets, fake data with no external calls. This is by design. Say so out loud —
it is a good moment.

More in [troubleshooting.md](troubleshooting.md).

---

## Adapting it

**Shorter (60 min)**: modules 1 and 3 only, demoing a pre-built server. You lose
the hands-on server build but keep the two ideas that matter most.

**Longer (half day)**: add a remote/Streamable HTTP section with real OAuth, have
people build a server for an API they actually use, and finish by wiring
everything into VS Code Copilot.

**Different domain**: the travel server is arbitrary. Any domain with 3–4 tools
and an obvious chaining question works — the only requirement is that some
question needs two tools to answer.

**Different language**: the concepts and module structure port to any SDK. Only
the code samples change.

---

If you run this and something lands badly — or lands unexpectedly well — please
open an issue. The timings above are honest estimates, and real rooms are the
only way to improve them.

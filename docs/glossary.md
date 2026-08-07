# Glossary

MCP has a fair amount of jargon, and some of it collides with words you already
use for other things ("client" and "server" in particular). This is everything
the workshop uses, in plain terms.

---

### Agent

A program that lets a model choose actions in a loop, rather than just producing
one reply. Concretely: send the conversation to a model with a list of available
tools; if it asks for a tool, run it, add the result, and send everything back;
repeat until it answers. You build one by hand in
[module 3](03-raw-client.md) — it is about forty lines.

There is no formal definition and the word is used loosely in marketing. The loop
is the substance.

### Client

One connection to one MCP server. A host runs several clients, one per server it
connects to.

Note this is *not* the same as "the client application" — the thing a user sees is
the **host**. In MCP, "client" is a narrow, technical role.

### Host

The application the user is actually using: VS Code, Claude Desktop, or your own
script. It owns the model, decides what the model is allowed to do, and manages
one or more clients.

### Server

A program that exposes capabilities — tools, resources, prompts — over MCP.
Usually small and boring, which is a feature. The travel server you build in
[module 2](02-build-a-server.md) is about 200 lines including fake data.

Runs as a subprocess (stdio) or as a web service (Streamable HTTP).

---

### Tool

Something the **model** can decide to call. The closest analogy is a POST
endpoint. `get_weather(city)` is a tool.

Tools are the primitive people mean when they say "MCP". Each has a name, a
description the model reads, and a JSON Schema for its arguments.

### Resource

Context the **application** decides to include — the model does not call it. Like
a GET endpoint or a file. Identified by a URI such as `travel://destinations`.

Use resources for reference data, file contents, schema dumps: things that inform
the model rather than actions it takes.

### Prompt

A reusable template the **user** deliberately selects — typically surfaced as a
slash command or menu item in a host. `/plan_a_trip` is a prompt.

This is how you ship an expert workflow instead of making every user reinvent
the wording.

> The three primitives differ by **who is in control**: model, application, user.
> This is the most commonly confused part of MCP.

---

### Tool calling *(a.k.a. function calling)*

The model-provider feature where you pass a list of tool definitions with your
request, and the model can reply asking for one to be called with specific
arguments. It does not run anything itself — it asks you to.

MCP and tool calling are complementary: MCP is how tools are published and
discovered, tool calling is how they reach a particular model.

### Structured output

A tool returning typed, machine-readable data (`structuredContent`) alongside the
human-readable text, described by an `outputSchema`. In Python you get this by
returning a Pydantic model.

### JSON Schema

The standard for describing the shape of JSON data. MCP uses it for tool inputs
and outputs. Since `2026-07-28`, full JSON Schema 2020-12.

This is the reason MCP tools drop into any model API unchanged — everyone already
speaks JSON Schema.

---

### JSON-RPC 2.0

The message format underneath MCP. A request has `jsonrpc`, `id`, `method` and
`params`; a response has `jsonrpc`, `id`, and either `result` or `error`. That is
essentially all of it. See it raw with `./scripts/raw_jsonrpc.sh`.

### Transport

How the JSON-RPC messages physically travel. MCP has two:

### stdio

The host launches the server as a subprocess and talks over stdin/stdout. Local,
no ports, no auth to configure. What this workshop uses.

**Consequence worth knowing**: stdout *is* the protocol channel, so a stray
`print()` in a stdio server corrupts the stream. Log to stderr.

### Streamable HTTP

The transport for remote servers, over HTTP POST. Add OAuth 2.1 and you can host
one. Replaces the deprecated HTTP+SSE transport.

---

### `_meta` envelope

Since `2026-07-28`, per-request metadata carrying the protocol version, client
capabilities and client info — the information that used to be exchanged once
during the handshake. It is what makes the protocol stateless.

Keys are reverse-DNS, e.g. `io.modelcontextprotocol/protocolVersion`.

### `server/discover`

The RPC that replaced the `initialize` handshake. Asks a server what it supports.
An ordinary request you can call whenever you like, or never.

### MRTR — Multi Round-Trip Requests

The replacement for server-initiated requests. If a server needs more information
it returns `resultType: "input_required"` rather than calling back into the
client; the client gathers what is needed and retries.

### Sampling *(deprecated)*

The old mechanism letting a **server** ask the **host** to run a model completion
— server-initiated, and removed in favour of MRTR. You will see it in older
tutorials.

### Roots *(deprecated)*

The old mechanism for a client telling a server which directories it may access.
Also server-initiated-adjacent, also on the deprecation path.

### Tasks

Long-running operations that outlive a single request. Moved out of core into an
official extension (`io.modelcontextprotocol/tasks`) in `2026-07-28`.

---

### Protocol revision

MCP versions are dates, not semver: `2026-07-28` is current. Servers advertise
which revisions they support, and a server can serve more than one era — you rely
on this in [module 4](04-pydantic-ai.md), where an `mcp` 1.x client drives your
2.0 server.

### `mcp` vs `fastmcp`

`mcp` is the official Python SDK; **2.0** is the first release speaking
`2026-07-28`. `fastmcp` is a popular third-party framework whose name survives in
the official SDK's v1 history (`mcp.server.fastmcp.FastMCP`), which is a
persistent source of confusion.

They currently pin incompatible versions of each other, which is why this
workshop uses two virtualenvs.

---

### Prompt injection

An attack where instructions are smuggled into text the model reads — including
**tool descriptions and tool results**. A malicious MCP server can put
instructions in a description. Treat servers like dependencies: only connect to
ones you trust. See [module 5](05-where-next.md).

### Confused deputy

Where your server acts with *its* credentials on behalf of a less-privileged
requester. If your server can read any file, anyone who can talk to the model can
read any file. Scope credentials narrowly.

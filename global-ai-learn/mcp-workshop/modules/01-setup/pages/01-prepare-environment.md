---
id: prepare-environment
title: Prepare and verify your environment
order: 1
estimatedMinutes: 5
---

You need Python 3.10 or newer, Git, and roughly 4 GB of free disk space. Node
22.19 or newer is optional and only needed for the MCP Inspector.

## Install the workshop

From the repository root, run:

```bash
make setup
```

This creates two virtual environments and downloads the browser chat UI used
later in the course:

| Environment | Purpose | MCP implementation |
|---|---|---|
| `.venv` | Server and raw client | Official `mcp` 2.0 SDK |
| `.venv-agent` | Pydantic AI and browser UI | FastMCP with `mcp` 1.x |

The dependency pins cannot be satisfied in one environment. Keeping the two
processes separate also demonstrates why a protocol is useful: implementations
can use different libraries and versions as long as they agree on the wire
format.

## Choose a model

The default is Ollama with `qwen3:4b`, which runs locally without an account:

```bash
ollama pull qwen3:4b
ollama run qwen3:4b "hello" --verbose=false
```

Copy the example configuration:

```bash
cp .env.example .env
```

The workshop also supports Google Gemini, xAI Grok, and Microsoft Foundry. Set
`MCP_WORKSHOP_PROVIDER` and the corresponding credentials in `.env` when you use
a hosted provider.

## Verify the installation

Run the complete setup check:

```bash
make check
```

Confirm that it reports a supported Python version, both virtual environments,
four server tools, the vendored browser UI, and an available model. Resolve any
failure before continuing because later exercises depend on all of these pieces.
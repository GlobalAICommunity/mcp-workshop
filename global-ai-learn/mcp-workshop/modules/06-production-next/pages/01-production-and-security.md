---
id: production-and-security
title: Deploy and secure MCP systems
order: 1
estimatedMinutes: 10
---

You now have an MCP server, a raw client, an agent loop, a framework agent, and a
browser UI. Moving that system into production changes the operational and
security requirements even though the tool implementations can remain the same.

## Move from stdio to HTTP

For a remote server, change the transport:

```python
mcp.run(transport="streamable-http")
```

Use OAuth 2.1 and RFC 9728 protected-resource metadata. Do not replace a proper
authorization flow with one shared bearer token. The stateless `2026-07-28`
protocol allows identical instances behind a load balancer without session
affinity or a shared session store.

Production servers also need rate limits, timeouts, health checks, partial
degradation plans, and structured logs. Continue sending logs to stderr when the
same server can run over stdio.

## Protect the context window

Every tool result consumes model context. A tool that returns thousands of rows
can crowd out the conversation and create unnecessary cost without raising a
clear error.

Default to small responses, support pagination, and offer explicit limits.
Summarize large datasets rather than dumping them. The travel server's
`max_results` argument demonstrates this design choice.

## Treat model-facing data as untrusted

Tool descriptions and results enter the model's context, where malicious content
can act as prompt injection. Connect only trusted servers, review their updates,
and treat tool definitions like dependency changes.

A server acts with its own credentials. Scope those credentials narrowly and,
where possible, per user. Validate every tool argument and perform authorization
checks in the tool implementation. Schema validation checks shape, not permission.

Require human confirmation before tools delete data, send messages, make
payments, or deploy software. Also audit combinations of tools: a file-reading
tool and an HTTP tool may enable data exfiltration even if each looks safe alone.

## Build a useful next server

Choose a system you use daily, such as team documentation, a scoped notes folder,
an internal API, or a read-only database with mandatory limits. Wire it into your
host, use it for real work, and revise its descriptions when the model chooses
tools incorrectly. Tool descriptions are executable guidance, so small wording
changes can materially improve behavior.
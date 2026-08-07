---
id: protocol-foundations
title: Protocol foundations and primitives
order: 1
estimatedMinutes: 25
---

A language model cannot inspect your live systems or perform actions by itself.
AI applications therefore need integrations for repositories, databases,
ticketing systems, files, and internal APIs.

## From M x N to M + N

If you have M AI applications and N external systems, custom adapters require
M x N integrations. MCP changes the shape: each application implements the
protocol once and each external system exposes one MCP server. The result is
approximately M + N implementations.

This is the same architectural benefit provided by the Language Server Protocol.
A language server does not need custom code for every editor, and an MCP server
does not need custom code for every model host.

## Host, client, and server

| Role | Responsibility |
|---|---|
| Host | Owns the user experience, model, permissions, and policy |
| Client | Maintains one connection from a host to one server |
| Server | Exposes capabilities for one domain or system |

A host can run several clients, one for each connected server. Communication uses
JSON-RPC 2.0 requests with `method` and `params`, followed by responses containing
either `result` or `error`.

The server does not know which model provider the host uses. That separation is
what lets you change models without changing server code.

## Tools, resources, and prompts

The three primitives differ by who decides to use them:

| Primitive | Controlled by | Use it for |
|---|---|---|
| Tool | Model | Actions and on-demand lookups |
| Resource | Application | Context such as files, schemas, or reference data |
| Prompt | User | Named expert workflows and reusable instructions |

Ask three questions when choosing a primitive:

- Should the model invoke it during reasoning? Use a tool.
- Should the application inject it as context? Use a resource.
- Should the user deliberately select the workflow? Use a prompt.

## Transports

Use `stdio` for local integrations. The client launches the server as a child
process and communicates over standard input and output. Never log to stdout in
a stdio server because stdout carries the protocol. Send logs to stderr.

Use Streamable HTTP for remote servers. It uses HTTP POST and should be paired
with OAuth 2.1. The older HTTP plus SSE transport is deprecated.

## Protocol revision 2026-07-28

The current revision is stateless. The old initialization handshake and
`Mcp-Session-Id` are gone. Request metadata carries protocol and client details,
and `server/discover` provides capability discovery.

Server-initiated requests such as sampling, roots, and logging are deprecated.
Multi Round-Trip Requests replace callbacks by returning an `input_required`
result when a server needs more information. Stateless requests simplify remote
deployment because instances do not need session affinity or shared session state.
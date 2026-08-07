---
schemaVersion: 1
id: mcp-workshop
version: "1.0"
title: Build with the Model Context Protocol
summary: Build an MCP server, connect it to an agent, and ship the result in a browser.
durationMinutes: 120
difficulty: Intermediate
prerequisites:
  - Python 3.10 or newer
  - Git and a terminal
  - Basic experience calling an LLM API
learningOutcomes:
  - Explain how MCP replaces M x N custom integrations with M + N protocol implementations
  - Build an MCP server with typed tools, a resource, and a prompt
  - Implement the tool-calling agent loop with a raw MCP client
  - Use Pydantic AI to expose an MCP-backed agent in a browser
  - Apply deployment and security practices to production MCP servers
modules: [setup, mcp-basics, build-server, agent-loop, pydantic-browser, production-next]
---

In this hands-on course, you build a fake travel service that exposes weather,
forecasts, flights, and destinations through the Model Context Protocol (MCP).
The data is deterministic and local, so you can focus on the protocol rather
than API keys, rate limits, or network failures.

You first inspect MCP at the protocol level, then build a server and consume it
from an ordinary Python client. After that, you write the complete agent loop by
hand, rebuild it with Pydantic AI, and put it in a browser. The final module
covers remote deployment, context limits, and the security concerns that matter
when a language model can choose which functions to execute.

The course targets MCP revision `2026-07-28` and Python SDK `mcp` 2.0.
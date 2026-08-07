---
id: pydantic-browser
title: Use Pydantic AI and a browser
summary: Replace manual agent plumbing with a framework and expose the MCP-backed agent as a local chat application.
order: 5
pages: [framework-and-browser]
questions:
  - id: framework-value
    type: multiple-choice
    prompt: Which responsibilities can Pydantic AI take over from the raw agent loop?
    options:
      - id: tool-conversion
        text: Converting MCP tool definitions into the model's tool format
      - id: turn-bookkeeping
        text: Preserving assistant turns and matching tool call ids
      - id: retries
        text: Retrying invalid model output and tool calls
      - id: server-authorization
        text: Defining the production authorization policy for the MCP server
    correctOptionIds: [tool-conversion, turn-bookkeeping, retries]
    explanation: The framework handles agent-loop mechanics and retries, but application owners still define authentication and authorization policy.
---

Rebuild the raw agent with Pydantic AI, inspect what the framework now owns, and
serve the same MCP-backed experience in a browser.
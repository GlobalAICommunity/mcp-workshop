---
id: setup
title: Set up the workshop
summary: Install the two Python environments, choose a model, and verify the local toolchain.
order: 1
pages: [prepare-environment]
questions:
  - id: two-environments
    type: single-choice
    prompt: Why does this workshop use two Python virtual environments?
    options:
      - id: incompatible-pins
        text: The official MCP 2.0 SDK and the FastMCP version used by Pydantic AI have incompatible dependency pins
      - id: operating-systems
        text: The server and client must run on different operating systems
      - id: model-isolation
        text: Every model provider requires its own Python interpreter
    correctOptionIds: [incompatible-pins]
    explanation: The server uses the official MCP 2.0 SDK, while Pydantic AI currently reaches MCP through FastMCP, which pins mcp below 2.0.
---

Prepare a reproducible local environment before working with the protocol. The
verification script checks the SDKs, server, browser assets, and selected model.
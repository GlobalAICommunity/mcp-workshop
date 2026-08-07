---
id: agent-loop
title: Write a client and agent loop
summary: Call the server without a model, then implement tool calling and conversation bookkeeping by hand.
order: 4
pages: [client-and-loop]
questions:
  - id: preserve-tool-turn
    type: single-choice
    prompt: Why must the agent append the assistant turn containing tool calls to the message history?
    options:
      - id: model-stateless
        text: The model is stateless between requests and needs that turn to understand why tool results follow
      - id: server-storage
        text: The MCP server stores assistant messages in its database
      - id: schema-generation
        text: Tool schemas can only be generated from previous assistant text
    correctOptionIds: [model-stateless]
    explanation: The messages list is the model's memory. Without the assistant request, the next tool result has no matching conversational context.
---

Separate MCP from model behavior by calling the server from an ordinary client.
Then add the small loop that turns model tool requests into an agent.
---
id: mcp-basics
title: Understand MCP
summary: Learn the integration model, architecture, primitives, transports, and current protocol lifecycle.
order: 2
pages: [protocol-foundations]
questions:
  - id: primitive-control
    type: multiple-choice
    prompt: Which statements correctly match MCP primitives to the party that controls them?
    options:
      - id: model-tools
        text: The model chooses when to call tools
      - id: application-resources
        text: The application chooses which resources to include
      - id: user-prompts
        text: The user chooses prompts such as expert workflows
      - id: model-prompts
        text: The model silently chooses prompts on behalf of the user
    correctOptionIds: [model-tools, application-resources, user-prompts]
    explanation: Tools are model-controlled, resources are application-controlled, and prompts are user-controlled.
---

Build a mental model of MCP before writing code. The important distinctions are
who controls each primitive and where the host, client, and server boundaries sit.
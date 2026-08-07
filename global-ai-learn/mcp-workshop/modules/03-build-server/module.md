---
id: build-server
title: Build an MCP server
summary: Define typed tools, structured results, recoverable errors, a resource, and a prompt.
order: 3
pages: [server-capabilities]
questions:
  - id: structured-output
    type: multiple-choice
    prompt: Which benefits come from returning a Pydantic model from an MCP tool?
    options:
      - id: output-schema
        text: The SDK can expose a machine-readable output schema
      - id: result-validation
        text: Returned values can be validated against declared types and constraints
      - id: automatic-auth
        text: The SDK automatically authorizes every caller
      - id: structured-content
        text: Non-model consumers can use structured content without parsing prose
    correctOptionIds: [output-schema, result-validation, structured-content]
    explanation: Typed models provide schemas, validation, and structured content. Authentication remains an application and deployment concern.
---

Build the fake travel server used throughout the rest of the course. Its
deterministic data keeps the exercise focused on MCP behavior and schemas.
---
title: Build with the Model Context Protocol final test
questions:
  - id: final-integration-shape
    type: single-choice
    prompt: What integration shape does MCP provide for M hosts and N external systems?
    options:
      - id: additive
        text: Approximately M + N protocol implementations
      - id: multiplicative
        text: M x N custom adapters
      - id: constant
        text: One implementation regardless of the number of hosts and systems
    correctOptionIds: [additive]
    explanation: Each host and each system implements MCP once, changing the integration shape from multiplicative to approximately additive.
  - id: final-primitives
    type: multiple-choice
    prompt: Which primitive and controller pairings are correct?
    options:
      - id: tool-model
        text: Tools are selected by the model
      - id: resource-app
        text: Resources are selected by the application
      - id: prompt-user
        text: Prompts are selected by the user
      - id: resource-model
        text: Resources are always fetched directly by the model
    correctOptionIds: [tool-model, resource-app, prompt-user]
    explanation: Control is the key distinction among tools, resources, and prompts.
  - id: final-schema
    type: single-choice
    prompt: What becomes the JSON Schema for a decorated Python tool's arguments?
    options:
      - id: type-hints
        text: Its Python type hints and supported Pydantic field metadata
      - id: function-body
        text: The implementation statements inside the function
      - id: server-name
        text: The MCP server's display name
    correctOptionIds: [type-hints]
    explanation: The SDK derives input schema from annotations and Pydantic metadata; the function body is not exposed to the model.
  - id: final-tool-errors
    type: true-false
    prompt: A recoverable MCP tool error should tell the model what was invalid and how it can correct the request.
    options:
      - id: "true"
        text: "True"
      - id: "false"
        text: "False"
    correctOptionIds: ["true"]
    explanation: Tool errors are model-facing results, so actionable messages can enable recovery on the next agent turn.
  - id: final-loop
    type: multiple-choice
    prompt: Which steps are required for a reliable raw tool-calling loop?
    options:
      - id: preserve-assistant
        text: Preserve assistant turns that contain tool requests
      - id: match-ids
        text: Match each result to the request's tool call id
      - id: cap-turns
        text: Set a maximum number of turns
      - id: discard-errors
        text: Discard all tool errors before the model sees them
    correctOptionIds: [preserve-assistant, match-ids, cap-turns]
    explanation: Conversation history, call id matching, and a turn limit prevent common correctness and runaway-loop failures.
  - id: final-interoperability
    type: true-false
    prompt: An MCP client and server can use different SDK implementations and dependency versions if they agree on a compatible protocol.
    options:
      - id: "true"
        text: "True"
      - id: "false"
        text: "False"
    correctOptionIds: ["true"]
    explanation: The protocol is the contract, which is why the workshop's official MCP server and FastMCP client can communicate across separate environments.
  - id: final-production-security
    type: multiple-choice
    prompt: Which practices reduce risk for a production MCP server?
    options:
      - id: authorize
        text: Authorize each operation instead of relying only on schema validation
      - id: limit-output
        text: Bound and paginate tool output
      - id: approve-destructive
        text: Require human approval for irreversible actions
      - id: stdout-logs
        text: Write diagnostic logs to stdout when using stdio
    correctOptionIds: [authorize, limit-output, approve-destructive]
    explanation: Production systems need permission checks, bounded context usage, and approval gates. Stdout must remain reserved for the stdio protocol.
---

This final test covers the architecture, implementation, agent behavior, and
production practices from all six modules.
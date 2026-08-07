---
id: production-next
title: Prepare MCP for production
summary: Move beyond local stdio with remote transport, bounded outputs, authorization, and model-aware security controls.
order: 6
pages: [production-and-security]
questions:
  - id: production-controls
    type: multiple-choice
    prompt: Which controls are important when an MCP server is used in production?
    options:
      - id: bounded-results
        text: Pagination and result limits to protect the model's context window
      - id: human-approval
        text: Human approval for destructive or irreversible actions
      - id: narrow-credentials
        text: Narrow, preferably per-user credentials and authorization checks
      - id: trust-arguments
        text: Trust tool arguments because the model generated them from a schema
    correctOptionIds: [bounded-results, human-approval, narrow-credentials]
    explanation: Model-generated arguments remain untrusted input. Bound results, scope credentials, check permissions, and confirm irreversible actions.
---

Review the deployment and security practices needed when an MCP server leaves a
developer laptop and starts acting with real credentials.
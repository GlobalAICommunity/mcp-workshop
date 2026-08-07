---
id: client-and-loop
title: Build the client and tool-calling loop
order: 1
estimatedMinutes: 25
---

Work first in `src/starter/mcp_client.py`, then in
`src/starter/agent_raw.py`. Matching solutions are available under
`src/solution/`.

## Call MCP without a model

An MCP client is an ordinary program. It starts the server, lists capabilities,
and invokes them:

```python
from mcp import Client, StdioServerParameters, stdio_client

transport = stdio_client(
    StdioServerParameters(command=sys.executable, args=[str(SERVER)])
)

async with Client(transport) as client:
    listing = await client.list_tools()
    result = await client.call_tool("get_weather", {"city": "Amsterdam"})
    print(result.structured_content)
```

Run it with `make client`. Inspect `client.protocol_version`,
`result.structured_content`, and `result.is_error`. Tool errors arrive as normal
results rather than client exceptions. Resources and prompts use
`read_resource` and `get_prompt`, not `call_tool`.

## Understand the agent mechanism

A model does not execute a tool. It returns a request naming a tool and its
arguments. Your application executes that request, appends the result to the
conversation, and asks the model what to do next. Repeat until the model answers
without requesting another tool.

The MCP-to-model adapter is small because both sides already use JSON Schema:

```python
def mcp_tools_to_openai(tools) -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.input_schema,
            },
        }
        for tool in tools
    ]
```

No per-tool conversion is required. The envelope changes, but
`tool.input_schema` passes through unchanged.

## Implement the loop

```python
for turn in range(MAX_TURNS):
    response = await llm.chat.completions.create(
        model=model_name,
        messages=messages,
        tools=tools,
    )
    reply = response.choices[0].message
    messages.append(assistant_message(reply))

    if not reply.tool_calls:
        return reply.content

    for call in reply.tool_calls:
        arguments = json.loads(call.function.arguments)
        result = await mcp.call_tool(call.function.name, arguments)
        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": text_of(result),
        })
```

Three details keep this reliable:

1. Append the complete assistant turn, including its tool calls. The messages
   list is the stateless model's only memory.
2. Return each result with the exact `tool_call_id` from its request. The id
   pairs concurrent requests with their results.
3. Cap the number of turns. A model can repeat a failing call indefinitely.

Treat malformed arguments as feedback for the model instead of crashing the
loop. For example, append `Error: arguments were not valid JSON. Try again.` and
let the next turn recover.

## Exercise multi-step behavior

Run the agent:

```bash
make agent Q="Find me a flight from Amsterdam to Barcelona and tell me the weather there"
```

The model should choose both a flight tool and a weather tool, then combine the
results. Also ask for weather in Atlantis. A useful tool error lets the model
recover, often by calling `list_destinations` before trying again.

This loop is the core of an agent framework. Frameworks add retries, streaming,
tracing, persistence, and richer error handling, but the request-execute-append
cycle remains underneath.
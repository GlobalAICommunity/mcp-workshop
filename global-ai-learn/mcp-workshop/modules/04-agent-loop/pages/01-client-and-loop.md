---
id: client-and-loop
title: Build the client and tool-calling loop
order: 1
estimatedMinutes: 40
---

You will create two files from nothing. `mcp_client.py` proves that MCP works
without a model. `agent_raw.py` then adds the complete model tool-calling loop.
The repository provides `src/model_config.py` as setup infrastructure so this
lesson can focus on MCP and agent mechanics rather than provider authentication.

## Part 1, step 1: Create the client file

Empty the client file:

```bash
: > src/starter/mcp_client.py
```

Add imports, paths, and the stdio transport factory:

```python
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters, stdio_client

SERVER = Path(__file__).with_name("travel_server.py")


def server_transport():
    return stdio_client(
        StdioServerParameters(command=sys.executable, args=[str(SERVER)])
    )
```

The transport launches the server file you built in the previous module using
the same Python environment as the client.

## Part 1, step 2: Discover and call tools

Append the asynchronous program:

```python
async def main() -> None:
    async with Client(server_transport()) as client:
        print(f"Protocol revision: {client.protocol_version}\n")

        listing = await client.list_tools()
        print("Tools:")
        for tool in listing.tools:
            print(f"  - {tool.name}: {tool.description}")

        weather = await client.call_tool("get_weather", {"city": "Amsterdam"})
        print("\nStructured weather:", weather.structured_content)
        print("Text weather:", weather.content[0].text)

        error = await client.call_tool("get_weather", {"city": "Atlantis"})
        print("\nAtlantis is_error:", error.is_error)
        print("Atlantis result:", error.content[0].text)

        resources = await client.list_resources()
        print("\nResources:", [str(item.uri) for item in resources.resources])
        catalog = await client.read_resource("travel://destinations")
        print(catalog.contents[0].text)

        prompts = await client.list_prompts()
        print("\nPrompts:", [item.name for item in prompts.prompts])
        prompt = await client.get_prompt(
            "plan_a_trip", {"city": "Tokyo", "nights": "4"}
        )
        print(json.dumps(prompt.messages[0].content.text, indent=2))
```

Tool errors arrive as results instead of client exceptions. Resources and prompts
have their own methods because they are distinct protocol primitives.

## Part 1, step 3: Run your client

Append the entry point:

```python
if __name__ == "__main__":
    asyncio.run(main())
```

Compile and run the file you created:

```bash
.venv/bin/python -m py_compile src/starter/mcp_client.py
.venv/bin/python src/starter/mcp_client.py
```

## Part 2, step 1: Create the raw agent file

Now start the agent from an empty file:

```bash
: > src/starter/agent_raw.py
```

Add imports and shared configuration:

```python
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp import Client

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from model_config import describe, get_openai_client

from mcp_client import server_transport

MAX_TURNS = 6

SYSTEM_PROMPT = (
    "You are a concise travel assistant. Use the available tools for weather "
    "and flight questions. Use list_destinations when a city is uncertain."
)
```

`model_config.py` returns an OpenAI-compatible client for the provider selected
in `.env`. The MCP server remains unaware of that provider.

## Part 2, step 2: Adapt MCP schemas

Append the only protocol-to-model adapter:

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

MCP and the model API both use JSON Schema, so `input_schema` passes through
unchanged. Only the surrounding envelope is different.

## Part 2, step 3: Start the conversation loop

Append the beginning of the `run` function:

```python
async def run(question: str) -> str:
    llm, model_name = get_openai_client()

    async with Client(server_transport()) as mcp:
        listing = await mcp.list_tools()
        tools = mcp_tools_to_openai(listing.tools)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]

        for turn in range(MAX_TURNS):
            response = await llm.chat.completions.create(
                model=model_name,
                messages=messages,
                tools=tools,
            )
            reply = response.choices[0].message
```

Do not close the function yet. The next step is appended at the same indentation
level inside the `for` loop.

## Part 2, step 4: Preserve the assistant request

Append this code with 12 leading spaces, aligned with `response` and `reply`:

```python
            messages.append(
                {
                    "role": "assistant",
                    "content": reply.content or "",
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": "function",
                            "function": {
                                "name": call.function.name,
                                "arguments": call.function.arguments,
                            },
                        }
                        for call in (reply.tool_calls or [])
                    ],
                }
            )

            if not reply.tool_calls:
                return reply.content or "(no answer)"
```

The messages list is the stateless model's memory. If you omit the assistant turn
that requested tools, the next tool result has no conversational cause.

## Part 2, step 5: Execute requested tools

Append the tool execution block, still inside the `for` loop:

```python
            for call in reply.tool_calls:
                name = call.function.name
                try:
                    arguments = json.loads(call.function.arguments or "{}")
                except json.JSONDecodeError:
                    output = "Error: arguments were not valid JSON. Try again."
                else:
                    print(f"  -> calling {name}({arguments})")
                    result = await mcp.call_tool(name, arguments)
                    output = "\n".join(
                        block.text
                        for block in result.content
                        if hasattr(block, "text")
                    )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": output,
                    }
                )

        return "Stopped after too many tool-calling turns."
```

Matching `tool_call_id` values pair each result with its request. `MAX_TURNS`
prevents a repeating model from creating an unbounded loop. Invalid JSON is fed
back as a tool result so the model can retry.

## Part 2, step 6: Add the command-line entry point

Append the final section at the left margin:

```python
async def main() -> None:
    question = " ".join(sys.argv[1:]) or "What is the weather in Amsterdam?"
    print(f"[{describe()}]")
    print(f"Q: {question}\n")
    answer = await run(question)
    print(f"\nA: {answer}")


if __name__ == "__main__":
    asyncio.run(main())
```

Compile and run your agent directly:

```bash
.venv/bin/python -m py_compile src/starter/agent_raw.py
.venv/bin/python src/starter/agent_raw.py \
  "Find me a flight from Amsterdam to Barcelona and tell me the weather there"
```

The model should call both flight and weather tools before answering. Then ask
for weather in Atlantis. The recoverable server error gives the model enough
information to choose a supported city or call `list_destinations`.

You have now built the complete request-execute-append cycle used by agent
frameworks. The next module replaces this plumbing with a framework only after
you have implemented every moving part yourself.
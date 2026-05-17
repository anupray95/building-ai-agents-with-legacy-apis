# Building an AI Agent with Legacy APIs

The whole point of this project is to build a fully working AI agent from scratch using nothing but the legacy OpenAI Chat Completions API. No native function calling, no Responses API, no assistants API — just plain old `chat.completions.create` and some prompt engineering.

The idea is to understand what agents actually do under the hood before reaching for the abstractions that hide it all.

## How it works

The agent loop is manual. The system prompt tells the model to always respond with a specific JSON structure — either a tool request or a final answer. The code parses that JSON, runs the tool if needed, appends the result back to the conversation history, and loops until the model says it's done.

Because this is the legacy completions format, tool results go back in as `user` role messages, not `tool` role. The model reads them in the next turn and decides what to do next.

The response schema looks like this:

```json
{
  "isFinalAnswer": false,
  "toolsReq": [
    {
      "toolName": "WebSearch",
      "params": { "query": "something" }
    }
  ],
  "response": ""
}
```

When `isFinalAnswer` is `true`, the loop ends and the response is printed.

## Setup

You'll need Python and these packages:

```
pip install openai python-dotenv mcp ddgs
```

Copy `.env.example` to `.env` (or just create a `.env`) and fill in:

```
AI_API_KEY=your_api_key_here
AI_BASE_URL= # optional, leave blank for OpenAI
AI_MODEL=your_model_name
```

`AI_BASE_URL` is optional. If you leave it out, it defaults to OpenAI's endpoint. This makes it easy to swap in any OpenAI-compatible provider.

## Running

```bash
python main.py
```

You'll get a prompt. Type your message and the agent will work through it, calling tools as needed, until it has a final answer.

## Tools available out of the box

- `Calculator` — basic arithmetic
- `WebSearch` — DuckDuckGo search, returns up to 5 results
- `ReadFile` / `WriteFile` — local file access
- `get_current_datetime` — current date and time
- `userPrompt` — asks you a follow-up question mid-task

## Adding a tool

1. Write a Python function in `agent/tools.py`
2. Add it to `tools_registry` (name → function)
3. Add a descriptor to the `tools` list (name, params, description)

The descriptor goes straight into the system prompt, so the model knows the tool exists and how to call it.

## MCP support

You can connect MCP servers by editing `mcp.json`. The bridge discovers tools from each server on startup and adds them to the registry automatically. Supports stdio, SSE, and HTTP transports.

```json
{
  "servers": [
    {
      "name": "my-server",
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@some/mcp-server"]
    }
  ]
}
```

If `mcp.json` doesn't exist or has no servers, it just skips that step.

## Project structure

```
main.py              entry point, starts the conversation loop
chat.py              thin wrapper around chat.completions.create
agent/
  core.py            the agentic loop and JSON extraction
  tools.py           tool definitions and registry
  prompt.py          system prompt builder
  mcp_bridge.py      MCP server discovery and tool wrapping
```

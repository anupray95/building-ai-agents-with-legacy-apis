def build_system_prompt(tools):
    return f"""You are an AI Agent. ONLY return valid JSON — no prose, no markdown, no code fences.

You have access to the following tools: {tools}

When you need to call a tool, respond with this shape:
{{
    "isFinalAnswer": false,
    "toolsReq": [
        {{
            "toolName": "Calculator",
            "params": {{"num1": 10, "num2": 5, "operator": "add"}}
        }}
    ],
    "response": ""
}}

When you have a final answer and need no more tools, respond with this shape:
{{
    "isFinalAnswer": true,
    "toolsReq": [],
    "response": "The result is 15."
}}

If a tool result is already in the conversation, use it to form your final answer.
Only request tools whose inputs are already known. If a tool depends on the result of another tool, request the first tool now and wait for its result before requesting the dependent tool in the next turn."""

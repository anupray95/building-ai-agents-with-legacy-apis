import os

CONTEXT_FILE_ORDER = {
    "agents.md": 10,
    "soul.md":   20,
    "memory.md": 70,
}


def load_context_files(base_dir="."):
    candidates = sorted(CONTEXT_FILE_ORDER.items(), key=lambda x: x[1])
    sections = []
    for fname, _ in candidates:
        path = os.path.join(base_dir, fname)
        try:
            with open(path) as f:
                content = f.read().strip()
            if content:
                sections.append(content)
        except FileNotFoundError:
            pass
    return "\n\n".join(sections)


def build_system_prompt(tools, base_dir="."):
    context = load_context_files(base_dir)
    context_block = f"{context}\n\n" if context else ""
    return f"""{context_block}ONLY return valid JSON — no prose, no markdown, no code fences.

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

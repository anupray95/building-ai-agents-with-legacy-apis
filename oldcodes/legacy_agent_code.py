import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from duckduckgo_search import DDGS
from chat import chatCompletion

load_dotenv()

def userPrompt(question):
    return input(question+'\n')

def get_current_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def WebSearch(query):
    results = DDGS().text(query, max_results=5)
    return [{"title": r["title"], "url": r["href"], "snippet": r["body"]} for r in results]

def ReadFile(path):
    with open(path, "r") as f:
        return f.read()

def WriteFile(path, content):
    with open(path, "w") as f:
        f.write(content)
    return f"Written to {path}"

def Calculator(num1, num2, operator):
    num1 = int(num1)
    num2 = int(num2)
    if operator == 'add':
        return num1 + num2
    elif operator == 'sub':
        return num1 - num2
    elif operator == 'mul':
        return num1 * num2
    elif operator == 'div':
        return num1 / num2

def extract_json(s):
    start = s.find('{')
    depth = 0
    for i, ch in enumerate(s[start:], start):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return s[start:i+1]

def get_client():
    return (
        OpenAI(api_key=os.getenv("AI_API_KEY"), base_url=os.getenv("AI_BASE_URL") or None),
        os.getenv("AI_MODEL"),
    )

client, model = get_client()
tools_registry = {
    "Calculator": Calculator,
    "userPrompt": userPrompt,
    "get_current_datetime": get_current_datetime,
    "WebSearch": WebSearch,
    "ReadFile": ReadFile,
    "WriteFile": WriteFile,
}

tools = [
    {
        "name": "Calculator",
        "params": "num1, num2, operator",
        "description": "Performs arithmetic. operator must be one of: add, sub, mul, div.",
    },
    {
        "name": "userPrompt",
        "params": "question",
        "description": "Ask the user a clarifying question. Returns their answer as a string.",
    },
    {
        "name": "get_current_datetime",
        "params": "",
        "description": "Returns the current date and time as a string. No params required.",
    },
    {
        "name": "WebSearch",
        "params": "query",
        "description": "Searches the web using DuckDuckGo. Returns up to 5 results with title, url, and snippet.",
    },
    {
        "name": "ReadFile",
        "params": "path",
        "description": "Reads and returns the contents of a local file at the given path.",
    },
    {
        "name": "WriteFile",
        "params": "path, content",
        "description": "Writes content to a local file at the given path. Creates the file if it does not exist.",
    },
]
system_prompt = f"""You are an AI Agent. ONLY return valid JSON — no prose, no markdown, no code fences.

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

MAX_STEPS = int(os.getenv("MAX_STEPS", 10))

def core_agent(conversation_history, user_message):
    conversation_history.append({"role": "user", "content": user_message})
    result = None
    for step in range(MAX_STEPS):
        raw = chatCompletion(client, conversation_history, model)
        try:
            result = json.loads(extract_json(raw))
        except (TypeError, json.JSONDecodeError) as e:
            raise ValueError(f"Model returned invalid JSON: {e}\nRaw response: {raw}")
        conversation_history.append({"role": "assistant", "content": json.dumps(result)})
        toolReq = result['toolsReq']
        for tool_call in toolReq:
            toolName = tool_call['toolName']
            params = tool_call['params']
            try:
                toolResult = tools_registry[toolName](**params)
            except Exception as e:
                raise RuntimeError(f"Tool '{toolName}' failed with params {params}: {e}") from e
            conversation_history.append({
                "role": "user",
                "content": json.dumps({
                    "tool": toolName,
                    "params": params,
                    "result": toolResult
                })
            })

        if result['isFinalAnswer']:
            break
    else:
        raise RuntimeError(f"Agent exceeded {MAX_STEPS} iterations without a final answer.")

    print(result['response'])


if __name__ == "__main__":
    history = [{"role": "system", "content": system_prompt}]
    try:
        while True:
            try:
                user_input = input("You: ").strip()
            except EOFError:
                break
            if user_input.lower() in ("quit", "exit"):
                break
            if not user_input:
                continue
            core_agent(history, user_input)
    except KeyboardInterrupt:
        pass


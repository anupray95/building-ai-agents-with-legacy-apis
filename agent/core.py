import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from agent.chat import chatCompletion
from agent.tools import tools_registry

load_dotenv()

MAX_STEPS = int(os.getenv("MAX_STEPS", 10))


def get_client():
    return (
        OpenAI(api_key=os.getenv("AI_API_KEY"), base_url=os.getenv("AI_BASE_URL") or None),
        os.getenv("AI_MODEL"),
    )

client, model = get_client()


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


def core_agent(conversation_history, user_message):
    conversation_history.append({"role": "user", "content": user_message})
    result = None
    for _ in range(MAX_STEPS):
        raw = chatCompletion(client, conversation_history, model)
        try:
            result = json.loads(extract_json(raw))
        except (TypeError, json.JSONDecodeError) as e:
            raise ValueError(f"Model returned invalid JSON: {e}\nRaw response: {raw}")
        conversation_history.append({"role": "assistant", "content": json.dumps(result)})
        for tool_call in result['toolsReq']:
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

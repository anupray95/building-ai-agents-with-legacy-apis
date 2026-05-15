import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from chat import chatCompletion

load_dotenv()

def userPrompt(question):
    return input(question+'\n')

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
    "userPrompt": userPrompt
}

tools = [{
    "name": "Calculator",
    "params": '''num1, num2, operator(enum)''',
    "description": '''operator must be one of the below
    add, sub, mul, div
    ''',
},
{
    "name": "userPrompt",
    "params": '''question''',
    "description": '''agent can ask user a question, if it needs to clarify something,
    it will return answer as a string
    ''',
}
]
system_prompt = f"""You are an AI Agent, ONLY RETURN JSON IN THE BELOW FORMAT

JSON Format
=========
{{
    "isFinalAnswer": <Boolean>, // if you dont require any more processing and got the verdict, return this as True, else False
    toolsReq:[{{toolName: <toolName>, params: {{param1: value, param2: value,...}}}}], // list of tools required, along with their param, Note: param1 value is num1 for Calculator tools
    response:<String> // Only return if isFinalAnswer is true, give your answer here, else keep it blank

}}
you have the following tools access{tools}, 

If you already have tool result in userMessage, use that to give answer,
if you required any tools access, give me toolName along with param, I will call the tools and give you result in the next message"""

isFirstMessage = True
def core_agent(system_prompt, user_message,isFirstMessage=True, conversation_history=[]):
    conversation_history = [
        {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_message},]
    while isFirstMessage or result['isFinalAnswer'] == False:
        isFirstMessage = False

        result = chatCompletion(client, system_prompt, conversation_history, user_message, model)
        result = json.loads(extract_json(result))
        conversation_history.append({"role": "assistant", "content": json.dumps(result)})
        toolReq = result['toolsReq']
        if len(toolReq):
            toolName = result['toolsReq'][0]['toolName']
            params = result['toolsReq'][0]['params']

            toolResult = tools_registry[toolName](**params)
            conversation_history.append({"role": "assistant", "content": f'Result for tool {toolName} with params {params} is {toolResult}'})

    content = conversation_history[-1]['content']
    print(json.loads(content)['response'])

user_message = "use tools, calculate this,31246 multiply with 117846"
core_agent(system_prompt, user_message)


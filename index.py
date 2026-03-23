import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from chat import chatCompletion

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

# result = chatCompletion(client, '', [], "31246 *43265691")
# print(result)
# exit(0)


tools = [{
    "name": "Calculator",
    "params": '''num1, num2, operator(enum)''',
    "description": '''operator must be one of the below
    add, sub, mul, div
    ''',
}]
system_prompt = f"""You are a artificial intelligence, ONLY RETURN JSON IN THE BELOW FORMAT

JSON Format
=========
{{
    "isFinalAnswer": <Boolean>, // if you dont require any more processing and got the verdict, return this as True, else False
    toolsReq:[{{toolName, param1: value, param2: value,...}}], // list of tools required, along with their param, Note: param1 value is num1 for Calculator tools
    response:<String> // Only return if isFinalAnswer is true, give your answer here, else keep it blank

}}
you have the following tools access{tools}, If you already have tool result in userMessage, use that to give answer,
if you required any tools access, give me toolName along with param, I will call the tools and give you result in the next message"""


conversation_history = [
    
]

user_message = "use tools, calculate this, 31246 *43265691"

result = chatCompletion(client, system_prompt, conversation_history, user_message)
result = json.loads(result.replace("```json", "").replace("```", "").strip())
print(result)

conversation_history = [
    {"role": "user", "content": "31246 *43265691"},
    {"role": "assistant", "content": json.dumps(result)},
]


{'toolName': 'Calculator', 'num1': 31246, 'num2': 43265691, 'operator': 'mul'}


currTool = result['toolsReq'][0]
toolName = currTool['toolName']
num1 = currTool['num1']
num2 = currTool['num2']
operatorName = currTool['operator']

toolResult = 0
if operatorName == 'mul':
    toolResult = int(num1) * int(num2)


user_message = f"Tool result is {toolResult}" 
result = chatCompletion(client, system_prompt, conversation_history, user_message)
print(result)

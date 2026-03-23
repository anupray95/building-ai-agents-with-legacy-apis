import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

# Legacy Completions API (pre-Chat, most legacy endpoint still active)
response = client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt="Say hello in one word.",
    max_tokens=10,
)

print(response.choices[0].text.strip())

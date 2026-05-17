from datetime import datetime
from ddgs import DDGS


def userPrompt(question):
    return input(question + '\n')

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

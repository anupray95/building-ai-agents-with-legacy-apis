from agent.core import core_agent
from agent.tools import tools, tools_registry
from agent.mcp_bridge import MCPBridge
from agent.prompt import build_system_prompt

bridge = MCPBridge()
mcp_registry, mcp_descriptors = bridge.load()

tools_registry.update(mcp_registry)
all_tools = tools + mcp_descriptors

system_prompt = build_system_prompt(all_tools)

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

import asyncio
import json
from contextlib import asynccontextmanager

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client


class MCPBridge:
    def __init__(self):
        self._server_configs = {}  # server_name -> config

    @asynccontextmanager
    async def _open_session(self, config):
        transport = config.get("transport")
        if transport == "http":
            async with streamablehttp_client(config["url"]) as (r, w, _):
                async with ClientSession(r, w) as session:
                    await session.initialize()
                    yield session
        elif transport == "sse":
            async with sse_client(config["url"]) as (r, w):
                async with ClientSession(r, w) as session:
                    await session.initialize()
                    yield session
        else:
            params = StdioServerParameters(
                command=config["command"],
                args=config.get("args", []),
                env=config.get("env"),
            )
            async with stdio_client(params) as (r, w):
                async with ClientSession(r, w) as session:
                    await session.initialize()
                    yield session

    async def _discover_server(self, config):
        registry = {}
        descriptors = []
        async with self._open_session(config) as session:
            result = await session.list_tools()
            for tool in result.tools:
                props = (tool.inputSchema or {}).get("properties", {})
                descriptors.append({
                    "name": tool.name,
                    "params": ", ".join(props.keys()),
                    "description": tool.description or "",
                })
                registry[tool.name] = self._make_wrapper(tool.name, config)
        return registry, descriptors

    async def _load_all(self, servers):
        all_registry = {}
        all_descriptors = []
        for srv in servers:
            self._server_configs[srv["name"]] = srv
            try:
                reg, desc = await self._discover_server(srv)
                all_registry.update(reg)
                all_descriptors.extend(desc)
                print(f"[MCP] Loaded {len(desc)} tools from '{srv['name']}'")
            except Exception as e:
                print(f"[MCP] Failed to connect to '{srv['name']}': {e}")
        return all_registry, all_descriptors

    def _make_wrapper(self, tool_name, config):
        def wrapper(**kwargs):
            return asyncio.run(self._call_tool(config, tool_name, kwargs))
        return wrapper

    async def _call_tool(self, config, tool_name, args):
        async with self._open_session(config) as session:
            result = await session.call_tool(tool_name, args)
            parts = [c.text for c in result.content if hasattr(c, "text")]
            return "\n".join(parts) if parts else str(result.content)

    def load(self, config_path="mcp.json"):
        try:
            with open(config_path) as f:
                config = json.load(f)
        except FileNotFoundError:
            return {}, []

        servers = config.get("servers", [])
        if not servers:
            return {}, []

        return asyncio.run(self._load_all(servers))

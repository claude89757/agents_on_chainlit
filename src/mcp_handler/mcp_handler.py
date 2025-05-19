import chainlit as cl
from mcp import ClientSession

@cl.on_mcp_connect
async def on_mcp_connect(connection, session: ClientSession):
    print(f"[INFO] MCP {connection.name} connected, of {session}")
    result = await session.list_tools()
    tools = [{
        "name": t.name,
        "description": t.description,
        "input_schema": t.inputSchema,
        } for t in result.tools]
    
    mcp_tools = cl.user_session.get("mcp_tools", {})
    mcp_tools[connection.name] = tools
    cl.user_session.set("mcp_tools", mcp_tools)
    print(f"[INFO] MCP tools: {len(mcp_tools)}")    

@cl.on_mcp_disconnect
async def on_mcp_disconnect(name, session: ClientSession):
    print(f"[INFO] MCP {name} disconnected, of {session}")
    mcp_tools = cl.user_session.get("mcp_tools", {})
    mcp_tools.pop(name, None)
    cl.user_session.set("mcp_tools", mcp_tools)
    print(f"[INFO] MCP tools: {len(mcp_tools)}")

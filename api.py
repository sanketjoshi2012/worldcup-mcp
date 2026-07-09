import os
import asyncio
import json
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack

load_dotenv()

anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
tools = []
mcp_session = None
exit_stack = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global tools, mcp_session, exit_stack
    exit_stack = AsyncExitStack()
    transport = await exit_stack.enter_async_context(
        stdio_client(StdioServerParameters(command="uv", args=["run", "mcp_server.py"]))
    )
    stdio, write = transport
    mcp_session = await exit_stack.enter_async_context(ClientSession(stdio, write))
    await mcp_session.initialize()
    tools_result = await mcp_session.list_tools()
    tools = [
        {"name": t.name, "description": t.description, "input_schema": t.inputSchema}
        for t in tools_result.tools
    ]
    yield
    await exit_stack.aclose()


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.websocket("/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()
    messages = []
    try:
        while True:
            user_input = await websocket.receive_text()
            messages.append({"role": "user", "content": user_input})

            while True:
                response = anthropic.messages.create(
                    model="claude-sonnet-4-5",
                    max_tokens=1024,
                    tools=tools,
                    messages=messages,
                )

                if response.stop_reason == "tool_use":
                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            await websocket.send_text(json.dumps({
                                "type": "tool", "name": block.name
                            }))
                            result = await mcp_session.call_tool(block.name, block.input)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result.content[0].text if result.content else "",
                            })
                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({"role": "user", "content": tool_results})
                else:
                    answer = "".join(b.text for b in response.content if hasattr(b, "text"))
                    messages.append({"role": "assistant", "content": answer})
                    await websocket.send_text(json.dumps({"type": "message", "content": answer}))
                    break

    except WebSocketDisconnect:
        pass

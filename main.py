import asyncio
import os
from dotenv import load_dotenv
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=ANTHROPIC_API_KEY)
messages = []


async def run():
    async with AsyncExitStack() as stack:
        transport = await stack.enter_async_context(
            stdio_client(StdioServerParameters(command="uv", args=["run", "mcp_server.py"]))
        )
        stdio, write = transport
        session = await stack.enter_async_context(ClientSession(stdio, write))
        await session.initialize()

        tools_result = await session.list_tools()
        tools = [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.inputSchema,
            }
            for t in tools_result.tools
        ]

        print("\nWorld Cup 2026 AI Assistant")
        print("Ask me about matches, scores, standings!")
        print("Type 'quit' to exit.\n")

        while True:
            user_input = input("> ").strip()
            if user_input.lower() in ("quit", "exit"):
                break
            if not user_input:
                continue

            messages.append({"role": "user", "content": user_input})

            while True:
                response = client.messages.create(
                    model="claude-sonnet-4-5",
                    max_tokens=1024,
                    tools=tools,
                    messages=messages,
                )

                if response.stop_reason == "tool_use":
                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            print(f"[Fetching {block.name}...]")
                            result = await session.call_tool(block.name, block.input)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result.content[0].text if result.content else "",
                            })

                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({"role": "user", "content": tool_results})
                else:
                    answer = "".join(b.text for b in response.content if hasattr(b, "text"))
                    print(f"\n{answer}\n")
                    messages.append({"role": "assistant", "content": answer})
                    break


if __name__ == "__main__":
    asyncio.run(run())

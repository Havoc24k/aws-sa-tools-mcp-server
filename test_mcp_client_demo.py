#!/usr/bin/env python3
"""MCP Client Demo for AWS MCP Server.

This script demonstrates how to interact with the AWS MCP server using the MCP protocol.
It connects via stdio transport, lists available tools, and tests a sample tool call.
"""

import asyncio
import sys
import traceback

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

# Constants
MAX_ERROR_LENGTH = 100


async def test_mcp_server_simple() -> None:
    """Test the MCP server using the ClientSession."""
    print("🚀 Testing AWS MCP Server with ClientSession")

    try:
        # Set up server parameters
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "aws_mcp_server.server"],
        )

        print("✅ Connecting to server...")

        # Connect to the server via stdio
        async with stdio_client(server_params) as streams:
            read_stream, write_stream = streams
            print("✅ Connected to MCP server via stdio")

            # Create a client session
            async with ClientSession(read_stream, write_stream) as session:
                print("✅ Client session established")

                # Initialize the session
                await session.initialize()
                print("✅ Session initialized")

                # List available tools
                print("\n📋 Listing available tools...")
                tools = await session.list_tools()

                print(f"✅ Found {len(tools.tools)} tools:")
                for i, tool in enumerate(tools.tools, 1):
                    print(f"   {i}. {tool.name}")
                    if tool.description:
                        # Show first line of description
                        desc_lines = tool.description.strip().split("\n")
                        if desc_lines:
                            first_line = desc_lines[0].strip()
                            if first_line:
                                print(f"      {first_line[:70]}...")

                # Test calling a tool with minimal args (will likely fail but shows structure)
                if tools.tools:
                    test_tool = tools.tools[0]
                    print(f"\n🔧 Testing tool: {test_tool.name}")

                    test_args = {
                        "profile_name": "default",
                        "region": "us-east-1",
                    }

                    try:
                        result = await session.call_tool(test_tool.name, test_args)
                        print("✅ Tool call successful!")
                        print(f"   Content items: {len(result.content)}")
                        if result.content:
                            print(f"   First content type: {type(result.content[0])}")
                    except Exception as e:  # noqa: BLE001
                        print("⚠️  Tool call failed (expected due to AWS credentials):")
                        error_str = str(e)
                        if len(error_str) > MAX_ERROR_LENGTH:
                            error_str = error_str[:MAX_ERROR_LENGTH] + "..."
                        print(f"   Error: {error_str}")

                print("\n🎉 MCP client test completed successfully!")

    except Exception as e:  # noqa: BLE001
        print(f"❌ Error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mcp_server_simple())

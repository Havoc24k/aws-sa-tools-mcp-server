#!/usr/bin/env python3
"""
Remote MCP Client for AWS MCP Server
====================================

Connects to AWS MCP Server using FastMCP's HTTP client for remote connections.
Demonstrates how to connect to and interact with a remote MCP server.
"""

import argparse
import asyncio
import json
import logging
import sys
from enum import Enum
from textwrap import shorten
from typing import Any
from urllib.parse import urljoin

try:
    import readline

    HAS_READLINE = True
except ImportError:
    HAS_READLINE = False

from fastmcp import Client

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ClientAction(Enum):
    """Available client actions."""

    LIST_TOOLS = "list_tools"
    TEST_S3 = "test_s3"
    TEST_EC2 = "test_ec2"
    TEST_ALL = "test_all"
    INTERACTIVE = "interactive"


class MCPRemoteClient:
    """Remote MCP client using FastMCP's HTTP client."""

    def __init__(self, host: str = "localhost", port: int = 8888):
        self.host = host
        self.port = port
        base_url = f"http://{host}:{port}"
        self.url = urljoin(base_url, "/sse")
        # Connect to SSE endpoint for remote MCP server
        self.client: Client = Client(self.url)

    async def connect(self):
        """Connect to the remote MCP server."""
        logger.info(f"🔗 Connecting to remote AWS MCP Server at {self.url}...")
        # Connection is handled by the context manager

    def _truncate_description(self, text: str, max_length: int = 80) -> str:
        """Truncate description text using standard library."""
        return shorten(text or "", width=max_length, placeholder="...")

    def _format_tools(self, tools: list) -> list[dict[str, str]]:
        """Format tools for consistent output."""
        return [
            {"name": tool.name, "description": tool.description or ""} for tool in tools
        ]

    def _parse_json_args(self, args_str: str) -> dict[str, Any]:
        """Parse JSON arguments with proper error handling."""
        try:
            return json.loads(args_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON arguments: {e}") from e

    async def list_tools(self) -> list[dict[str, Any]]:
        """List available MCP tools."""
        logger.info("📋 Listing available tools from remote server...")

        async with self.client:
            await self.client.ping()
            tools = await self.client.list_tools()
            tools_dict = self._format_tools(tools)
            logger.info(f"✅ Found {len(tools_dict)} tools")
            return tools_dict

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Call an MCP tool on the remote server."""
        logger.info(f"🔧 Calling remote tool: {name}")

        async with self.client:
            result = await self.client.call_tool(name, arguments)
            logger.info("✅ Tool executed successfully")
            return result

    async def test_aws_tool(
        self, tool_name: str, profile: str = "default", region: str = "us-east-1"
    ) -> None:
        """Test an AWS tool with error handling."""
        result = await self.call_tool(
            tool_name, {"profile_name": profile, "region": region}
        )

        # Format results for different tool types
        if (
            tool_name == "s3-list_buckets"
            and isinstance(result, dict)
            and "Buckets" in result
        ):
            buckets = result["Buckets"]
            logger.info(f"  📦 Found {len(buckets)} S3 buckets")
            for bucket in buckets[:3]:
                logger.info(f"    - {bucket.get('Name', 'Unknown')}")
            if len(buckets) > 3:
                logger.info(f"    ... and {len(buckets) - 3} more")
        elif (
            tool_name == "ec2-describe_instances"
            and isinstance(result, dict)
            and "Reservations" in result
        ):
            reservations = result["Reservations"]
            total_instances = sum(len(r.get("Instances", [])) for r in reservations)
            logger.info(
                f"  🖥️ Found {total_instances} instances in {len(reservations)} reservations"
            )
        else:
            logger.info(f"  📄 Response: {str(result)[:200]}...")

    async def interactive_mode(self) -> None:
        """Interactive mode for MCP communication."""
        logger.info(
            "🎯 Entering interactive mode. Type 'help' for commands or 'quit' to exit."
        )

        # Setup readline for better terminal experience
        if HAS_READLINE:
            # Enable tab completion and history
            readline.set_completer_delims(" \t\n")
            readline.parse_and_bind("tab: complete")
            # Enable command history
            try:
                readline.read_history_file()
            except FileNotFoundError:
                pass  # No history file yet
        else:
            print("⚠️  For better terminal experience, install readline support")

        tools = await self.list_tools()
        tool_names = [tool["name"] for tool in tools]

        # Setup command completion
        if HAS_READLINE:
            commands = ["help", "quit", "exit", "list_tools", "call"] + tool_names

            def completer(text: str, state: int) -> str | None:
                options = [cmd for cmd in commands if cmd.startswith(text)]
                if state < len(options):
                    return options[state]
                return None

            readline.set_completer(completer)

        # Show available tools
        print("\n📋 Available tools:")
        for i, tool in enumerate(tools, 1):
            print(f"  {i:2d}. {tool['name']}")
            if tool["description"]:
                desc = self._truncate_description(tool["description"])
                print(f"      {desc}")

        try:
            while True:
                try:
                    command = input("\nmcp> ").strip()
                except EOFError:
                    break

                if command.lower() in ["quit", "exit", "q"]:
                    break
                elif command.lower() == "help":
                    self._show_help()
                elif command.lower() == "list_tools":
                    await self._show_tools_interactive()
                elif command.startswith("call "):
                    await self._handle_tool_call_interactive(command[5:], tool_names)
                else:
                    if command:  # Only show error for non-empty commands
                        print(
                            f"Unknown command: {command}. Type 'help' for available commands."
                        )
        except KeyboardInterrupt:
            print("\n")  # Clean newline after Ctrl+C
        finally:
            # Save command history
            if HAS_READLINE:
                try:
                    readline.write_history_file()
                except Exception:
                    pass  # Ignore history save errors

        logger.info("Exiting interactive mode")

    def _show_help(self) -> None:
        """Show interactive help."""
        print("\nAvailable commands:")
        print("  list_tools - List all available tools")
        print("  call <tool_name> <json_args> - Call a tool with JSON arguments")
        print("  quit/exit/q - Exit interactive mode")
        print(
            '\nExample: call s3-list_buckets {"profile_name": "default", "region": "us-east-1"}'
        )

    async def _show_tools_interactive(self) -> None:
        """Show tools in interactive mode."""
        tools = await self.list_tools()
        print(f"\n📋 Available {len(tools)} tools:")
        for tool in tools:
            desc = self._truncate_description(tool["description"])
            print(f"  • {tool['name']}: {desc}")

    async def _handle_tool_call_interactive(
        self, call_args: str, tool_names: list[str]
    ) -> None:
        """Handle interactive tool call."""
        parts = call_args.split(" ", 1)
        if len(parts) != 2:
            print("Usage: call <tool_name> <json_args>")
            return

        tool_name, args_str = parts
        if tool_name not in tool_names:
            print(f"❌ Unknown tool: {tool_name}")
            print(f"Available tools: {', '.join(tool_names[:5])}...")
            return

        try:
            args = self._parse_json_args(args_str)
            result = await self.call_tool(tool_name, args)

            # Extract actual JSON data from CallToolResult
            if (
                hasattr(result, "content")
                and result.content
                and hasattr(result.content[0], "text")
            ):
                json_data = json.loads(result.content[0].text)
            else:
                json_data = result

            # Format JSON response with colors if possible
            try:
                from pygments import highlight  # type: ignore[import-untyped]
                from pygments.formatters import TerminalFormatter  # type: ignore[import-untyped]
                from pygments.lexers import JsonLexer  # type: ignore[import-untyped]

                json_str = json.dumps(
                    json_data, indent=2, default=str, ensure_ascii=False
                )
                formatted = highlight(json_str, JsonLexer(), TerminalFormatter())
                print(f"\n📄 Result:\n{formatted}")
            except ImportError:
                # Fallback to regular JSON formatting
                json_str = json.dumps(
                    json_data, indent=2, default=str, ensure_ascii=False
                )
                print(f"\n📄 Result:\n{json_str}")

        except ValueError as e:
            print(f"❌ {e}")
        except Exception as e:
            print(f"❌ Tool call error: {e}")

    async def run_action(self, action: str, **kwargs: Any) -> None:
        """Run specified action."""
        try:
            await self.connect()

            if action == ClientAction.LIST_TOOLS.value:
                tools = await self.list_tools()
                print(f"\n📋 Available {len(tools)} MCP tools:")
                for i, tool in enumerate(tools, 1):
                    print(f"  {i:2d}. {tool['name']}")
                    if tool["description"]:
                        desc = self._truncate_description(tool["description"], 100)
                        print(f"      {desc}")

            elif action == ClientAction.TEST_S3.value:
                await self.test_aws_tool("s3-list_buckets", **kwargs)

            elif action == ClientAction.TEST_EC2.value:
                await self.test_aws_tool("ec2-describe_instances", **kwargs)

            elif action == ClientAction.TEST_ALL.value:
                await self.test_aws_tool("s3-list_buckets", **kwargs)
                await self.test_aws_tool("ec2-describe_instances", **kwargs)

            elif action == ClientAction.INTERACTIVE.value:
                await self.interactive_mode()

            else:
                logger.error(f"❌ Unknown action: {action}")

        except Exception as e:
            logger.error(f"❌ Client error: {e}")
            raise


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Remote MCP Client for AWS MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (default)
  python client/mcp_json_rpc_client.py

  # List all available tools
  python client/mcp_json_rpc_client.py --action list_tools

  # Test S3 tools
  python client/mcp_json_rpc_client.py --action test_s3 --profile prod --region us-west-2
        """,
    )

    parser.add_argument(
        "--host", default="localhost", help="Server host (default: localhost)"
    )
    parser.add_argument(
        "--port", type=int, default=8888, help="Server port (default: 8888)"
    )
    parser.add_argument(
        "--action",
        choices=[action.value for action in ClientAction],
        default=ClientAction.INTERACTIVE.value,
        help="Action to perform (default: interactive)",
    )
    parser.add_argument(
        "--profile", default="default", help="AWS profile name (default: default)"
    )
    parser.add_argument(
        "--region", default="us-east-1", help="AWS region (default: us-east-1)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    print("=" * 60)
    print("AWS MCP Server - Remote Client")
    print("=" * 60)
    print(f"Target: {args.host}:{args.port}")
    print(f"Action: {args.action}")
    print(f"AWS Profile: {args.profile}, Region: {args.region}")

    client = MCPRemoteClient(host=args.host, port=args.port)
    kwargs = {"profile": args.profile, "region": args.region}

    try:
        await client.run_action(args.action, **kwargs)
        print("\n🎉 Client completed successfully!")
    except KeyboardInterrupt:
        logger.info("⚠️ Client interrupted by user")
    except Exception as e:
        logger.error(f"❌ Client failed: {e}")
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure AWS MCP Server is running")
        print("2. Check AWS credentials are configured")
        print("3. Verify the server is accessible")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

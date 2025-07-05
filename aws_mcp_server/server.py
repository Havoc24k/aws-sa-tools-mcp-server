import argparse
from .mcp import mcp


def main():
    """Run the MCP server with CLI argument support."""
    parser = argparse.ArgumentParser(
        description='A Model Context Protocol (MCP) server')
    parser.add_argument('--sse', action='store_true', help='Use SSE transport')
    parser.add_argument('--port', type=int, default=8888,
                        help='Port to run the server on')

    args = parser.parse_args()

    # Run server with appropriate transport
    if args.sse:
        mcp.settings.port = args.port
        mcp.run(transport='sse')
    else:
        # Initialize and run the server
        mcp.run(transport='stdio')


if __name__ == '__main__':
    main()

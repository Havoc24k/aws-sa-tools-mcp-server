import argparse
import os

from .logging_config import setup_logging
from .mcp import mcp


def main() -> None:
    """Run the MCP server with CLI argument support."""
    parser = argparse.ArgumentParser(
        description="A Model Context Protocol (MCP) server"
    )
    parser.add_argument("--sse", action="store_true", help="Use SSE transport")
    parser.add_argument(
        "--port", type=int, default=8888, help="Port to run the server on"
    )
    parser.add_argument(
        "--enable-vector-store",
        action="store_true",
        default=False,
        help="Enable vector store and document management features (default: False)",
    )
    parser.add_argument(
        "--data-source",
        type=str,
        default="datasource/",
        help="Path to data source directory for automatic ingestion (default: datasource/)",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default="logs/aws_mcp_server.log",
        help="Path to log file (default: logs/aws_mcp_server.log)",
    )

    args = parser.parse_args()

    # Set up logging with file output
    setup_logging(level="INFO", include_timestamp=False,
                  log_file=args.log_file)

    # Set environment variables for vector store based on CLI flags
    os.environ["ENABLE_VECTOR_STORE"] = str(args.enable_vector_store).lower()
    os.environ["DATA_SOURCE_PATH"] = args.data_source

    # Initialize vector store if enabled
    if args.enable_vector_store:
        from .services.knowledge.vector_store_init import initialize_vector_store

        initialize_vector_store(args.data_source)

    # Run server with appropriate transport
    if args.sse:
        mcp.settings.port = args.port
        mcp.run(transport="sse")
    else:
        # Initialize and run the server
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

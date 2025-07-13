# Multi-stage build for minimal production image
FROM cgr.dev/chainguard/python:latest-dev AS builder

WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY aws_mcp_server/ ./aws_mcp_server/

# Install dependencies using uv
RUN uv sync --no-dev

# Production stage - distroless runtime (no shell, no package managers)
FROM cgr.dev/chainguard/python:latest

WORKDIR /app

# Copy built application and dependencies from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/aws_mcp_server /app/aws_mcp_server
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

# Expose port for SSE mode
EXPOSE 8888

# Set PATH to include virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Set entrypoint for proper argument handling
ENTRYPOINT ["python", "-m", "aws_mcp_server.server"]

# Default arguments for SSE mode
CMD ["--sse", "--port", "8888"]

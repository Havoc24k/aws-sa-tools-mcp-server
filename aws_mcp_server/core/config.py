"""Modern configuration using dataclasses with validation."""

import os
from dataclasses import dataclass, field
from typing import Final, Literal


@dataclass(slots=True, frozen=True)
class ServerConfig:
    """Server configuration with validation."""
    port: int = field(default_factory=lambda: int(os.getenv("AWS_MCP_PORT", "8888")))
    transport: str = field(default_factory=lambda: os.getenv("AWS_MCP_TRANSPORT", "stdio"))
    debug: bool = field(default_factory=lambda: os.getenv("AWS_MCP_DEBUG", "false").lower() == "true")
    log_file: str = field(default_factory=lambda: os.getenv("AWS_MCP_LOG_FILE", "logs/aws_mcp_server.log"))

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if not 1024 <= self.port <= 65535:
            raise ValueError(f"Port must be between 1024 and 65535, got {self.port}")
        if self.transport not in ("stdio", "sse"):
            raise ValueError(f"Transport must be 'stdio' or 'sse', got {self.transport}")


@dataclass(slots=True, frozen=True)
class AWSConfig:
    """AWS configuration with defaults."""
    default_region: str = field(default_factory=lambda: os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
    default_profile: str = field(default_factory=lambda: os.getenv("AWS_PROFILE", "default"))
    max_concurrent: int = field(default_factory=lambda: int(os.getenv("AWS_MCP_MAX_CONCURRENT", "10")))
    max_results: int = field(default_factory=lambda: int(os.getenv("AWS_MCP_MAX_RESULTS", "1000")))
    timeout_seconds: int = field(default_factory=lambda: int(os.getenv("AWS_MCP_TIMEOUT", "30")))
    enable_pagination: bool = field(default_factory=lambda: os.getenv("AWS_MCP_ENABLE_PAGINATION", "true").lower() == "true")

    def __post_init__(self) -> None:
        """Validate AWS configuration."""
        if self.max_concurrent < 1:
            raise ValueError(f"max_concurrent must be positive, got {self.max_concurrent}")
        if self.max_results < 1:
            raise ValueError(f"max_results must be positive, got {self.max_results}")
        if self.timeout_seconds < 1:
            raise ValueError(f"timeout_seconds must be positive, got {self.timeout_seconds}")


@dataclass(slots=True, frozen=True)
class VectorStoreConfig:
    """Vector store configuration."""
    enabled: bool = field(default_factory=lambda: os.getenv("ENABLE_VECTOR_STORE", "true").lower() == "true")
    db_path: str = field(default_factory=lambda: os.getenv("CHROMA_DB_PATH", "./chroma_db"))
    collection_name: str = field(default_factory=lambda: os.getenv("COLLECTION_NAME", "aws_docs"))


# Singleton instances
SERVER_CONFIG: Final[ServerConfig] = ServerConfig()
AWS_CONFIG: Final[AWSConfig] = AWSConfig()
VECTOR_CONFIG: Final[VectorStoreConfig] = VectorStoreConfig()

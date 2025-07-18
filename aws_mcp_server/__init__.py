# Import all AWS service modules to register MCP tools
import os

from .logging_config import get_logger
from .services.auth import sso
from .services.billing import ce
from .services.compute import ec2
from .services.database import rds
from .services.generic import sdk_wrapper
from .services.monitoring import cloudwatch
from .services.storage import s3

# Get logger for this module
logger = get_logger(__name__)

# Simple vector store enabling - only check environment variable
ENABLE_VECTOR_STORE = os.getenv("ENABLE_VECTOR_STORE", "false").lower() == "true"

if ENABLE_VECTOR_STORE:
    try:
        from .services.knowledge import (
            document_management,
            generic_pdf_ingestion,
            vector_store,
        )

        logger.info("Vector store and document management features enabled")
    except ImportError as e:
        logger.warning(f"Failed to import vector store modules: {e}")
        logger.warning("Vector store features will be unavailable")
else:
    logger.info(
        "Vector store features disabled (set ENABLE_VECTOR_STORE=true to enable)"
    )

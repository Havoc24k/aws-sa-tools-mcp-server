"""
Vector Store Initialization and Auto-Sync
Handles automatic initialization and syncing of the vector store with a data source directory
"""

import asyncio
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ...logging_config import get_logger
from .generic_pdf_ingestion import pdf_ingest_from_file
from .vector_store import vector_store_info, vector_store_reset

# File index to track ingested documents
INDEX_FILE = "vector_store_index.json"

# Get logger for this module
logger = get_logger(__name__)


def initialize_vector_store(data_source_path: str) -> None:
    """
    Initialize vector store and sync with data source directory
    This is the main entry point called by server.py

    Args:
        data_source_path: Path to the data source directory
    """
    import sys

    logger.info("Initializing Vector Store")
    logger.info(f"Data Source: {data_source_path}")
    logger.info("─" * 60)

    # Create data source directory if it doesn't exist
    Path(data_source_path).mkdir(parents=True, exist_ok=True)

    # Run async initialization with progress reporting
    try:
        asyncio.run(_async_initialize_vector_store(data_source_path))
        logger.info("─" * 60)
        logger.info("Vector Store initialization completed successfully!")
        logger.info("Server ready to handle document queries")
    except Exception as e:
        logger.error("─" * 60)
        logger.error(f"Vector Store initialization failed: {e}")
        logger.warning("Server will start without vector store functionality")
        # Don't exit - let the server start without vector store

    logger.info("")  # Add blank line before server starts


async def _async_initialize_vector_store(data_source_path: str) -> None:
    """Async version of vector store initialization"""

    # Step 1: Check if vector store exists
    logger.info("Checking vector store status...")
    info_result = await vector_store_info()

    if info_result["success"]:
        document_count = info_result["current_collection"]["count"]
        logger.info(f"Vector store found with {document_count} documents")
    else:
        logger.info("Vector store not found, will create new one")
        document_count = 0

    # Step 2: Load existing file index
    index_path = Path(INDEX_FILE)
    file_index = load_file_index(index_path)

    if file_index:
        logger.info(f"Loaded index with {len(file_index)} tracked files")
    else:
        logger.info("No existing index found, creating new one")
        file_index = {}

    # Step 3: Scan data source directory for files
    logger.info(f"Scanning data source directory: {data_source_path}")
    source_files = scan_data_source(data_source_path)

    if not source_files:
        logger.info(f"No supported files found in {data_source_path}")
        logger.info("Supported formats: .pdf")
        logger.info(f"Add PDF files to {data_source_path} and restart the server")
        return

    logger.info(f"Found {len(source_files)} files to process")
    for i, file_path in enumerate(source_files, 1):
        file_size_mb = file_path.stat().st_size / 1024 / 1024
        logger.info(f"  {i}. {file_path.name} ({file_size_mb:.1f} MB)")

    # Step 4: Sync files (ingest new/modified files)
    logger.info("Syncing files with vector store...")
    updated_index = await sync_files_to_vector_store(source_files, file_index)

    # Step 5: Save updated index
    save_file_index(index_path, updated_index)

    # Step 6: Show final status
    final_info = await vector_store_info()
    if final_info["success"]:
        final_count = final_info["current_collection"]["count"]
        logger.info("Vector Store Ready!")
        logger.info(f"Total document chunks: {final_count}")
        logger.info(f"Tracked files: {len(updated_index)}")
        logger.info("Ready to serve document queries!")
    else:
        logger.error("Vector store status check failed")


def scan_data_source(data_source_path: str) -> list[Path]:
    """
    Scan data source directory for supported files

    Args:
        data_source_path: Path to scan

    Returns:
        List of supported file paths
    """
    supported_extensions = {".pdf"}
    source_path = Path(data_source_path)

    if not source_path.exists():
        return []

    files = []
    for file_path in source_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            files.append(file_path)

    return sorted(files)


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of file for change detection"""
    hasher = hashlib.sha256()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def load_file_index(index_path: Path) -> dict[str, Any]:
    """Load file index from JSON file"""
    if not index_path.exists():
        return {}

    try:
        with open(index_path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.warning(f"Error loading index file: {e}")
        return {}


def save_file_index(index_path: Path, file_index: dict[str, Any]) -> None:
    """Save file index to JSON file"""
    try:
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(file_index, f, indent=2, ensure_ascii=False)
    except OSError as e:
        logger.warning(f"Error saving index file: {e}")


async def sync_files_to_vector_store(
    source_files: list[Path], file_index: dict[str, Any]
) -> dict[str, Any]:
    """
    Sync files to vector store, only ingesting new or modified files

    Args:
        source_files: List of source files to check
        file_index: Current file index

    Returns:
        Updated file index
    """
    updated_index = file_index.copy()
    new_files = 0
    updated_files = 0
    skipped_files = 0

    total_files = len(source_files)

    for idx, file_path in enumerate(source_files, 1):
        file_key = str(file_path)
        file_stats = file_path.stat()

        logger.info(f"[{idx}/{total_files}] Processing {file_path.name}...")

        # Calculate file hash
        try:
            file_hash = calculate_file_hash(file_path)
        except OSError as e:
            logger.warning(f"Error reading file: {e}")
            continue

        # Check if file needs to be processed
        existing_entry = file_index.get(file_key, {})
        existing_hash = existing_entry.get("hash")

        if existing_hash == file_hash:
            logger.info("Skipped (unchanged)")
            skipped_files += 1
            continue

        # File is new or modified, ingest it
        is_new = existing_hash is None
        status = "new" if is_new else "modified"
        file_size_mb = file_stats.st_size / 1024 / 1024
        logger.info(f"Ingesting ({status}, {file_size_mb:.1f} MB)...")

        try:
            # Determine document category based on file location or name
            category, doc_type, tags = categorize_file(file_path)

            # Ingest the file
            result = await pdf_ingest_from_file(
                pdf_path=str(file_path),
                document_title=file_path.stem,
                category=category,
                doc_type=doc_type,
                tags=tags + ["auto_synced"],
                metadata={
                    "source_file": str(file_path),
                    "auto_synced": True,
                    "sync_timestamp": datetime.now().isoformat(),
                },
                collection_name="documents",
            )

            if result["success"]:
                # Update index entry
                updated_index[file_key] = {
                    "hash": file_hash,
                    "size": file_stats.st_size,
                    "modified_time": file_stats.st_mtime,
                    "ingested_at": datetime.now().isoformat(),
                    "document_title": result["document_title"],
                    "chunks_created": result.get("chunks_created", 0),
                    "category": category,
                    "doc_type": doc_type,
                    "tags": tags,
                }

                if is_new:
                    new_files += 1
                else:
                    updated_files += 1

                chunks_count = result.get("chunks_created", 0)
                text_length = result.get("total_text_length", 0)
                logger.info(
                    f"Success! Added {chunks_count} chunks ({text_length:,} chars)"
                )
            else:
                logger.error(f"Failed: {result['error']}")

        except Exception as e:
            logger.error(f"Error ingesting file: {e}")

    # Summary
    logger.info("Sync Summary:")
    logger.info(f"New files: {new_files}")
    logger.info(f"Updated files: {updated_files}")
    logger.info(f"Skipped files: {skipped_files}")
    logger.info(f"Total processed: {new_files + updated_files}/{total_files}")

    return updated_index


def categorize_file(file_path: Path) -> tuple[str, str, list[str]]:
    """
    Automatically categorize a file based on its path and name

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (category, doc_type, tags)
    """
    path_parts = [part.lower() for part in file_path.parts]
    file_name = file_path.name.lower()

    # Check path for category indicators
    if any(
        keyword in path_parts for keyword in ["aws", "cloud", "documentation", "docs"]
    ):
        return "technical", "documentation", ["aws", "cloud"]

    if any(keyword in path_parts for keyword in ["policy", "compliance", "governance"]):
        return "business", "policy", ["policy", "compliance"]

    if any(keyword in path_parts for keyword in ["manual", "guide", "reference"]):
        return "technical", "manual", ["manual", "reference"]

    if any(keyword in path_parts for keyword in ["tutorial", "training", "course"]):
        return "educational", "tutorial", ["tutorial", "training"]

    if any(keyword in path_parts for keyword in ["research", "paper", "study"]):
        return "research", "paper", ["research", "study"]

    if any(keyword in path_parts for keyword in ["legal", "contract", "terms"]):
        return "legal", "contract", ["legal", "contract"]

    # Check filename for specific indicators
    if any(
        keyword in file_name
        for keyword in ["wellarchitected", "well-architected", "framework"]
    ):
        return "technical", "documentation", ["aws", "framework", "best-practices"]

    if any(keyword in file_name for keyword in ["manual", "guide", "reference"]):
        return "technical", "manual", ["manual", "reference"]

    if any(keyword in file_name for keyword in ["policy", "procedure"]):
        return "business", "policy", ["policy", "procedure"]

    # Default categorization
    return "general", "documentation", ["general"]


def get_vector_store_status() -> dict[str, Any]:
    """
    Get current vector store status synchronously
    Helper function for use in other modules
    """
    try:
        return asyncio.run(vector_store_info())
    except Exception as e:
        return {"success": False, "error": f"Failed to get vector store status: {e}"}


def get_file_index_status() -> dict[str, Any]:
    """Get current file index status"""
    index_path = Path(INDEX_FILE)

    if not index_path.exists():
        return {"exists": False, "file_count": 0, "index_file": str(index_path)}

    try:
        file_index = load_file_index(index_path)
        return {
            "exists": True,
            "file_count": len(file_index),
            "index_file": str(index_path),
            "files": list(file_index.keys()),
        }
    except Exception as e:
        return {
            "exists": True,
            "error": f"Failed to read index: {e}",
            "index_file": str(index_path),
        }

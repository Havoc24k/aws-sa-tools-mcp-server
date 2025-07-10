"""
Generic document management for MCP Server vector store
Handles any type of document with flexible categorization and metadata
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Union

from ...mcp import mcp
from .vector_store import vector_store_add, vector_store_info, vector_store_search

# Document categories and types
DOCUMENT_CATEGORIES = {
    "technical": ["documentation", "manual", "guide", "reference", "api"],
    "business": ["policy", "procedure", "compliance", "governance", "strategy"],
    "educational": ["tutorial", "course", "lesson", "training", "workshop"],
    "legal": ["contract", "agreement", "terms", "privacy", "regulation"],
    "research": ["paper", "study", "analysis", "report", "whitepaper"],
    "general": ["misc", "other", "uncategorized"],
}

SOURCE_TYPES = ["pdf", "web", "file", "api", "manual"]


@mcp.tool(
    name="document_ingest",
    description="Ingest any document into the vector store with flexible metadata",
)
async def document_ingest(
    content: str | list[str],
    document_title: str,
    source_type: str = "manual",
    category: str = "general",
    doc_type: str = "documentation",
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
    collection_name: str = "documents",
    chunk_size: int = 1200,
    overlap_size: int = 200,
) -> dict[str, Any]:
    """
    Ingest any document content into the vector store

    Args:
        content: Document content (string or list of strings)
        document_title: Human-readable title for the document
        source_type: Type of source (pdf, web, file, api, manual)
        category: Document category (technical, business, educational, legal, research, general)
        doc_type: Specific document type (documentation, manual, guide, etc.)
        tags: Optional list of tags for categorization
        metadata: Additional custom metadata
        collection_name: Vector store collection name
        chunk_size: Size of text chunks for embedding
        overlap_size: Overlap between chunks to maintain context

    Returns:
        Dictionary with ingestion results
    """
    try:
        # Validate inputs
        if not content or not document_title:
            return {
                "success": False,
                "error": "Content and document title are required",
            }

        # Convert content to string if it's a list
        if isinstance(content, list):
            text_content = "\n\n".join(content)
        else:
            text_content = content

        # Validate category
        if category not in DOCUMENT_CATEGORIES:
            category = "general"

        # Create chunks
        chunks = create_smart_chunks(text_content, chunk_size, overlap_size)

        # Prepare base metadata (ChromaDB requires scalar values)
        base_metadata = {
            "document_title": document_title,
            "source_type": source_type,
            "category": category,
            "doc_type": doc_type,
            "tags": ",".join(tags or []),  # Convert list to comma-separated string
            "ingested_at": datetime.now().isoformat(),
            "content_length": len(text_content),
            **(metadata or {}),
        }

        # Create chunk metadata and IDs
        safe_title = create_safe_document_id(document_title)

        # Use list comprehensions for Pythonic code
        chunk_metadatas = [
            {
                **base_metadata,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "chunk_size": len(chunk),
            }
            for i, chunk in enumerate(chunks)
        ]

        chunk_ids = [f"{safe_title}_chunk_{i:04d}" for i in range(len(chunks))]

        # Add to vector store
        result = await vector_store_add(
            documents=chunks,
            ids=chunk_ids,
            metadatas=chunk_metadatas,
            collection_name=collection_name,
        )

        if result["success"]:
            result.update(
                {
                    "document_title": document_title,
                    "category": category,
                    "doc_type": doc_type,
                    "total_text_length": len(text_content),
                    "chunks_created": len(chunks),
                    "safe_document_id": safe_title,
                }
            )

        return result

    except Exception as e:
        return {"success": False, "error": f"Document ingestion failed: {str(e)}"}


@mcp.tool(
    name="document_search",
    description="Search documents with category and type filtering",
)
async def document_search(
    query: str,
    category: str | None = None,
    doc_type: str | None = None,
    tags: list[str] | None = None,
    collection_name: str = "documents",
    n_results: int = 5,
) -> dict[str, Any]:
    """
    Search documents with filtering by category, type, and tags

    Args:
        query: Search query text
        category: Filter by document category
        doc_type: Filter by document type
        tags: Filter by tags (documents must have at least one matching tag)
        collection_name: Vector store collection name
        n_results: Maximum number of results to return

    Returns:
        Dictionary with search results
    """
    try:
        # Perform initial search
        search_result = await vector_store_search(
            query=query,
            n_results=n_results * 3,  # Get more results for filtering
            collection_name=collection_name,
            include_distances=True,
        )

        if not search_result["success"]:
            return search_result

        # Filter results based on criteria
        filtered_results = []

        for result in search_result["results"]:
            metadata = result["metadata"]

            # Category filter
            if category and metadata.get("category") != category:
                continue

            # Doc type filter
            if doc_type and metadata.get("doc_type") != doc_type:
                continue

            # Tags filter
            if tags:
                result_tags_str = metadata.get("tags", "")
                result_tags = result_tags_str.split(",") if result_tags_str else []
                if not any(tag in result_tags for tag in tags):
                    continue

            # Add additional fields for display
            result["category"] = metadata.get("category", "unknown")
            result["doc_type"] = metadata.get("doc_type", "unknown")
            tags_str = metadata.get("tags", "")
            result["tags"] = tags_str.split(",") if tags_str else []
            result["document_title"] = metadata.get("document_title", "Untitled")

            filtered_results.append(result)

            if len(filtered_results) >= n_results:
                break

        return {
            "success": True,
            "query": query,
            "filters": {"category": category, "doc_type": doc_type, "tags": tags},
            "results": filtered_results,
            "total_found": len(filtered_results),
            "searched_collection": collection_name,
        }

    except Exception as e:
        return {"success": False, "error": f"Document search failed: {str(e)}"}


@mcp.tool(
    name="document_list",
    description="List all documents in the vector store with metadata",
)
async def document_list(
    collection_name: str = "documents",
    category: str | None = None,
    doc_type: str | None = None,
) -> dict[str, Any]:
    """
    List all documents with their metadata

    Args:
        collection_name: Vector store collection name
        category: Filter by category
        doc_type: Filter by document type

    Returns:
        Dictionary with document list
    """
    try:
        # Get collection info
        info_result = await vector_store_info(collection_name)

        if not info_result["success"]:
            return info_result

        # For now, we'll use a search to get all documents
        # In a real implementation, you'd query the collection directly
        all_docs_result = await vector_store_search(
            query="",  # Empty query to get diverse results
            n_results=min(info_result["current_collection"]["count"], 100),
            collection_name=collection_name,
        )

        if not all_docs_result["success"]:
            return all_docs_result

        # Group documents by title and extract unique documents
        documents = {}

        for result in all_docs_result["results"]:
            metadata = result["metadata"]
            doc_title = metadata.get("document_title", "Untitled")

            # Apply filters
            if category and metadata.get("category") != category:
                continue
            if doc_type and metadata.get("doc_type") != doc_type:
                continue

            if doc_title not in documents:
                tags_str = metadata.get("tags", "")
                tags_list = tags_str.split(",") if tags_str else []
                documents[doc_title] = {
                    "title": doc_title,
                    "category": metadata.get("category", "unknown"),
                    "doc_type": metadata.get("doc_type", "unknown"),
                    "source_type": metadata.get("source_type", "unknown"),
                    "tags": tags_list,
                    "ingested_at": metadata.get("ingested_at", "unknown"),
                    "total_chunks": metadata.get("total_chunks", 1),
                    "content_length": metadata.get("content_length", 0),
                }

        return {
            "success": True,
            "collection": collection_name,
            "filters": {"category": category, "doc_type": doc_type},
            "documents": list(documents.values()),
            "total_documents": len(documents),
            "total_chunks": info_result["current_collection"]["count"],
        }

    except Exception as e:
        return {"success": False, "error": f"Document listing failed: {str(e)}"}


@mcp.tool(
    name="document_categories",
    description="Get available document categories and types",
)
async def document_categories() -> dict[str, Any]:
    """
    Get available document categories and types for classification

    Returns:
        Dictionary with available categories and types
    """
    return {
        "success": True,
        "categories": DOCUMENT_CATEGORIES,
        "source_types": SOURCE_TYPES,
        "usage": {
            "categories": "High-level classification of document purpose",
            "doc_types": "Specific type within each category",
            "source_types": "How the document was ingested",
            "tags": "Custom labels for flexible categorization",
        },
    }


def create_smart_chunks(text: str, chunk_size: int, overlap_size: int) -> list[str]:
    """Create simple text chunks with sentence boundary detection"""
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        if end >= len(text):
            chunks.append(text[start:].strip())
            break

        # Find last sentence ending before chunk limit using walrus operator
        chunk_text = text[start:end]

        if (sentence_end := chunk_text.rfind(". ")) > chunk_size * 0.5:
            chunks.append(text[start : start + sentence_end + 1].strip())
            start = start + sentence_end + 1 - overlap_size
        else:
            chunks.append(chunk_text)
            start = end - overlap_size

    return [chunk for chunk in chunks if chunk.strip()]


def create_safe_document_id(title: str) -> str:
    """Create a safe ID from document title"""
    # Convert to lowercase and replace spaces/special chars with underscores
    safe_id = re.sub(r"[^a-zA-Z0-9_-]", "_", title.lower().strip())
    # Remove multiple consecutive underscores
    safe_id = re.sub(r"_+", "_", safe_id)
    # Remove leading/trailing underscores
    safe_id = safe_id.strip("_")
    # Limit length
    if len(safe_id) > 50:
        safe_id = safe_id[:50].rstrip("_")

    return safe_id or "untitled_document"

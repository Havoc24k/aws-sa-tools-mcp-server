"""
Simple Chroma vector store integration for AWS MCP Server
"""

import os
from pathlib import Path
from typing import Any, Optional

import chromadb
from chromadb.config import Settings

from ...mcp import mcp

# Simple configuration constants
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
COLLECTION_NAME = "aws_docs"

# Initialize Chroma client with persistent storage
chroma_client = chromadb.PersistentClient(
    path=CHROMA_DB_PATH, settings=Settings(allow_reset=True)
)


def get_or_create_collection(collection_name: str = COLLECTION_NAME) -> Any:
    """Get or create a Chroma collection"""
    try:
        return chroma_client.get_collection(name=collection_name)
    except Exception:
        return chroma_client.create_collection(
            name=collection_name,
            metadata={"description": "AWS documentation and knowledge base"},
        )


@mcp.tool(
    name="vector_store_add",
    description="Add documents to the vector store for semantic search",
)
async def vector_store_add(
    documents: list[str],
    ids: list[str] | None = None,
    metadatas: list[dict[str, Any]] | None = None,
    collection_name: str = COLLECTION_NAME,
) -> dict[str, Any]:
    """
    Add documents to the vector store

    Args:
        documents: List of document texts to add
        ids: Optional list of document IDs (will auto-generate if not provided)
        metadatas: Optional list of metadata dictionaries for each document
        collection_name: Name of the collection to add to

    Returns:
        Dictionary with success status and added document count
    """
    try:
        collection = get_or_create_collection(collection_name)

        # Auto-generate IDs if not provided
        if ids is None:
            existing_count = collection.count()
            ids = [f"doc_{existing_count + i}" for i in range(len(documents))]

        # Add default metadata if not provided
        if metadatas is None:
            metadatas = [{"type": "general"} for _ in documents]

        # Add documents to collection
        collection.add(documents=documents, ids=ids, metadatas=metadatas)

        return {
            "success": True,
            "message": f"Added {len(documents)} documents to collection '{collection_name}'",
            "document_count": len(documents),
            "collection_total": collection.count(),
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to add documents: {str(e)}"}


@mcp.tool(
    name="vector_store_search",
    description="Search documents in the vector store using semantic similarity",
)
async def vector_store_search(
    query: str,
    n_results: int = 5,
    collection_name: str = COLLECTION_NAME,
    include_distances: bool = True,
) -> dict[str, Any]:
    """
    Search documents using semantic similarity

    Args:
        query: Search query text
        n_results: Number of results to return
        collection_name: Name of the collection to search
        include_distances: Whether to include similarity distances

    Returns:
        Dictionary with search results and metadata
    """
    try:
        collection = get_or_create_collection(collection_name)

        # Check if collection is empty
        if collection.count() == 0:
            return {
                "success": True,
                "message": "Collection is empty. Add documents first.",
                "results": [],
                "total_documents": 0,
            }

        # Perform search
        include_list = ["documents", "metadatas"]
        if include_distances:
            include_list.append("distances")

        search_results = collection.query(
            query_texts=[query],
            n_results=min(n_results, collection.count()),
            include=include_list,
        )

        # Format results
        results = []
        for i in range(len(search_results["documents"][0])):
            result = {
                "id": search_results["ids"][0][i],
                "document": search_results["documents"][0][i],
                "metadata": search_results["metadatas"][0][i],
                "rank": i + 1,
            }

            if include_distances:
                # Convert distance to similarity score (0-1, higher is better)
                distance = search_results["distances"][0][i]
                result["similarity_score"] = max(0, 1 - distance)
                result["distance"] = distance

            results.append(result)

        return {
            "success": True,
            "query": query,
            "results": results,
            "total_documents": collection.count(),
            "returned_count": len(results),
        }

    except Exception as e:
        return {"success": False, "error": f"Search failed: {str(e)}"}


@mcp.tool(
    name="vector_store_info",
    description="Get information about the vector store collections",
)
async def vector_store_info(collection_name: str = COLLECTION_NAME) -> dict[str, Any]:
    """
    Get information about a vector store collection

    Args:
        collection_name: Name of the collection to get info for

    Returns:
        Dictionary with collection information
    """
    try:
        collection = get_or_create_collection(collection_name)

        # Get collection info
        collection_info = {
            "name": collection.name,
            "count": collection.count(),
            "metadata": collection.metadata,
        }

        # List all collections
        all_collections = chroma_client.list_collections()
        collection_names = [col.name for col in all_collections]

        return {
            "success": True,
            "current_collection": collection_info,
            "all_collections": collection_names,
            "database_path": CHROMA_DB_PATH,
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to get collection info: {str(e)}"}


@mcp.tool(
    name="vector_store_reset",
    description="Reset/clear a vector store collection (use with caution)",
)
async def vector_store_reset(collection_name: str = COLLECTION_NAME) -> dict[str, Any]:
    """
    Reset a vector store collection (removes all documents)

    Args:
        collection_name: Name of the collection to reset

    Returns:
        Dictionary with reset status
    """
    try:
        # Delete and recreate collection
        try:
            chroma_client.delete_collection(name=collection_name)
        except Exception:
            pass  # Collection might not exist

        collection = chroma_client.create_collection(
            name=collection_name,
            metadata={"description": "AWS documentation and knowledge base"},
        )

        return {
            "success": True,
            "message": f"Collection '{collection_name}' has been reset",
            "collection_count": collection.count(),
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to reset collection: {str(e)}"}

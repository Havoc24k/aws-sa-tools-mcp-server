"""
Generic PDF ingestion with flexible categorization and metadata
Replaces AWS-specific PDF ingestion with a more flexible system
"""

import os
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pypdf
import requests

from ...logging_config import get_logger
from ...mcp import mcp
from .document_management import document_ingest

# Get logger for this module
logger = get_logger(__name__)


@mcp.tool(
    name="pdf_ingest_from_url",
    description="Download and ingest any PDF document from URL with flexible categorization",
)
async def pdf_ingest_from_url(
    pdf_url: str,
    document_title: str | None = None,
    category: str = "technical",
    doc_type: str = "documentation",
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
    collection_name: str = "documents",
    chunk_size: int = 1200,
    overlap_size: int = 200,
) -> dict[str, Any]:
    """
    Download and ingest any PDF document from URL

    Args:
        pdf_url: URL of the PDF to download
        document_title: Title for the document (auto-detected if not provided)
        category: Document category (technical, business, educational, legal, research, general)
        doc_type: Specific document type (documentation, manual, guide, etc.)
        tags: Custom tags for categorization
        metadata: Additional custom metadata
        collection_name: Vector store collection name
        chunk_size: Size of text chunks for embedding
        overlap_size: Overlap between chunks to maintain context

    Returns:
        Dictionary with ingestion results
    """
    try:
        # Auto-detect title from URL if not provided
        if document_title is None:
            parsed_url = urlparse(pdf_url)
            document_title = (
                Path(parsed_url.path).stem.replace("-", " ").replace("_", " ").title()
            )

        logger.info(f"Downloading PDF: {document_title}")
        logger.info(f"URL: {pdf_url}")

        # Download PDF
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()

        # Store content size for reporting
        content_length = 0

        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
                content_length += len(chunk)
            temp_pdf_path = temp_file.name

        try:
            # Process PDF
            result = await pdf_ingest_from_file(
                pdf_path=temp_pdf_path,
                document_title=document_title,
                category=category,
                doc_type=doc_type,
                tags=tags,
                metadata=metadata,
                collection_name=collection_name,
                chunk_size=chunk_size,
                overlap_size=overlap_size,
            )

            # Add download info to metadata
            if result["success"]:
                result["source_url"] = pdf_url
                result["download_size_bytes"] = content_length
                result["download_size_mb"] = round(content_length / 1024 / 1024, 1)

            return result

        finally:
            # Clean up temporary file
            os.unlink(temp_pdf_path)

    except requests.RequestException as e:
        return {
            "success": False,
            "error": f"Failed to download PDF from {pdf_url}: {str(e)}",
        }
    except Exception as e:
        return {"success": False, "error": f"PDF ingestion failed: {str(e)}"}


@mcp.tool(
    name="pdf_ingest_from_file",
    description="Ingest a local PDF file with flexible categorization",
)
async def pdf_ingest_from_file(
    pdf_path: str,
    document_title: str | None = None,
    category: str = "technical",
    doc_type: str = "documentation",
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
    collection_name: str = "documents",
    chunk_size: int = 1200,
    overlap_size: int = 200,
) -> dict[str, Any]:
    """
    Ingest a local PDF file into the vector store

    Args:
        pdf_path: Path to the PDF file
        document_title: Title for the document (auto-detected if not provided)
        category: Document category (technical, business, educational, legal, research, general)
        doc_type: Specific document type (documentation, manual, guide, etc.)
        tags: Custom tags for categorization
        metadata: Additional custom metadata
        collection_name: Vector store collection name
        chunk_size: Size of text chunks for embedding
        overlap_size: Overlap between chunks to maintain context

    Returns:
        Dictionary with ingestion results
    """
    try:
        pdf_file = Path(pdf_path)

        if not pdf_file.exists():
            return {"success": False, "error": f"PDF file not found: {pdf_path}"}

        # Auto-detect title from filename if not provided
        if document_title is None:
            document_title = pdf_file.stem.replace("-", " ").replace("_", " ").title()

        logger.info(f"Processing PDF: {document_title}")

        # Extract text from PDF
        text_content = extract_text_from_pdf(pdf_path)

        if not text_content.strip():
            return {"success": False, "error": "No text content extracted from PDF"}

        logger.info(f"Extracted {len(text_content):,} characters of text")

        # Prepare metadata
        pdf_metadata = {
            "source_file": str(pdf_file),
            "file_size_bytes": pdf_file.stat().st_size,
            "file_size_mb": round(pdf_file.stat().st_size / 1024 / 1024, 1),
            **(metadata or {}),
        }

        # Use generic document ingestion
        result = await document_ingest(
            content=text_content,
            document_title=document_title,
            source_type="pdf",
            category=category,
            doc_type=doc_type,
            tags=tags,
            metadata=pdf_metadata,
            collection_name=collection_name,
            chunk_size=chunk_size,
            overlap_size=overlap_size,
        )

        return result

    except Exception as e:
        return {"success": False, "error": f"PDF processing failed: {str(e)}"}


@mcp.tool(
    name="pdf_ingest_preset",
    description="Ingest PDFs using predefined presets for common document types",
)
async def pdf_ingest_preset(
    pdf_source: str,  # URL or file path
    preset: str,
    document_title: str | None = None,
    tags: list[str] | None = None,
    collection_name: str = "documents",
) -> dict[str, Any]:
    """
    Ingest PDFs using predefined presets for common document types

    Args:
        pdf_source: URL or local file path to PDF
        preset: Preset type (aws_docs, technical_manual, research_paper, business_policy, etc.)
        document_title: Optional custom title
        tags: Additional tags beyond preset defaults
        collection_name: Collection to store in

    Returns:
        Dictionary with ingestion results
    """
    # Predefined presets
    presets: dict[str, dict[str, Any]] = {
        "aws_docs": {
            "category": "technical",
            "doc_type": "documentation",
            "tags": ["aws", "cloud", "documentation"],
            "chunk_size": 1500,
            "overlap_size": 300,
        },
        "technical_manual": {
            "category": "technical",
            "doc_type": "manual",
            "tags": ["manual", "technical", "reference"],
            "chunk_size": 1200,
            "overlap_size": 200,
        },
        "research_paper": {
            "category": "research",
            "doc_type": "paper",
            "tags": ["research", "academic", "study"],
            "chunk_size": 1000,
            "overlap_size": 150,
        },
        "business_policy": {
            "category": "business",
            "doc_type": "policy",
            "tags": ["policy", "business", "governance"],
            "chunk_size": 800,
            "overlap_size": 100,
        },
        "tutorial": {
            "category": "educational",
            "doc_type": "tutorial",
            "tags": ["tutorial", "learning", "guide"],
            "chunk_size": 1000,
            "overlap_size": 200,
        },
        "legal_document": {
            "category": "legal",
            "doc_type": "contract",
            "tags": ["legal", "contract", "compliance"],
            "chunk_size": 800,
            "overlap_size": 100,
        },
    }

    if preset not in presets:
        return {
            "success": False,
            "error": f"Unknown preset '{preset}'. Available: {list(presets.keys())}",
        }

    preset_config = presets[preset]

    # Merge tags
    preset_tags: list[str] = list(preset_config["tags"]).copy()
    if tags:
        preset_tags.extend(tags)

    # Determine if it's URL or file
    is_url = pdf_source.startswith(("http://", "https://"))

    if is_url:
        return await pdf_ingest_from_url(
            pdf_url=pdf_source,
            document_title=document_title,
            category=preset_config["category"],
            doc_type=preset_config["doc_type"],
            tags=preset_tags,
            metadata={"preset_used": preset},
            collection_name=collection_name,
            chunk_size=preset_config["chunk_size"],
            overlap_size=preset_config["overlap_size"],
        )
    else:
        return await pdf_ingest_from_file(
            pdf_path=pdf_source,
            document_title=document_title,
            category=preset_config["category"],
            doc_type=preset_config["doc_type"],
            tags=preset_tags,
            metadata={"preset_used": preset},
            collection_name=collection_name,
            chunk_size=preset_config["chunk_size"],
            overlap_size=preset_config["overlap_size"],
        )


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from PDF file with improved cleaning"""
    text_content = ""

    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = pypdf.PdfReader(file)
            total_pages = len(pdf_reader.pages)

            logger.info(f"Processing {total_pages} pages...")

            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        # Clean up the text
                        page_text = clean_pdf_text(page_text)
                        text_content += (
                            f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
                        )

                    # Progress indicator for large PDFs
                    if page_num % 10 == 0 and page_num > 0:
                        logger.info(f"Processed {page_num}/{total_pages} pages...")

                except Exception as e:
                    logger.warning(
                        f"Error extracting text from page {page_num + 1}: {e}"
                    )
                    continue

            # Final page count
            if total_pages > 10:
                logger.info(f"Completed processing all {total_pages} pages")

    except Exception as e:
        raise Exception(f"Failed to read PDF file: {e}") from e

    return text_content.strip()


def clean_pdf_text(text: str) -> str:
    """Clean and normalize text extracted from PDF"""
    import re

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove common PDF artifacts
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)  # Add space between words
    text = re.sub(r"([.!?])([A-Z])", r"\1 \2", text)  # Space after punctuation

    # Remove page numbers (standalone numbers)
    text = re.sub(r"\n\d+\n", "\n", text)

    # Remove header/footer patterns (adjust as needed)
    text = re.sub(r"\n.*?©.*?\n", "\n", text)  # Copyright lines
    text = re.sub(r"\n.*?confidential.*?\n", "\n", text, flags=re.IGNORECASE)

    return text.strip()

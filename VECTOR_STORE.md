# Vector Store Integration

The AWS MCP Server now includes a powerful document ingestion and semantic search system using ChromaDB.

## Features

- **Generic PDF Ingestion**: Ingest any PDF document with flexible categorization
- **Semantic Search**: Natural language search across all ingested documents  
- **Document Management**: List, search, and organize documents by category and tags
- **Multiple Collections**: Organize documents in separate collections
- **Predefined Presets**: Optimized settings for different document types

## Quick Start

### 1. Enable Vector Store Features
The vector store is **disabled by default**. Enable it when running the MCP server:

```bash
# STDIO transport with vector store
python -m aws_mcp_server.server --enable-vector-store

# SSE transport with vector store
python -m aws_mcp_server.server --sse --port 8888 --enable-vector-store

# Custom data source directory
python -m aws_mcp_server.server --enable-vector-store --data-source /path/to/documents

# Default (without vector store)
python -m aws_mcp_server.server
```

### 2. Automatic Document Ingestion
When `--enable-vector-store` is enabled, the server automatically:

1. **Scans** the data source directory (default: `datasource/`) on startup
2. **Ingests** all PDF files automatically with intelligent categorization
3. **Tracks** file changes and only processes new/modified files
4. **Maintains** an index to avoid duplicate processing

### 3. Manual Document Ingestion
```bash
# From URL with preset
python -c "
import asyncio
from aws_mcp_server.services.knowledge.generic_pdf_ingestion import pdf_ingest_preset
asyncio.run(pdf_ingest_preset(
    pdf_source='https://example.com/doc.pdf',
    preset='technical_manual',
    document_title='My Technical Manual'
))
"
```

## MCP Tools Available

### Document Ingestion
- `pdf_ingest_from_url` - Download and ingest PDF from URL
- `pdf_ingest_from_file` - Ingest local PDF file
- `pdf_ingest_preset` - Use predefined settings for common document types
- `document_ingest` - Generic document ingestion (any text content)

### Document Management  
- `document_search` - Search with category/type/tag filtering
- `document_list` - List all documents with metadata
- `document_categories` - Get available categories and presets

### Vector Store Operations
- `vector_store_add` - Add documents to vector store
- `vector_store_search` - Semantic search
- `vector_store_info` - Get collection information
- `vector_store_reset` - Clear collection

## Document Categories

- **technical**: documentation, manual, guide, reference, api
- **business**: policy, procedure, compliance, governance, strategy
- **educational**: tutorial, course, lesson, training, workshop  
- **legal**: contract, agreement, terms, privacy, regulation
- **research**: paper, study, analysis, report, whitepaper
- **general**: misc, other, uncategorized

## Presets

- `aws_docs` - AWS documentation (1500 char chunks, 300 overlap)
- `technical_manual` - Product manuals, guides (1200/200)
- `research_paper` - Academic papers, studies (1000/150)  
- `business_policy` - Policies, procedures (800/100)
- `tutorial` - Educational content (1000/200)
- `legal_document` - Contracts, compliance (800/100)

## Configuration

### Environment Variables
- `ENABLE_VECTOR_STORE` - Enable vector store features (set to "true" to enable)
- `CHROMA_DB_PATH` - Path to ChromaDB storage (default: `./chroma_db`)
- `EMBEDDING_MODEL` - Embedding model to use (default: ChromaDB default)

### Collection Management
Documents are stored in collections. Default collection is "aws_docs" but you can specify any collection name.

## Data Source Directory

The server scans a designated directory for PDF files when `--enable-vector-store` is enabled.

### Default Structure
```
datasource/
├── aws-docs/              # AWS documentation (category: technical)
├── policies/              # Business policies (category: business)
├── manuals/               # Technical manuals (category: technical)
├── research/              # Research papers (category: research)
├── training/              # Educational content (category: educational)
└── legal/                 # Legal documents (category: legal)
```

### Supported File Types
- **PDF Documents** (`.pdf`)
  - Technical documentation
  - Business policies
  - Research papers
  - Manuals and guides

### Automatic Categorization
Files are automatically categorized based on:
- **Directory path** (e.g., files in `policies/` become business documents)
- **Filename keywords** (e.g., "wellarchitected" becomes AWS technical documentation)

### Auto-Sync Process
When the server starts with vector store enabled:

1. **Scans** the data source directory for PDF files
2. **Checks** which files are new or modified since last run
3. **Ingests** only changed files to avoid duplicates
4. **Tracks** file changes using SHA-256 hashes
5. **Updates** the vector store incrementally

### File Index
The server maintains a `vector_store_index.json` file to track:
- File hashes for change detection
- Ingestion metadata
- Document categorization
- Chunk counts

### Usage Workflow
1. **Add PDF files** to the data source directory (or subdirectories)
2. **Start the server** with `--enable-vector-store`
3. **Files are automatically ingested** on startup
4. **Query documents** using the MCP tools

Files added while the server is running will be ingested on the next restart.

## Local Storage

All vector data is stored locally in the `chroma_db/` directory. This directory is automatically added to `.gitignore` to prevent committing large embedding files.

The vector store uses ChromaDB's default embedding model (`sentence-transformers/all-MiniLM-L6-v2`) which runs locally without API dependencies.
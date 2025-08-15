# Vector Store Workflow

This document explains the complete workflow for using the AWS MCP Server with vector store capabilities.

## Quick Start

### 1. Setup Data Source
```bash
# Create directory and add PDF documents
mkdir -p datasource/aws-docs
# Copy your PDF files to datasource/ or subdirectories
```

### 2. Start Server with Vector Store
```bash
# Start with automatic document ingestion
python -m aws_mcp_server.server --enable-vector-store

# Or with custom data source path
python -m aws_mcp_server.server --enable-vector-store --data-source /path/to/your/documents
```

### 3. Server Initialization Flow

When you start the server with `--enable-vector-store`, it automatically:

#### Step 1: Vector Store Check
- ✅ Checks if vector store database exists
- 📊 Reports current document count if found
- 🆕 Creates new vector store if needed

#### Step 2: File Index Loading
- 📋 Loads existing file tracking index (`vector_store_index.json`)
- 🔍 Contains hashes and metadata for previously processed files
- 🆕 Creates new index if none exists

#### Step 3: Data Source Scan
- 📁 Scans data source directory for supported files (.pdf)
- 📄 Lists all found files with their paths
- 🏷️ Prepares automatic categorization based on path/filename

#### Step 4: Incremental Sync
- 🔄 Compares file hashes to detect new/modified files
- ⏭️ Skips unchanged files to avoid duplicate processing
- 📥 Ingests only new or modified documents

#### Step 5: Auto-Categorization
Files are automatically categorized based on:
- **Directory structure**: `aws-docs/` → technical/documentation
- **Filename keywords**: `wellarchitected` → technical/documentation + aws tags
- **Path patterns**: `policies/` → business/policy

#### Step 6: Index Update
- 💾 Updates file index with new hashes and metadata
- 📊 Tracks ingestion timestamps and chunk counts
- 🏷️ Stores category and tag information

#### Step 7: Ready to Serve
- ✅ Vector store is ready for semantic queries
- 🎯 All MCP tools are available
- 📈 Reports final document count and status

## Example Server Output

```
🚀 Initializing Vector Store
📁 Data Source: datasource/

📊 Checking vector store status...
   ✅ Vector store found with 0 documents
📋 No existing index found, creating new one

🔍 Scanning data source directory: datasource/
   📄 Found 2 files
      • datasource/aws-docs/wellarchitected-framework.pdf
      • datasource/policies/data-privacy-policy.pdf

🔄 Syncing files with vector store...
   📥 Ingesting wellarchitected-framework.pdf (new)
      ✅ Success! Added 1247 chunks
   📥 Ingesting data-privacy-policy.pdf (new)
      ✅ Success! Added 89 chunks

📈 Sync Summary:
   📄 New files: 2
   🔄 Updated files: 0
   ⏭️ Skipped files: 0

✅ Vector Store Ready!
   📊 Total documents: 1336
   📁 Tracked files: 2
   🎯 Ready to serve document queries!
```

## File Management

### Adding New Documents
1. **Copy PDF files** to `datasource/` (or subdirectories)
2. **Restart the server** - new files will be automatically detected and ingested
3. **Check the console output** to see ingestion progress

### Updating Existing Documents
1. **Replace the PDF file** with the updated version
2. **Restart the server** - modified files will be re-ingested
3. **Old chunks are replaced** with new content

### Directory Organization
```
datasource/
├── aws-docs/              # AWS technical documentation
│   ├── wellarchitected-framework.pdf
│   └── security-best-practices.pdf
├── policies/              # Business policies
│   ├── data-privacy-policy.pdf
│   └── security-policy.pdf
├── manuals/               # Technical manuals
│   └── api-reference.pdf
└── research/              # Research papers
    └── cloud-security-study.pdf
```

## Querying Documents

Once ingested, use MCP tools to search documents:

### Search by Content
```python
# Search across all documents
await document_search(
    query="What are the Well-Architected pillars?",
    n_results=5
)
```

### Search by Category
```python
# Search only business policies
await document_search(
    query="data privacy requirements",
    category="business",
    doc_type="policy"
)
```

### Search by Tags
```python
# Search documents with specific tags
await document_search(
    query="security best practices",
    tags=["aws", "security"]
)
```

## File Index Structure

The `vector_store_index.json` file tracks:

```json
{
  "datasource/aws-docs/wellarchitected-framework.pdf": {
    "hash": "sha256_hash_of_file",
    "size": 2847392,
    "modified_time": 1704567890.123,
    "ingested_at": "2024-01-06T15:30:00",
    "document_title": "wellarchitected-framework",
    "chunks_created": 1247,
    "category": "technical",
    "doc_type": "documentation",
    "tags": ["aws", "framework", "best-practices", "auto_synced"]
  }
}
```

## Performance Notes

- **Hash-based change detection** means only modified files are re-processed
- **Large documents** are automatically chunked for optimal embedding
- **Memory usage** scales with the number of documents in the vector store
- **Startup time** depends on the number of new files to process

## Troubleshooting

### No Files Found
```
ℹ️ No supported files found in datasource/
📝 Supported formats: .pdf
```
**Solution**: Add PDF files to the data source directory

### File Access Errors
```
⚠️ Error reading file.pdf: Permission denied
```
**Solution**: Check file permissions and ensure the server can read the files

### Memory Issues
**Symptoms**: Slow performance or out of memory errors
**Solution**: Process large documents in batches or increase system memory

### Index Corruption
**Symptoms**: Files are re-ingested every startup
**Solution**: Delete `vector_store_index.json` to rebuild the index

## Advanced Configuration

### Custom Data Source
```bash
# Use a different directory
python -m aws_mcp_server.server --enable-vector-store --data-source /company/documents
```

### Environment Variables
- `ENABLE_VECTOR_STORE` - Enable vector store features (default: false)
- `CHROMA_DB_PATH` - Vector store database location (default: ./chroma_db)
- `DATA_SOURCE_PATH` - Default data source directory (overridden by CLI)

This workflow ensures your documents are automatically available for semantic search with minimal manual intervention!
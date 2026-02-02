# Backend - FAISS Semantic Search API

Production-ready Flask API for semantic search using FAISS index.

## Features

- Fast semantic search with FAISS IndexFlatIP
- Normalized L2 vectors for cosine similarity
- JSON metadata support
- CORS-enabled REST API
- Health check endpoint
- Configurable top-k and similarity thresholds

## Setup

### 1. Install Dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Note for Windows:** If FAISS fails to install, use:
```powershell
conda install -c conda-forge faiss-cpu
```

### 2. Configure Environment

```powershell
Copy-Item .env.example .env
```

Edit `.env`:
```env
BACKEND_HOST=0.0.0.0
BACKEND_PORT=5000
CORS_ORIGINS=http://localhost:8000
INDEX_DIR=indexes
```

### 3. Prepare Index Files

Ensure you have:
- `indexes/faiss_index.index` - FAISS binary index
- `indexes/metadata.jsonl` - One JSON object per line with document metadata

### 4. Run API Server

**Development:**
```powershell
python -m src.api
# API on http://localhost:5000
```

**Production (Windows):**
```powershell
waitress-serve --port=5000 --host=0.0.0.0 "src.api:create_app()"
```

**Production (Linux):**
```bash
gunicorn --workers=4 --bind=0.0.0.0:5000 "src.api:create_app()"
```

## API Reference

### POST /search
Search for semantic matches.

**Request:**
```json
{
  "q": "How to reset password?",
  "top_k": 50,
  "threshold": 0.5
}
```

**Response (200):**
```json
{
  "results": [
    {
      "id": "doc-123",
      "thread_id": "thread-456",
      "title": "Password Reset Guide",
      "question_text": "...",
      "snippet": "...",
      "url": "https://...",
      "score": 0.8756
    }
  ],
  "count": 1
}
```

**Error Response (400):**
```json
{
  "error": "empty query",
  "results": []
}
```

### GET /search
Alternative GET interface with query parameters.

```
GET /search?q=How+to+reset+password&top_k=50&threshold=0.5
```

### GET /health
Health check endpoint.

**Response (200):**
```json
{
  "status": "ok",
  "index_size": 15234
}
```

## CLI Usage

Search from command line:

```powershell
python -m src.search --query "How to reset password?" --top-k 5 --threshold 0.8
```

Options:
- `--query` - Search query
- `--index-dir` - Index directory (default: indexes)
- `--model` - Embedding model (default: all-MiniLM-L6-v2)
- `--top-k` - Number of results (default: 5)
- `--threshold` - Similarity threshold (default: 0.8)

## Testing

```powershell
# Run tests
pytest tests/ -v

# Test search endpoint
python -m pytest tests/test_api.py -v

# Test CLI
python -m src.search --query "test" --top-k 1
```

## Metadata Format (JSONL)

Each line in `metadata.jsonl` should be a valid JSON object:

```json
{"id": "1", "title": "Q1", "snippet": "...", "url": "...", "thread_id": "t1"}
{"id": "2", "title": "Q2", "snippet": "...", "url": "...", "thread_id": "t2"}
```

Required fields:
- `id` - Unique document identifier

Optional fields:
- `title` - Document title
- `snippet` - Document excerpt
- `url` - Document URL
- `thread_id` - Thread identifier
- `question_text` - Full question text
- Any other custom fields

## Performance Tuning

### Search Speed
- Increase `threshold` to filter results faster
- Decrease `top_k` to search fewer items
- Use GPU with `faiss-gpu` for large indexes

### Memory
- FAISS IndexFlatIP stores all vectors in RAM
- For 1M vectors × 384 dims: ~1.5 GB RAM
- Consider IndexIVF for very large datasets

## Troubleshooting

### FAISS Import Error
```python
ImportError: No module named 'faiss'
```

Solution (Windows):
```powershell
conda install -c conda-forge faiss-cpu
```

Or for GPU:
```powershell
conda install -c conda-forge faiss-gpu
```

### Index Not Found
```
RuntimeError: Index or metadata not found in indexes
```

Ensure both files exist:
```powershell
ls indexes/faiss_index.index
ls indexes/metadata.jsonl
```

### Slow First Query
Model loading takes ~1-2 seconds on first query. Subsequent queries are fast.

### CORS Errors
Update `CORS_ORIGINS` in `.env` to include frontend URL:
```env
CORS_ORIGINS=http://localhost:8000,http://example.com
```

## Development

### Project Structure
```
src/
├── api.py           # Flask API server
├── search.py        # CLI search utility
└── __init__.py

indexes/
├── faiss_index.index
├── metadata.jsonl
└── processed_ids.json
```

### Code Style
- Python 3.8+ type hints
- Docstrings for public functions
- 100-char line limit (soft)

### Adding Custom Models
Edit `create_app()` to change embedding model:
```python
model = SentenceTransformer('model-name')  # From sentence-transformers
```

Popular models:
- `all-MiniLM-L6-v2` (384-dim, fast, default)
- `all-mpnet-base-v2` (768-dim, slower but better)
- `sentence-transformers/all-distilroberta-v1` (768-dim)

## License

Developed by Azar

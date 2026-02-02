# ServiceNow Semantic Search - Restructured

A two-tier semantic search application for ServiceNow community questions. **Backend** runs FAISS-based semantic indexing and search, **Frontend** provides a web UI.

## Project Structure

```
.
├── backend/                 # Search API backend
│   ├── src/
│   │   ├── api.py          # Flask API server
│   │   ├── search.py       # CLI search utility
│   │   └── __init__.py
│   ├── indexes/            # FAISS index and metadata
│   │   ├── faiss_index.index
│   │   ├── metadata.jsonl
│   │   └── processed_ids.json
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── frontend/               # Web UI frontend
│   ├── src/
│   │   ├── app.py         # Flask web app
│   │   └── __init__.py
│   ├── templates/         # HTML templates
│   │   ├── layout.html
│   │   └── search.html
│   ├── static/            # CSS/JS assets
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── search.js
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── README.md              # This file
└── .gitignore
```

## Quick Start (Windows PowerShell)

### 1. Backend Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# Copy environment
Copy-Item .env.example .env

# Run API
python -m src.api
```

Backend runs on `http://localhost:5000`

### 2. Frontend Setup (new terminal)

```powershell
cd frontend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# Copy environment
Copy-Item .env.example .env
# Ensure BACKEND_API_URL=http://localhost:5000

# Run app
python -m src.app
```

Frontend runs on `http://localhost:8000`

## Documentation

- [Backend README](backend/README.md) - API setup and deployment
- [Frontend README](frontend/README.md) - UI setup and customization

## Features

✅ **Backend**
- FAISS semantic search engine
- REST API with JSON responses
- Configurable similarity thresholds
- CLI search utility
- Health check endpoint

✅ **Frontend**
- Modern responsive design
- Real-time search with AJAX
- Server-side rendering fallback
- Mobile-friendly UI
- Zero external JS dependencies

## Architecture

```
Frontend (Port 8000)           Backend (Port 5000)
┌─────────────────────┐        ┌─────────────────────┐
│ Flask Web App       │        │ Flask API Server    │
│ - Search UI         │───────→│ - FAISS Index       │
│ - HTML/CSS/JS       │←───────│ - Embedding Model   │
│ - API Proxy         │        │ - Metadata JSON     │
└─────────────────────┘        └─────────────────────┘
```

## Environment Setup

### Backend (.env)
```env
FLASK_ENV=development
BACKEND_HOST=0.0.0.0
BACKEND_PORT=5000
CORS_ORIGINS=http://localhost:8000
INDEX_DIR=indexes
```

### Frontend (.env)
```env
FLASK_ENV=development
FRONTEND_HOST=127.0.0.1
FRONTEND_PORT=8000
BACKEND_API_URL=http://localhost:5000
```

## API Endpoints

**Backend:**
- `GET/POST /search` - Search with query, top_k, threshold
- `GET /health` - Health check

**Frontend:**
- `GET /` - Home page
- `POST /search` - Server-side search (non-JS fallback)
- `GET/POST /api/search` - API proxy

## Requirements

### Backend (`backend/requirements.txt`)
- Flask 2.2+
- faiss-cpu (or faiss-gpu)
- sentence-transformers
- numpy, scipy
- python-dotenv

### Frontend (`frontend/requirements.txt`)
- Flask 2.2+
- requests (for backend API calls)
- python-dotenv

## CLI Usage

Search from command line:

```powershell
cd backend
python -m src.search --query "How to reset password?" --top-k 5 --threshold 0.8
```

## Deployment

### Production (Windows)

```powershell
# Backend
cd backend
waitress-serve --port=5000 --host=0.0.0.0 "src.api:create_app()"

# Frontend (new terminal)
cd frontend
waitress-serve --port=8000 "src.app:create_app()"
```

### Production (Linux)

```bash
# Backend
cd backend
gunicorn --workers=4 --bind=0.0.0.0:5000 "src.api:create_app()"

# Frontend
cd frontend
gunicorn --workers=4 --bind=0.0.0.0:8000 "src.app:create_app()"
```

## Troubleshooting

### Backend won't start
- Check `indexes/faiss_index.index` exists
- Verify FAISS installation: `python -c "import faiss"`
- On Windows with issues: `conda install -c conda-forge faiss-cpu`

### Frontend can't reach backend
- Ensure backend running on port 5000
- Check `BACKEND_API_URL` in frontend `.env`
- Verify CORS settings in backend

### Slow searches
- First query slower (model loading)
- Increase similarity threshold to filter
- Decrease top_k for faster results

## License

Developed by Azar

- Larger discovery (sitemaps + crawl, recommended for many URLs):

```powershell
python src\discover_both.py --start-url "https://www.servicenow.com/community/" --mode both --max-urls 2000 --max-pages 200 --out data/queue/urls.txt
```

After discovery, `data/queue/urls.txt` will contain one URL per line.

5) Run the worker to scrape queued threads

- Run directly as a module (recommended):

```powershell
python -m src.worker --queue data/queue/urls.txt --rate 1.0 --last-hours 72
```

- Or use the local helper (the repository includes `src/run_worker_local.py`):

```powershell
python src\run_worker_local.py
```

Worker notes:
- By default the worker writes flat JSON to `data/threads_flat/<thread_id>.json`.
- It appends processed URLs to `data/queue/processed_flat.txt` so processed items are skipped on subsequent runs.
- Default behavior filters to threads that include an accepted answer and enforces the `--last-hours` age cutoff (use `--no-accepted` to disable that filter or change `--last-hours`).

6) Inspect outputs

- Flat JSON files: `data/threads_flat/<thread_id>.json` — sample keys: `url`, `thread_id`, `title`, `question_text`, `answer_count`, `answer_1_text`, `answer_1_is_accepted`, etc.
- Nested JSON (if you run with `--no-flat`): `data/threads/<thread_id>.json` with `posts`/`answers` arrays.
- Processed list: `data/queue/processed_flat.txt` — one URL per line.

Troubleshooting

- If you see import errors for Playwright, ensure it is installed and browsers are installed: `pip install -r requirements.txt` then `python -m playwright install`.
- If `src` import errors occur when running helper scripts, use the module form: `python -m src.worker ...` or run `src/run_worker_local.py` which ensures the project root is on `sys.path`.
- If discovery returns few or no URLs, increase `--max-pages`/`--max-urls` or run `src/discover.py` on a specific board page to seed the queue.

Example flat JSON shape (illustrative)

```json
{
	"url": "https://.../td-p/123456",
	"thread_id": "123456",
	"title": "Thread title",
	"question_text": "Question summary...",
	"answer_count": 2,
	"answer_1_text": "Answer text...",
	"answer_1_is_accepted": true
}
```

If you want, I can also:
- Run the environment installs and start the worker here.
- Add a small discovery wrapper or CI scheduler to run the worker regularly.

Files of interest

- `src/scrape.py` — scraping and JSON output (`run` / `run_flat`)
- `src/worker.py` — queue processing and CLI
- `src/discover.py` / `src/discover_both.py` — helpers to populate `data/queue/urls.txt`
- `data/threads_flat/` and `data/queue/` — output and queue files

See `src` for implementation details.

//for web app running
 python -m pip install -r requirements.txt
python src\webapp.py  



// for small discovery and worker run

this will get ids from processed jsons and build seen_ids.txt
python src/tools/build_seen_ids.py

this is for discovery of new urls to crawl
python src/discover_both.py --out data/queue/urls_crawl.txt --mode both --max-urls 5000 --max-pages 2000
or
$env:PYTHONPATH='.'; python src/discover_both.py --mode crawl --max-urls 5000 --max-pages 2000 --out data/queue/urls_crawl_test.txt --show-dates


this will run the worker to process the discovered urls
python -m src.worker --queue data/queue/urls_crawl.txt --rate 1.0 --last-hours 99999

Indexing & Semantic Search

7) Build or update the FAISS index (incremental)

- The repository includes an incremental ingest tool that embeds texts and appends vectors + aligned metadata into `indexes/`.
- Embeddings combine `title` + `question_text` (preferred) to improve relevance.
- Persistent files written under `indexes/`:
	- `faiss_index.index` — FAISS binary index (IndexFlatIP over L2-normalized vectors)
	- `metadata.jsonl` — newline-delimited JSON metadata; order must match FAISS insertion order
	- `processed_ids.json` — list of `thread_id` values already indexed (used to avoid duplicates)

Run the incremental ingest (processes only new JSONs not already listed in `processed_ids.json`):

```powershell
& ".venv\Scripts\python.exe" src\ingest.py --data-dir data/threads_flat --index-dir indexes
```

- The ingest tool will skip files whose `thread_id` is already recorded in `indexes/processed_ids.json`, so re-running it after adding new JSON files will only index the newly added files.

8) Rebuild a small test index (optional)

- A helper script `src/rebuild_partial_index.py` can build a fresh index from the first N JSONs (useful for experiments or when you want to overwrite `indexes/`):

```powershell
& ".venv\Scripts\python.exe" src\rebuild_partial_index.py
```

9) Querying and the UI

- The Flask UI (`src/webapp.py`) and API accept two useful parameters:
	- `top_k`: how many nearest neighbors to return (default visible in UI). Adjust to inspect more candidates.
	- `threshold`: minimum cosine similarity required to include a hit (0..1). Because vectors are L2-normalized and FAISS uses inner-product, the returned scores are equivalent to cosine similarity.
- For higher precision use `threshold` ≈ 0.6–0.8; for higher recall use a lower threshold (0.0–0.4). Typical `top_k` values: 5–20.

Notes & safety
- Keep backups before performing destructive merges of indexes; the ingest script appends metadata and updates `processed_ids.json` atomically, but if you plan to overwrite `indexes/` use `src/rebuild_partial_index.py`.
- If you encounter metadata parsing errors, inspect `indexes/metadata.jsonl` for malformed lines — each line must be valid JSON and the line order must match FAISS insertion order.
python -c "from src.webapp import create_app; app = create_app('indexes'); app.run(host='127.0.0.1', port=5000, debug=True)"
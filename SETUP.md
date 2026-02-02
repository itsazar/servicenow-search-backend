# Complete Setup & Deployment Guide

This guide covers setting up, testing, and deploying the ServiceNow Semantic Search application.

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Testing](#testing)
3. [Production Deployment](#production-deployment)
4. [Docker](#docker)
5. [Troubleshooting](#troubleshooting)

---

## Local Development Setup

### Windows PowerShell

#### Option 1: Using Run Scripts (Recommended)

**Terminal 1 - Backend:**
```powershell
.\run-backend.ps1
```

**Terminal 2 - Frontend:**
```powershell
.\run-frontend.ps1
```

#### Option 2: Manual Setup

**Backend:**
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python -m src.api
```

**Frontend (new terminal):**
```powershell
cd frontend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python -m src.app
```

### Linux/macOS

#### Using Run Scripts

**Terminal 1 - Backend:**
```bash
bash run-backend.sh
```

**Terminal 2 - Frontend:**
```bash
bash run-frontend.sh
```

#### Manual Setup

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python -m src.api
```

**Frontend (new terminal):**
```bash
cd frontend
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python -m src.app
```

### Verify Setup

1. **Backend Health Check:**
   ```bash
   curl http://localhost:5000/health
   # Expected: {"status": "ok", "index_size": <count>}
   ```

2. **Frontend Access:**
   - Open browser: http://localhost:8000
   - Try a search query

3. **Backend Direct Search:**
   ```powershell
   cd backend
   python -m src.search --query "test query" --top-k 5
   ```

---

## Testing

### Backend Tests

```powershell
cd backend

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Frontend Tests

```powershell
cd frontend

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Manual Integration Testing

```powershell
# Test form submission (non-JS fallback)
curl -X POST http://localhost:8000/search -d "q=password"

# Test API endpoint
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"q":"password"}'

# Test backend API
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"q":"password", "top_k": 10}'
```

---

## Production Deployment

### Windows Server

#### Backend - Using Waitress

```powershell
cd backend
pip install -r requirements.txt
waitress-serve --port=5000 --host=0.0.0.0 "src.api:create_app()"
```

#### Frontend - Using Waitress

```powershell
cd frontend
pip install -r requirements.txt
waitress-serve --port=8000 --host=0.0.0.0 "src.app:create_app()"
```

#### Using Windows Task Scheduler

**Script: `start-backend.ps1`**
```powershell
$backendPath = "C:\path\to\backend"
Set-Location $backendPath
.\.venv\Scripts\Activate.ps1
waitress-serve --port=5000 --host=0.0.0.0 "src.api:create_app()"
```

Add to Task Scheduler:
- Trigger: At startup
- Action: `powershell.exe -ExecutionPolicy Bypass -File "C:\path\to\start-backend.ps1"`
- Run: With highest privileges

### Linux (Ubuntu/Debian)

#### Using systemd

**File: `/etc/systemd/system/search-backend.service`**
```ini
[Unit]
Description=ServiceNow Search Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/search-backend
ExecStart=/var/www/search-backend/venv/bin/gunicorn \
  --workers=4 \
  --bind=0.0.0.0:5000 \
  "src.api:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```

**File: `/etc/systemd/system/search-frontend.service`**
```ini
[Unit]
Description=ServiceNow Search Frontend
After=network.target search-backend.service

[Service]
User=www-data
WorkingDirectory=/var/www/search-frontend
ExecStart=/var/www/search-frontend/venv/bin/gunicorn \
  --workers=4 \
  --bind=0.0.0.0:8000 \
  "src.app:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable search-backend
sudo systemctl enable search-frontend
sudo systemctl start search-backend
sudo systemctl start search-frontend

# Check status
sudo systemctl status search-backend
sudo systemctl status search-frontend
```

#### Using Nginx (Reverse Proxy)

**File: `/etc/nginx/sites-available/search`**
```nginx
upstream backend {
    server 127.0.0.1:5000;
}

upstream frontend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name search.example.com;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/backend {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/search /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Environment Variables for Production

**Backend `.env`:**
```env
FLASK_ENV=production
FLASK_DEBUG=False
BACKEND_HOST=0.0.0.0
BACKEND_PORT=5000
CORS_ORIGINS=https://search.example.com
INDEX_DIR=/var/data/indexes
MODEL_NAME=all-MiniLM-L6-v2
```

**Frontend `.env`:**
```env
FLASK_ENV=production
FLASK_DEBUG=False
FRONTEND_HOST=0.0.0.0
FRONTEND_PORT=8000
BACKEND_API_URL=http://127.0.0.1:5000
```

---

## Docker

### Docker Setup

**File: `backend/Dockerfile`**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY indexes/ indexes/
COPY .env .env

EXPOSE 5000

CMD ["python", "-m", "src.api"]
```

**File: `frontend/Dockerfile`**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY templates/ templates/
COPY static/ static/
COPY .env .env

EXPOSE 8000

CMD ["python", "-m", "src.app"]
```

**File: `docker-compose.yml`** (in root)
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - BACKEND_HOST=0.0.0.0
    volumes:
      - ./backend/indexes:/app/indexes

  frontend:
    build: ./frontend
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
      - BACKEND_API_URL=http://backend:5000
    depends_on:
      - backend
```

### Build and Run

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Troubleshooting

### Issue: FAISS Installation Fails on Windows

**Solution:**
```powershell
# Use conda instead
conda install -c conda-forge faiss-cpu
```

Or install pre-built wheel:
```powershell
pip install faiss-cpu --no-binary :all:
```

### Issue: "Address already in use"

```powershell
# Find process using port
netstat -ano | findstr :5000

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or change port in .env
BACKEND_PORT=5001
```

### Issue: Backend Connection Refused

1. Ensure backend is running: `python -m src.api`
2. Check backend URL in frontend `.env`
3. Verify CORS settings:
   ```env
   CORS_ORIGINS=http://localhost:8000
   ```

### Issue: Slow First Query

Normal - embedding model loads on first request. Subsequent queries are fast.

### Issue: Search Returns No Results

1. Check metadata.jsonl exists and is valid JSON
2. Verify threshold value (default 0.5)
3. Try increasing threshold:
   ```powershell
   python -m src.search --query "test" --threshold 0.1
   ```

### Issue: Out of Memory

FAISS loads entire index in RAM. For large indexes:
- Consider IndexIVF for better memory efficiency
- Increase server RAM
- Use GPU with faiss-gpu

### Check Logs

```powershell
# Backend logs (during run)
# Frontend logs (during run)

# Or check error files
Get-Content *.log | tail -50
```

---

## Performance Optimization

### Backend
- Use GPU: `pip install faiss-gpu`
- Increase workers: `gunicorn --workers=8`
- Add caching for frequent queries
- Use IndexIVF for large datasets

### Frontend
- Enable gzip compression in reverse proxy
- Minify CSS/JS for production
- Add caching headers

### General
- Use CDN for static assets
- Monitor resource usage
- Set up alerting

---

## Monitoring

### Systemd
```bash
sudo systemctl status search-backend
sudo journalctl -u search-backend -f
```

### Docker
```bash
docker-compose logs -f backend
docker ps
```

### Health Checks

```bash
# Backend
curl http://localhost:5000/health

# Frontend
curl http://localhost:8000/
```

---

## Support

For issues, check:
1. [Backend README](backend/README.md)
2. [Frontend README](frontend/README.md)
3. Application logs
4. Environment variables

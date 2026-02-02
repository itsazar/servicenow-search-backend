#!/bin/bash
# run-backend.sh - Start the backend API server (Linux/Mac)

BACKEND_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/backend" && pwd)"

echo -e "\033[32mStarting Backend API Server...\033[0m"
echo -e "\033[36mNavigate to: http://localhost:5000\033[0m"

cd "$BACKEND_PATH"

if [ ! -d "venv" ]; then
    echo -e "\033[33mVirtual environment not found. Creating...\033[0m"
    python3 -m venv venv
    source venv/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "\033[33m.env created - adjust settings if needed\033[0m"
fi

echo -e "\033[36mBackend API starting on http://0.0.0.0:5000\033[0m"
python -m src.api

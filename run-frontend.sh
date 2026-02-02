#!/bin/bash
# run-frontend.sh - Start the frontend web app (Linux/Mac)

FRONTEND_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/frontend" && pwd)"

echo -e "\033[32mStarting Frontend Web App...\033[0m"
echo -e "\033[36mNavigate to: http://localhost:8000\033[0m"
echo -e "\033[33mBackend API should be running on http://localhost:5000\033[0m"

cd "$FRONTEND_PATH"

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

echo -e "\033[36mFrontend app starting on http://127.0.0.1:8000\033[0m"
python -m src.app

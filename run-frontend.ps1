#!/usr/bin/env powershell
# run-frontend.ps1 - Start the frontend web app (Windows)

$frontendPath = Join-Path $PSScriptRoot "frontend"

Write-Host "Starting Frontend Web App..." -ForegroundColor Green
Write-Host "Navigate to: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Backend API should be running on http://localhost:5000" -ForegroundColor Yellow

Set-Location $frontendPath

if (!(Test-Path ".venv")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt
} else {
    .\.venv\Scripts\Activate.ps1
}

if (!(Test-Path ".env")) {
    Copy-Item .env.example .env
    Write-Host ".env created - adjust settings if needed" -ForegroundColor Yellow
}

Write-Host "Frontend app starting on http://127.0.0.1:8000" -ForegroundColor Cyan
python -m src.app

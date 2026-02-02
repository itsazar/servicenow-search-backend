#!/usr/bin/env powershell
# run-backend.ps1 - Start the backend API server (Windows)

$backendPath = Join-Path $PSScriptRoot "backend"

Write-Host "Starting Backend API Server..." -ForegroundColor Green
Write-Host "Navigate to: http://localhost:5000" -ForegroundColor Cyan

Set-Location $backendPath

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

Write-Host "Backend API starting on http://0.0.0.0:5000" -ForegroundColor Cyan
python -m src.api

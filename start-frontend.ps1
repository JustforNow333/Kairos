$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "frontend")

Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
npm install

Write-Host "Starting frontend at http://localhost:3000 ..." -ForegroundColor Green
npm run dev

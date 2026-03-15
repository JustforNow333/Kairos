$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$python = $null
try {
    $python = & py -3.11 -c "import sys; print(sys.executable)"
} catch {
    Write-Host "Python 3.11 is required but was not found via 'py -3.11'." -ForegroundColor Red
    Write-Host "Install Python 3.11, then rerun this script." -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    Write-Host "Creating root virtual environment with Python 3.11..." -ForegroundColor Cyan
    & py -3.11 -m venv venv
}

$venvPython = Join-Path $PSScriptRoot "venv\Scripts\python.exe"

$version = & $venvPython -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ($version -ne "3.11") {
    Write-Host "Rebuilding venv with Python 3.11..." -ForegroundColor Cyan
    Remove-Item -Recurse -Force ".\venv"
    & py -3.11 -m venv venv
}

$venvPython = Join-Path $PSScriptRoot "venv\Scripts\python.exe"

Write-Host "Upgrading pip..." -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip

Write-Host "Installing backend dependencies..." -ForegroundColor Cyan
& $venvPython -m pip install -r requirements.txt

Write-Host "Starting backend at http://localhost:8000 ..." -ForegroundColor Green
& $venvPython -m uvicorn backend.app.main:app --reload --reload-dir backend/app

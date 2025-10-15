# Quick Start Script - Content Analysis Platform

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Content Analysis Platform Setup     " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "1. Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   Python not found! Install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Create venv
Write-Host ""
Write-Host "2. Setting up virtual environment..." -ForegroundColor Yellow
if (!(Test-Path "venv")) {
    python -m venv venv
    Write-Host "   Created virtual environment" -ForegroundColor Green
} else {
    Write-Host "   Virtual environment exists" -ForegroundColor Green
}

# Activate venv
Write-Host ""
Write-Host "3. Activating environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
Write-Host "   Activated" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "4. Installing dependencies..." -ForegroundColor Yellow
Write-Host "   This may take a few minutes..." -ForegroundColor Gray
pip install -q -r backend/requirements.txt
pip install -q streamlit plotly pandas
Write-Host "   Dependencies installed" -ForegroundColor Green

# Check .env
Write-Host ""
Write-Host "5. Checking configuration..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
    } else {
        "OPENAI_API_KEY=your-key-here`nANTHROPIC_API_KEY=your-key-here" | Out-File ".env"
    }
    Write-Host "   Created .env file" -ForegroundColor Green
    Write-Host "   IMPORTANT: Edit .env and add your API key!" -ForegroundColor Red
} else {
    Write-Host "   .env file exists" -ForegroundColor Green
}

# Find app
Write-Host ""
Write-Host "6. Locating application..." -ForegroundColor Yellow
$app = ""
if (Test-Path "backend\src\ui\streamlit_app.py") {
    $app = "backend\src\ui\streamlit_app.py"
} elseif (Test-Path "frontend\app.py") {
    $app = "frontend\app.py"
}

if ($app -eq "") {
    Write-Host "   App not found!" -ForegroundColor Red
    exit 1
}

Write-Host "   Found: $app" -ForegroundColor Green

# Complete
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Setup Complete!                      " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env and add your API key" -ForegroundColor Yellow
Write-Host "2. Run: streamlit run $app" -ForegroundColor Cyan
Write-Host ""

# Ask to launch
$launch = Read-Host "Launch now? (y/n)"
if ($launch -eq "y") {
    Write-Host ""
    Write-Host "Launching..." -ForegroundColor Green
    Write-Host "Opening at http://localhost:8501" -ForegroundColor Cyan
    Write-Host ""
    streamlit run $app
} else {
    Write-Host ""
    Write-Host "To launch later: streamlit run $app" -ForegroundColor Yellow
}

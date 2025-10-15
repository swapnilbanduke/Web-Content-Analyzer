# Quick Setup and Run Script for Content Analysis Platform
# Run this to start the Streamlit application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Content Analysis Platform - Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host $pythonVersion -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "Virtual environment found!" -ForegroundColor Green
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "Virtual environment created!" -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host ""

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$streamlitInstalled = pip list | Select-String -Pattern "streamlit"
if ($streamlitInstalled) {
    Write-Host "Dependencies already installed!" -ForegroundColor Green
} else {
    Write-Host "Installing dependencies (this may take a few minutes)..." -ForegroundColor Yellow
    pip install streamlit plotly pandas python-dotenv
    Write-Host "Dependencies installed!" -ForegroundColor Green
}
Write-Host ""

# Check .env file
Write-Host "Checking configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host ".env file found!" -ForegroundColor Green
    
    # Check if API key is set
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "OPENAI_API_KEY=sk-") {
        Write-Host "OpenAI API key configured!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "WARNING: OpenAI API key not found in .env file" -ForegroundColor Red
        Write-Host "Please add your API key to the .env file:" -ForegroundColor Yellow
        Write-Host "OPENAI_API_KEY=sk-your-api-key-here" -ForegroundColor Yellow
        Write-Host ""
        $continue = Read-Host "Continue anyway? (y/n)"
        if ($continue -ne "y") {
            Write-Host "Exiting..." -ForegroundColor Red
            exit
        }
    }
} else {
    Write-Host ".env file not found - you'll need to enter API key in the UI" -ForegroundColor Yellow
}
Write-Host ""

# Check if Streamlit app exists
$streamlitApp = ""
if (Test-Path "backend\src\ui\streamlit_app.py") {
    $streamlitApp = "backend\src\ui\streamlit_app.py"
    Write-Host "Found Streamlit app: $streamlitApp" -ForegroundColor Green
} elseif (Test-Path "frontend\app.py") {
    $streamlitApp = "frontend\app.py"
    Write-Host "Found Streamlit app: $streamlitApp" -ForegroundColor Green
} else {
    Write-Host "ERROR: Streamlit app not found!" -ForegroundColor Red
    Write-Host "Looking for: backend\src\ui\streamlit_app.py or frontend\app.py" -ForegroundColor Yellow
    exit
}
Write-Host ""

# Launch Streamlit
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Content Analysis Platform..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The application will open in your browser at http://localhost:8501" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run Streamlit
streamlit run $streamlitApp --server.port 8501

Write-Host ""
Write-Host "Application stopped." -ForegroundColor Yellow

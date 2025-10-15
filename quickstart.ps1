# Quick Start Script - Content Analysis Platform
# Run this to set up and launch the application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Content Analysis Platform Setup     " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "1. Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   Found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
Write-Host ""
Write-Host "2. Setting up virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "   ✓ Virtual environment already exists" -ForegroundColor Green
} else {
    Write-Host "   Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "   ✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "3. Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
Write-Host "   ✓ Virtual environment activated" -ForegroundColor Green

# Install backend dependencies
Write-Host ""
Write-Host "4. Installing backend dependencies..." -ForegroundColor Yellow
Write-Host "   This may take a few minutes..." -ForegroundColor Gray
pip install -q -r backend/requirements.txt
Write-Host "   ✓ Backend dependencies installed" -ForegroundColor Green

# Install Streamlit and UI dependencies
Write-Host ""
Write-Host "5. Installing Streamlit and UI dependencies..." -ForegroundColor Yellow
pip install -q streamlit plotly pandas
Write-Host "   ✓ UI dependencies installed" -ForegroundColor Green

# Check for .env file
Write-Host ""
Write-Host "6. Checking configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "   .env file found" -ForegroundColor Green
} else {
    Write-Host "   .env file not found" -ForegroundColor Yellow
    Write-Host "   Creating .env from template..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "   .env file created" -ForegroundColor Green
    } else {
        # Create basic .env file
        $envContent = "# API Keys`nOPENAI_API_KEY=your-openai-key-here`nANTHROPIC_API_KEY=your-anthropic-key-here`n`n# Default Settings`nDEFAULT_AI_PROVIDER=openai`nDEFAULT_AI_MODEL=gpt-4"
        $envContent | Out-File -FilePath ".env" -Encoding utf8
        Write-Host "   Created basic .env file" -ForegroundColor Green
    }
    Write-Host ""
    Write-Host "   IMPORTANT: Please edit .env and add your API keys!" -ForegroundColor Red
    Write-Host ""
}

# Check if Streamlit UI exists
Write-Host ""
Write-Host "7. Checking application files..." -ForegroundColor Yellow

$streamlitApp = $null

if (Test-Path "backend\src\ui\streamlit_app.py") {
    $streamlitApp = "backend\src\ui\streamlit_app.py"
    Write-Host "   ✓ Found: backend\src\ui\streamlit_app.py" -ForegroundColor Green
} elseif (Test-Path "frontend\app.py") {
    $streamlitApp = "frontend\app.py"
    Write-Host "   ✓ Found: frontend\app.py" -ForegroundColor Green
} else {
    Write-Host "   ✗ Streamlit app not found!" -ForegroundColor Red
    Write-Host "   Looking for one of:" -ForegroundColor Yellow
    Write-Host "   - backend\src\ui\streamlit_app.py" -ForegroundColor Gray
    Write-Host "   - frontend\app.py" -ForegroundColor Gray
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Setup Complete! 🎉                  " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Display instructions
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Make sure you have an API key configured in .env" -ForegroundColor Yellow
Write-Host "   Edit .env and set:" -ForegroundColor Gray
Write-Host "   OPENAI_API_KEY=your-key-here" -ForegroundColor Gray
Write-Host "   OR" -ForegroundColor Gray
Write-Host "   ANTHROPIC_API_KEY=your-key-here" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Launch the application:" -ForegroundColor Yellow
Write-Host "   streamlit run $streamlitApp" -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to launch now
$launch = Read-Host "Would you like to launch the application now? (y/n)"

if ($launch -eq "y" -or $launch -eq "Y") {
    Write-Host ""
    Write-Host "Launching Content Analysis Platform..." -ForegroundColor Green
    Write-Host ""
    Write-Host "The app will open in your browser at: http://localhost:8501" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the application" -ForegroundColor Gray
    Write-Host ""
    
    streamlit run $streamlitApp
} else {
    Write-Host ""
    Write-Host "To launch later, run:" -ForegroundColor Yellow
    Write-Host "   streamlit run $streamlitApp" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or simply run this script again!" -ForegroundColor Gray
    Write-Host ""
}

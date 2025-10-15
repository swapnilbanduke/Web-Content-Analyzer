# 🔍 Installation Verification Script

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Web Content Analyzer - Installation Check    " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Python installed: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Docker
Write-Host "`nChecking Docker..." -ForegroundColor Yellow
$dockerVersion = docker --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker installed: $dockerVersion" -ForegroundColor Green
} else {
    Write-Host "⚠️  Docker not found (optional for manual setup)" -ForegroundColor Yellow
}

# Check Docker Compose
Write-Host "`nChecking Docker Compose..." -ForegroundColor Yellow
$composeVersion = docker-compose --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker Compose installed: $composeVersion" -ForegroundColor Green
} else {
    Write-Host "⚠️  Docker Compose not found (optional for manual setup)" -ForegroundColor Yellow
}

# Check project structure
Write-Host "`nChecking project structure..." -ForegroundColor Yellow

$requiredDirs = @(
    "backend",
    "backend\src",
    "backend\src\api",
    "backend\src\services",
    "backend\src\scrapers",
    "backend\src\processors",
    "frontend",
    "frontend\src",
    "frontend\src\components"
)

$missingDirs = @()
foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "  ✅ $dir" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $dir (missing)" -ForegroundColor Red
        $missingDirs += $dir
    }
}

# Check key files
Write-Host "`nChecking key files..." -ForegroundColor Yellow

$requiredFiles = @(
    "backend\main.py",
    "backend\requirements.txt",
    "backend\Dockerfile",
    "frontend\app.py",
    "frontend\requirements.txt",
    "frontend\Dockerfile",
    "docker-compose.yml",
    "README.md"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file (missing)" -ForegroundColor Red
        $missingFiles += $file
    }
}

# Check .env file
Write-Host "`nChecking environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✅ .env file exists" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  .env file not found" -ForegroundColor Yellow
    Write-Host "     Run: cp .env.example .env" -ForegroundColor Yellow
}

# Summary
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "  Installation Summary" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

if ($missingDirs.Count -eq 0 -and $missingFiles.Count -eq 0) {
    Write-Host "✅ All required files and directories are present!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "  1. Create .env file: cp .env.example .env" -ForegroundColor White
    Write-Host "  2. (Optional) Add OpenAI API key to .env" -ForegroundColor White
    Write-Host "  3. Start with Docker: docker-compose up -d" -ForegroundColor White
    Write-Host "  4. Or run manually - see QUICKSTART.md" -ForegroundColor White
    Write-Host "`n📖 For detailed instructions, see README.md and QUICKSTART.md" -ForegroundColor Cyan
} else {
    Write-Host "❌ Installation incomplete!" -ForegroundColor Red
    if ($missingDirs.Count -gt 0) {
        Write-Host "`nMissing directories:" -ForegroundColor Red
        $missingDirs | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    }
    if ($missingFiles.Count -gt 0) {
        Write-Host "`nMissing files:" -ForegroundColor Red
        $missingFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    }
}

Write-Host "`n================================================" -ForegroundColor Cyan

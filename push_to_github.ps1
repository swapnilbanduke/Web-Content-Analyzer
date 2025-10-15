# Git Setup and Push Script
Write-Host "`nInitializing Git repository and pushing to GitHub...`n" -ForegroundColor Cyan

cd "d:\MLops\Github projects\Amzur\Web content analyzer"

# Initialize git if needed
if (-not (Test-Path ".git")) {
    git init
    Write-Host "✅ Git initialized" -ForegroundColor Green
}

# Add remote
git remote add origin https://github.com/swapnilbanduke/Web-Content-Analyzer.git 2>$null
git remote set-url origin https://github.com/swapnilbanduke/Web-Content-Analyzer.git

# Stage all files
Write-Host "`nStaging files..." -ForegroundColor Yellow
git add .

# Create commit
Write-Host "`nCreating commit..." -ForegroundColor Yellow
git commit -m "Initial commit: Web Content Analyzer with AI-powered analysis

Features:
- AI-powered content analysis (OpenAI, Anthropic, Google Gemini)
- SEO analysis with keyword optimization and structure validation
- Sentiment analysis and topic extraction
- Readability scoring (Flesch, Gunning Fog, SMOG, Coleman-Liau)
- Competitive analysis
- Multi-format reports (HTML, PDF, JSON)
- Batch processing support
- Streamlit web interface

Tech Stack:
- Python 3.13+, Streamlit, BeautifulSoup4, httpx
- OpenAI, Anthropic, Google Generative AI APIs
- Plotly visualizations, xhtml2pdf for PDFs

Setup: See README.md and GETTING_STARTED.md"

# Push to GitHub
Write-Host "`nPushing to GitHub..." -ForegroundColor Yellow
git branch -M main
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "Repository: https://github.com/swapnilbanduke/Web-Content-Analyzer" -ForegroundColor Cyan
} else {
    Write-Host "`n⚠️ Push may have failed. Check your GitHub authentication." -ForegroundColor Yellow
}

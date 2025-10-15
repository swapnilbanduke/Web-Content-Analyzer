# 🎯 Getting Started - Visual Guide

## Step 1: Verify Installation ✅

Run the verification script in PowerShell:

```powershell
cd "d:\MLops\Github projects\Amzur\Web content analyzer"
.\verify-installation.ps1
```

## Step 2: Choose Your Deployment Method 🚀

### Option A: Docker (Recommended) 🐳

```
┌─────────────────────────────────────────┐
│  Step 1: Copy environment file          │
│  cp .env.example .env                   │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  Step 2: Start Docker containers        │
│  docker-compose up -d                   │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  Step 3: Access the application         │
│  Frontend: http://localhost:8501        │
│  Backend:  http://localhost:8000/docs   │
└─────────────────────────────────────────┘
```

**Commands:**
```powershell
# Copy environment template
cp .env.example .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

### Option B: Manual Setup 💻

```
┌──────────────────────┐    ┌──────────────────────┐
│   Terminal 1         │    │   Terminal 2         │
│   BACKEND            │    │   FRONTEND           │
└──────────────────────┘    └──────────────────────┘
          ↓                            ↓
┌──────────────────────┐    ┌──────────────────────┐
│ cd backend           │    │ cd frontend          │
│ python -m venv venv  │    │ python -m venv venv  │
│ .\venv\Scripts\      │    │ .\venv\Scripts\      │
│    activate          │    │    activate          │
│ pip install -r       │    │ pip install -r       │
│    requirements.txt  │    │    requirements.txt  │
│ python main.py       │    │ streamlit run app.py │
└──────────────────────┘    └──────────────────────┘
          ↓                            ↓
┌─────────────────────────────────────────────────┐
│     Backend runs on: http://localhost:8000      │
│     Frontend runs on: http://localhost:8501     │
└─────────────────────────────────────────────────┘
```

**Terminal 1 - Backend:**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

---

## Step 3: Test the Application 🧪

### Visual Testing Flow:

```
1. Open Browser
   ↓
   http://localhost:8501
   ↓
2. Enter URL
   ↓
   [https://example.com]
   ↓
3. Configure Options (optional)
   ☑ Include AI Analysis
   ☐ Aggressive Cleaning
   ↓
4. Click "Analyze Website"
   ↓
5. View Results! 🎉
   - Page Info
   - Content Stats
   - AI Analysis
   - Detailed Report
```

### Test URLs:
- ✅ `https://example.com` - Simple test page
- ✅ `https://python.org` - Rich content
- ✅ `https://github.com` - Complex layout

---

## Step 4: (Optional) Add LLM Support 🤖

### Enable AI Analysis:

```
┌─────────────────────────────────────────┐
│  1. Get OpenAI API Key                  │
│     → https://platform.openai.com       │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  2. Edit .env file                      │
│     OPENAI_API_KEY=sk-...               │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  3. Restart services                    │
│     Docker: docker-compose restart      │
│     Manual: Stop and restart servers    │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  4. AI features now enabled! ✅         │
│     - Summaries                         │
│     - Key points                        │
│     - Sentiment analysis                │
│     - Topic extraction                  │
└─────────────────────────────────────────┘
```

---

## Architecture Overview 🏗️

```
┌─────────────────────────────────────────────────────┐
│                    YOUR BROWSER                     │
│              http://localhost:8501                  │
└────────────────────┬────────────────────────────────┘
                     │
           ┌─────────▼──────────┐
           │   STREAMLIT UI     │
           │   (Frontend)       │
           │   Port: 8501       │
           └─────────┬──────────┘
                     │ HTTP API
           ┌─────────▼──────────┐
           │   FastAPI Server   │
           │   (Backend)        │
           │   Port: 8000       │
           └─────────┬──────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌────────┐  ┌─────────┐  ┌──────────┐
   │Scraper │  │Processor│  │LLM (AI)  │
   │        │  │         │  │          │
   └────────┘  └─────────┘  └──────────┘
        │            │            │
        └────────────┼────────────┘
                     ▼
              ┌─────────────┐
              │   Report    │
              └─────────────┘
```

---

## Quick Commands Reference 📝

### Docker Commands
```powershell
# Start
docker-compose up -d

# Stop
docker-compose down

# Rebuild
docker-compose build --no-cache

# Logs
docker-compose logs -f

# Status
docker-compose ps
```

### Development Commands
```powershell
# Run tests
cd backend
pytest tests/ -v

# Format code
black backend/src frontend/src

# Check style
flake8 backend/src
```

### Helpful Checks
```powershell
# Check if backend is running
curl http://localhost:8000/api/v1/health

# Check Docker status
docker ps

# View application logs
docker-compose logs backend
docker-compose logs frontend
```

---

## Troubleshooting Quick Fixes 🔧

### Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <pid> /F
```

### Docker Issues
```powershell
# Clean restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Python/Venv Issues
```powershell
# Make sure you're in the right directory
pwd

# Recreate virtual environment
rm -r venv
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

## Success Checklist ✅

After starting the application:

- [ ] Backend health check: http://localhost:8000/api/v1/health
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Frontend loads: http://localhost:8501
- [ ] Can enter URL in frontend
- [ ] Can analyze a test URL
- [ ] Results display correctly
- [ ] No error messages in logs

---

## What's Next? 🎯

1. **Explore Features**
   - Try different websites
   - Test with/without AI analysis
   - Check the detailed reports

2. **Customize**
   - Modify UI in `frontend/app.py`
   - Add new analysis features in `backend/src/services/`
   - Adjust settings in `.env`

3. **Learn More**
   - Read `README.md` for architecture details
   - Check `PROJECT_SUMMARY.md` for overview
   - Explore API docs at `/docs`

4. **Extend**
   - Add more processors
   - Integrate different LLMs
   - Add database storage
   - Implement authentication

---

## Support & Resources 📚

- 📖 Full Documentation: `README.md`
- ⚡ Quick Start: `QUICKSTART.md`
- 📊 Project Overview: `PROJECT_SUMMARY.md`
- 🔧 API Reference: http://localhost:8000/docs (when running)

---

**Happy Analyzing! 🚀**

Built with ❤️ using FastAPI & Streamlit

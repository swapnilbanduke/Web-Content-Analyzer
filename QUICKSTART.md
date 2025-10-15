# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone <repository-url>
cd "Web content analyzer"

# 2. Create environment file (optional for basic usage)
cp .env.example .env

# 3. Start the application
docker-compose up -d

# 4. Open your browser
# Frontend: http://localhost:8501
# Backend API: http://localhost:8000/docs
```

### Option 2: Manual Setup

#### Backend

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
python main.py
```

#### Frontend (Open new terminal)

```powershell
# Navigate to frontend
cd frontend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the frontend
streamlit run app.py
```

## 📝 Usage

1. Open http://localhost:8501 in your browser
2. Enter a website URL (e.g., https://example.com)
3. Click "Analyze Website"
4. View comprehensive analysis results!

## 🔑 Optional: Add LLM Support

To enable AI-powered analysis:

1. Get an OpenAI API key from https://platform.openai.com
2. Edit `.env` file:
   ```
   OPENAI_API_KEY=your-key-here
   ```
3. Restart the services

## 🛠️ Common Commands

### Docker

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

### Local Development

```bash
# Backend (from backend folder)
python main.py

# Frontend (from frontend folder)
streamlit run app.py

# Run tests
pytest tests/ -v
```

## ❓ Troubleshooting

### Port Already in Use

If you get a port conflict:

```bash
# Change ports in docker-compose.yml
# Backend: "8001:8000" instead of "8000:8000"
# Frontend: "8502:8501" instead of "8501:8501"
```

### Docker Issues

```bash
# Clean rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Module Import Errors

Make sure you're in the correct directory and virtual environment is activated:

```bash
# Check current directory
pwd

# Activate venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

## 🎯 Next Steps

- Explore the API documentation at http://localhost:8000/docs
- Check out the full README.md for detailed documentation
- Try analyzing different types of websites
- Customize the analysis options in the settings

Happy analyzing! 🎉

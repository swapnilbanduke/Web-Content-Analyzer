# Content Analysis Platform# 🌐 Web Content Analyzer



[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)A comprehensive web application that extracts content from any website URL and generates detailed analysis reports using AI-powered insights.

[![Streamlit](https://img.shields.io/badge/streamlit-1.30+-red.svg)](https://streamlit.io/)

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)![Architecture](https://img.shields.io/badge/Architecture-Microservices-blue)

[![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)]()![Backend](https://img.shields.io/badge/Backend-FastAPI-green)

![Frontend](https://img.shields.io/badge/Frontend-Streamlit-red)

**Professional AI-Powered Web Content Analysis Platform**![AI](https://img.shields.io/badge/AI-LLM%20Powered-purple)



Analyze web content across 6 dimensions using GPT-4 or Claude, generate professional reports, and gain actionable insights through a beautiful Streamlit interface.## 🚀 Features



![Platform Screenshot](docs/images/platform-screenshot.png)### Core Capabilities

- **Web Scraping**: Extract content from any publicly accessible website

---- **Content Analysis**: Comprehensive text analysis including word count, readability, keywords

- **AI-Powered Insights**: Generate summaries, key points, and sentiment analysis using LLMs

## 🌟 Features- **SEO Analysis**: Extract and analyze metadata, headings, and page structure

- **Batch Processing**: Analyze multiple URLs in a single request

### Core Capabilities- **Report Generation**: Create detailed, downloadable analysis reports

- ✅ **Web Scraping**: Extract content from any public URL

- ✅ **AI Analysis**: 6-dimensional content analysis using OpenAI or Anthropic### Technical Features

- ✅ **Report Generation**: Professional HTML/PDF reports with visualizations- ✅ **Clean Architecture**: Separation of concerns with distinct layers (API, Service, Data)

- ✅ **Batch Processing**: Analyze multiple URLs simultaneously- ✅ **Security First**: SSRF protection, input validation, rate limiting

- ✅ **Web Interface**: Beautiful Streamlit UI with interactive charts- ✅ **Async Processing**: Fast, non-blocking I/O operations

- ✅ **Export Options**: PDF, JSON, CSV, and HTML formats- ✅ **Error Handling**: Comprehensive error handling and logging

- ✅ **Docker Support**: Easy deployment with Docker Compose

### Analysis Dimensions- ✅ **Scalable**: Microservices architecture ready for horizontal scaling

1. **Content Summary**: Short, medium, and long summaries with key points

2. **Sentiment & Tone**: Emotional analysis and tone detection## 📋 Table of Contents

3. **Topics & Themes**: Main topics, entities, and keyword extraction

4. **SEO Analysis**: Keyword optimization, meta tags, and recommendations- [Architecture](#architecture)

5. **Readability**: Multiple formulas, accessibility checks, improvements- [Project Structure](#project-structure)

6. **Competitive Analysis**: Content gaps, UVPs, positioning (optional)- [Getting Started](#getting-started)

- [Installation](#installation)

### Report Features- [Configuration](#configuration)

- 📊 Interactive visualizations (gauges, charts, graphs)- [Usage](#usage)

- 🎨 4 professional themes (Professional, Modern, Minimal, Colorful)- [API Documentation](#api-documentation)

- 📑 Executive summaries with key findings- [Development](#development)

- 🎯 Actionable recommendations- [Testing](#testing)

- 📈 Comprehensive scoring and metrics- [Deployment](#deployment)

- [Contributing](#contributing)

---- [License](#license)



## 🚀 Quick Start (5 Minutes)## 🏗️ Architecture



### PrerequisitesThe application follows a microservices architecture with clear separation of concerns:

- Python 3.8 or higher

- pip package manager### Backend (FastAPI)

- OpenAI or Anthropic API key

```

### Installation┌─────────────────────────────────────────────┐

│           API LAYER                         │

1. **Clone the repository**│  - Routes (/analyze, /batch, /health)       │

```bash│  - Middleware (CORS, Logging, Rate Limit)   │

git clone <repository-url>└─────────────────────────────────────────────┘

cd "Web content analyzer"                    ↓

```┌─────────────────────────────────────────────┐

│         SERVICE LAYER                       │

2. **Install dependencies**│  - Analysis Service (orchestration)         │

```bash│  - Scraping Service                         │

cd backend│  - LLM Service                              │

pip install -r requirements.txt│  - Report Service                           │

pip install -r streamlit_requirements.txt└─────────────────────────────────────────────┘

```                    ↓

┌─────────────────────────────────────────────┐

3. **Set your API key**│       DATA PROCESSING LAYER                 │

│  ┌─────────────┐    ┌──────────────┐        │

**Windows PowerShell:**│  │  Scrapers   │    │  Processors  │        │

```powershell│  │ - Web       │    │ - Text       │        │

$env:OPENAI_API_KEY = "your-openai-api-key"│  │ - Content   │    │ - Cleaner    │        │

```│  └─────────────┘    └──────────────┘        │

└─────────────────────────────────────────────┘

4. **Launch the application**                    ↓

```bash┌─────────────────────────────────────────────┐

python launch_ui.py│      UTILITIES & SECURITY                   │

```│  - Validators  - Security  - Helpers        │

│  - Models      - Exceptions - Config        │

The application opens at `http://localhost:8501`└─────────────────────────────────────────────┘

```

### First Analysis

### Frontend (Streamlit)

1. Enter API key in sidebar (if not set)

2. Select AI Provider and Model```

3. Paste a URL┌─────────────────────────────────────────────┐

4. Click "🚀 Analyze"│         UI COMPONENTS                       │

5. View results across 7 tabs│  - URL Input  - Results Display             │

6. Export in any format│  - Progress UI                              │

└─────────────────────────────────────────────┘

---                    ↓

┌─────────────────────────────────────────────┐

## 📖 Documentation│         SERVICES                            │

│  - API Client (Backend communication)       │

### Quick References│  - State Manager (Session management)       │

- **[Quick Start Guide](QUICK_START.md)** - 5-minute setup└─────────────────────────────────────────────┘

- **[User Guide](STREAMLIT_UI_GUIDE.md)** - Comprehensive UI documentation                    ↓

- **[API Documentation](docs/API_REFERENCE.md)** - Python API reference┌─────────────────────────────────────────────┐

- **[Testing Guide](docs/TESTING.md)** - Testing procedures│         UTILITIES                           │

- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment│  - Formatters  - Validators  - Constants    │

└─────────────────────────────────────────────┘

### Implementation Details```

- **[Project Overview](PROJECT_OVERVIEW.md)** - Complete system overview

- **[Implementation Summary](IMPLEMENTATION_COMPLETE.md)** - Development summary## 📁 Project Structure

- **Step-by-step guides** in `STEP*.md` files

```

---project_root/

├── backend/                    # Backend FastAPI Application

## 💻 Usage│   ├── src/

│   │   ├── api/               # API Layer

### Web Interface (Recommended)│   │   │   ├── __init__.py

│   │   │   ├── routes.py      # API endpoints

```bash│   │   │   └── middleware.py  # Request/response middleware

cd backend│   │   ├── services/          # Service Layer

python launch_ui.py│   │   │   ├── analysis_service.py

```│   │   │   ├── scraping_service.py

│   │   │   ├── llm_service.py

**Features:**│   │   │   └── report_service.py

- Single URL analysis with 7 result tabs│   │   ├── scrapers/          # Data Layer - Scraping

- Batch processing up to 50 URLs│   │   │   ├── web_scraper.py

- Interactive Plotly visualizations│   │   │   └── content_extractor.py

- Multiple export formats│   │   ├── processors/        # Data Layer - Processing

- Analysis history with filtering│   │   │   ├── text_processor.py

- Theme customization│   │   │   └── content_cleaner.py

│   │   ├── models/            # Data Models

### Python API│   │   │   └── data_models.py

│   │   ├── utils/             # Utilities

```python│   │   │   ├── validators.py

import asyncio│   │   │   ├── security.py

from src.scraper import WebScraper, ScraperConfig│   │   │   ├── exceptions.py

from src.ai import create_ai_analysis_service, AnalysisConfig│   │   │   └── helpers.py

from src.reports import ReportGenerator, ReportConfig, ReportFormat│   │   └── config/            # Configuration

│   │       └── settings.py

async def analyze_url(url: str):│   ├── main.py                # FastAPI entry point

    # 1. Scrape content│   ├── requirements.txt

    scraper = WebScraper(ScraperConfig())│   └── Dockerfile

    result = await scraper.scrape_url(url)│

    ├── frontend/                  # Frontend Streamlit Application

    # 2. Analyze with AI│   ├── src/

    ai_service = await create_ai_analysis_service(│   │   ├── components/        # UI Components

        provider="openai",│   │   │   ├── url_input.py

        model="gpt-4-turbo"│   │   │   ├── results_display.py

    )│   │   │   └── progress.py

    │   │   ├── services/          # Frontend Services

    analysis = await ai_service.analyze(│   │   │   ├── api_client.py

        content=result.content,│   │   │   └── state_manager.py

        title=result.title,│   │   └── utils/             # Frontend Utilities

        url=url,│   │       ├── formatters.py

        config=AnalysisConfig()│   │       ├── validators.py

    )│   │       └── constants.py

    │   ├── app.py                 # Streamlit entry point

    # 3. Generate report│   ├── requirements.txt

    generator = ReportGenerator(ReportConfig(│   └── Dockerfile

        format=ReportFormat.HTML│

    ))├── docker-compose.yml         # Docker orchestration

    ├── .env.example              # Environment variables template

    report = await generator.generate_report(├── .gitignore

        analysis_result=analysis,└── README.md

        title=result.title,```

        url=url

    )## 🚀 Getting Started

    

    # 4. Save report### Prerequisites

    with open("report.html", "w") as f:

        f.write(report.content)- **Python 3.11+**

    - **Docker & Docker Compose** (optional, for containerized deployment)

    return analysis- **OpenAI API Key** (optional, for LLM features)



# Run### Quick Start with Docker

asyncio.run(analyze_url("https://example.com/article"))

```1. **Clone the repository**

   ```bash

---   git clone <repository-url>

   cd "Web content analyzer"

## 🏗️ Architecture   ```



```2. **Set up environment variables**

┌─────────────────────────────────────────────────────────┐   ```bash

│                   Presentation Layer                     │   cp .env.example .env

│  ┌──────────────────┐         ┌──────────────────┐     │   # Edit .env and add your OpenAI API key (optional)

│  │  Streamlit UI    │         │  Python API      │     │   ```

│  └────────┬─────────┘         └────────┬─────────┘     │

└───────────┼───────────────────────────┼────────────────┘3. **Start the application**

            │                           │   ```bash

┌───────────┴───────────────────────────┴────────────────┐   docker-compose up -d

│              Application Layer                          │   ```

│  ┌──────────────────────────────────────────────────┐  │

│  │      AI Analysis Service (Orchestrator)          │  │4. **Access the application**

│  │      ├─ Summary Analyzer                         │  │   - Frontend: http://localhost:8501

│  │      ├─ Sentiment Analyzer                       │  │   - Backend API: http://localhost:8000

│  │      ├─ Topics Analyzer                          │  │   - API Documentation: http://localhost:8000/docs

│  │      ├─ SEO Analyzer                             │  │

│  │      ├─ Readability Analyzer                     │  │### Manual Installation

│  │      └─ Competitive Analyzer                     │  │

│  └──────────────────────────────────────────────────┘  │#### Backend Setup

│  ┌───────────────────┐    ┌──────────────────┐        │

│  │  Report Generator │    │   Web Scraper    │        │```bash

│  └───────────────────┘    └──────────────────┘        │cd backend

└─────────────────────────────────────────────────────────┘

            │                           │# Create virtual environment

┌───────────┴───────────────────────────┴────────────────┐python -m venv venv

│              Integration Layer                          │

│  ┌──────────────┐         ┌──────────────┐             │# Activate virtual environment

│  │  OpenAI API  │         │ Anthropic API │             │# On Windows:

│  └──────────────┘         └──────────────┘             │venv\Scripts\activate

└─────────────────────────────────────────────────────────┘# On Linux/Mac:

```source venv/bin/activate



### Tech Stack# Install dependencies

pip install -r requirements.txt

**Backend:**

- Python 3.8+# Run the backend

- aiohttp (async HTTP)python main.py

- BeautifulSoup4 (HTML parsing)```

- OpenAI/Anthropic APIs

- Pydantic (data validation)#### Frontend Setup



**Frontend:**```bash

- Streamlit (web framework)cd frontend

- Plotly (visualizations)

- Pandas (data manipulation)# Create virtual environment

python -m venv venv

**Reports:**

- WeasyPrint (PDF generation)# Activate virtual environment

- Chart.js (interactive charts)venv\Scripts\activate  # Windows

- Custom HTML/CSS templates# source venv/bin/activate  # Linux/Mac



---# Install dependencies

pip install -r requirements.txt

## 📦 Installation

# Run the frontend

### System Requirementsstreamlit run app.py

- Python 3.8, 3.9, 3.10, 3.11, or 3.12```

- 2GB+ RAM

- Internet connection## ⚙️ Configuration



### Detailed Setup### Environment Variables



```bashCreate a `.env` file in the root directory:

# 1. Create virtual environment (recommended)

python -m venv venv```env

venv\Scripts\activate  # Windows# LLM Configuration

# source venv/bin/activate  # Linux/MacOPENAI_API_KEY=your-api-key-here

LLM_MODEL=gpt-3.5-turbo

# 2. Install core dependencies

cd backend# API Configuration

pip install -r requirements.txtAPI_HOST=0.0.0.0

API_PORT=8000

# 3. Install UI dependencies

pip install -r streamlit_requirements.txt# Scraping Settings

SCRAPING_TIMEOUT=30

# 4. Install optional (PDF generation)MAX_CONTENT_SIZE=10485760

pip install weasyprint

# Rate Limiting

# 5. Verify installationRATE_LIMIT_REQUESTS=100

python check_ui_dependencies.pyRATE_LIMIT_WINDOW=60

``````



---### Configuration Files



## ⚙️ Configuration- **Backend**: `backend/src/config/settings.py`

- **Frontend**: `frontend/src/utils/constants.py`

### API Keys (Required)

## 📖 Usage

**Option 1: Environment Variables**

```powershell### Web Interface

# Windows

$env:OPENAI_API_KEY = "sk-..."1. Open http://localhost:8501 in your browser

$env:ANTHROPIC_API_KEY = "sk-ant-..."2. Enter a website URL in the input field

3. Configure analysis options (optional)

# Linux/Mac4. Click "Analyze Website"

export OPENAI_API_KEY="sk-..."5. View comprehensive analysis results

export ANTHROPIC_API_KEY="sk-ant-..."

```### API Usage



**Option 2: .env File**#### Analyze Single URL

```env

OPENAI_API_KEY=sk-...```bash

ANTHROPIC_API_KEY=sk-ant-...curl -X POST "http://localhost:8000/api/v1/analyze" \

```  -H "Content-Type: application/json" \

  -d '{

**Option 3: UI Sidebar**    "url": "https://example.com",

- Enter directly in the application    "include_llm_analysis": true

  }'

### Configuration Files```



See `backend/src/config/` for:#### Health Check

- `scraper_config.py` - Scraping settings

- `analysis_config.py` - Analysis options```bash

- `report_config.py` - Report settingscurl http://localhost:8000/api/v1/health

```

---

## 📚 API Documentation

## 🧪 Testing

### Endpoints

### Run Tests

#### `POST /api/v1/analyze`

```bashAnalyze a single URL and generate comprehensive report.

cd backend

**Request Body:**

# Run all tests```json

python -m pytest tests/ -v{

  "url": "https://example.com",

# Run with coverage  "include_llm_analysis": true,

python -m pytest tests/ --cov=src --cov-report=html  "options": {}

}

# Run specific test```

python -m pytest tests/test_scraper.py -v

```**Response:**

```json

### Manual Testing{

  "url": "https://example.com",

```bash  "status": "success",

# Test scraper  "timestamp": "2025-10-10T12:00:00",

python examples/scraper_example.py  "processing_time": 2.5,

  "metadata": {...},

# Test AI analysis  "content_summary": {...},

python examples/ai_analysis_example.py  "analysis": {...},

  "report": {...}

# Test report generation}

python examples/report_generation_example.py```



# Test web UI#### `POST /api/v1/batch`

python launch_ui.pyAnalyze multiple URLs in batch.

```

#### `GET /api/v1/health`

See [TESTING.md](docs/TESTING.md) for comprehensive testing guide.Health check endpoint.



---**Interactive Documentation:**

- Swagger UI: http://localhost:8000/docs

## 🚢 Deployment- ReDoc: http://localhost:8000/redoc



### Local Development## 🛠️ Development

```bash

python launch_ui.py### Code Style

```

```bash

### Docker# Format code with black

```bashblack backend/src frontend/src

docker build -t content-analyzer .

docker run -p 8501:8501 -e OPENAI_API_KEY=your-key content-analyzer# Lint with flake8

```flake8 backend/src frontend/src



### Cloud Platforms# Type checking with mypy

- **Streamlit Cloud**: One-click deploymentmypy backend/src

- **AWS**: ECS, Elastic Beanstalk, Lambda```

- **Azure**: App Service, Container Instances

- **GCP**: Cloud Run, App Engine### Project Guidelines



See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed guides.- Follow PEP 8 style guide

- Write comprehensive docstrings

---- Add type hints to function signatures

- Keep functions small and focused

## 📊 Performance- Write unit tests for new features



**Single Analysis** (1,000 words):## 🧪 Testing

- Scraping: 1-3 seconds

- AI Analysis: 20-30 seconds (GPT-4)```bash

- Report Gen: <2 seconds# Backend tests

- **Total**: ~25-35 secondscd backend

pytest tests/ -v --cov=src

**Batch Processing**:

- 5 URLs: 2-3 minutes# Run specific test file

- 10 URLs: 4-6 minutespytest tests/test_api.py -v

- 20 URLs: 8-12 minutes```



---## 🚢 Deployment



## 💰 Costs### Docker Deployment



**Per Analysis** (1,000-word article):```bash

- GPT-4 Turbo: $0.02-$0.05# Build and start services

- GPT-3.5 Turbo: $0.001-$0.002docker-compose up -d

- Claude Opus: $0.02-$0.05

- Claude Haiku: $0.001-$0.003# View logs

docker-compose logs -f

**Monthly** (3,000 analyses):

- GPT-4: $60-$150# Stop services

- GPT-3.5: $3-$6docker-compose down

```

---

### Production Considerations

## 🐛 Troubleshooting

1. **Environment Variables**: Use proper secrets management

### Common Issues2. **HTTPS**: Configure SSL/TLS certificates

3. **Rate Limiting**: Adjust based on your needs

**"Module not found":**4. **Monitoring**: Add logging and monitoring solutions

```bash5. **Scalability**: Use load balancers for multiple instances

pip install -r requirements.txt streamlit_requirements.txt

```## 🔒 Security Features



**"API key not configured":**- **SSRF Protection**: Blocks access to private IP ranges

```bash- **Input Validation**: Validates all user inputs

$env:OPENAI_API_KEY = "your-key"- **Rate Limiting**: Prevents abuse

```- **Content Sanitization**: Prevents XSS attacks

- **Error Handling**: Secure error messages

**"Port in use":**

```bash## 🤝 Contributing

streamlit run src/ui/streamlit_app.py --server.port=8502

```Contributions are welcome! Please follow these steps:



**"PDF generation failed":**1. Fork the repository

```bash2. Create a feature branch (`git checkout -b feature/AmazingFeature`)

pip install weasyprint3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)

```4. Push to the branch (`git push origin feature/AmazingFeature`)

5. Open a Pull Request

See [Troubleshooting Guide](docs/TROUBLESHOOTING.md) for more solutions.

## 📝 License

---

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎓 Examples

## 👥 Authors

### Content Audit

```python- Your Name - Initial work

# Analyze all blog posts

urls = ["url1", "url2", "url3"]## 🙏 Acknowledgments

results = asyncio.run(batch_analyze(urls))

- FastAPI for the excellent web framework

# Export to CSV- Streamlit for the intuitive UI framework

export_to_csv(results, "audit.csv")- OpenAI for LLM capabilities

```- BeautifulSoup for HTML parsing



### SEO Optimization## 📧 Contact

```python

# Analyze pageFor questions or support, please open an issue on GitHub.

analysis = await analyze_url("https://example.com")

---

# Check SEO score

print(f"SEO: {analysis.seo_analysis.overall_score:.0%}")**Built with ❤️ for comprehensive web content analysis**


# Get recommendations
for issue in analysis.seo_analysis.issues:
    print(f"- {issue.description}")
```

### Competitive Research
```python
# Enable competitive analysis
config = AnalysisConfig(
    include_competitive=True,
    competitor_urls=["competitor1.com", "competitor2.com"]
)

# Analyze
analysis = await ai_service.analyze(content, title, url, config)

# View gaps
for gap in analysis.competitive_analysis.content_gaps:
    print(f"Gap: {gap.description}")
```

More examples in `backend/examples/`

---

## 🤝 Contributing

We welcome contributions!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

Built with:
- [OpenAI](https://openai.com/) - GPT-4 analysis
- [Anthropic](https://anthropic.com/) - Claude analysis
- [Streamlit](https://streamlit.io/) - Web framework
- [Plotly](https://plotly.com/) - Visualizations
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [WeasyPrint](https://weasyprint.org/) - PDF generation

---

## 📞 Support

- 📖 **Docs**: See `docs/` directory
- 💬 **Issues**: GitHub Issues
- 💡 **Examples**: See `examples/` directory

---

## 🗺️ Roadmap

### v1.0 (Current) ✅
- Complete analysis platform
- Web interface
- Batch processing
- Report generation

### v2.0 (Planned)
- User authentication
- Database integration
- Scheduled analysis
- Email delivery
- API endpoints
- Mobile app

---

## ⭐ Star History

If you find this project useful, please give it a star!

---

**Made with ❤️ using Python, Streamlit, and AI**

**Version**: 1.0.0 | **Status**: Production Ready ✅ | **Updated**: October 10, 2025

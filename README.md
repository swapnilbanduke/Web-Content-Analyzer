# 🌐 Web Content Analyzer

AI-powered web content analysis platform that extracts, analyzes, and generates intelligent insights from any website.

## ✨ Features

- **Web Scraping**: Extract content from any public URL
- **AI Analysis**: 6-dimensional content analysis (Summary, Sentiment, Topics, SEO, Readability, Competitive)
- **Report Generation**: Professional HTML, PDF, JSON, and CSV reports
- **Batch Processing**: Analyze multiple URLs simultaneously
- **Beautiful UI**: Interactive Streamlit interface with visualizations
- **Export Options**: Download reports in multiple formats
- **Security**: SSRF protection, input validation, rate limiting

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI or Anthropic API key (optional for basic analysis)

### Installation

```bash
# Clone the repository
git clone https://github.com/swapnilbanduke/Web-Content-Analyzer.git
cd Web-Content-Analyzer

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows
# or source venv/bin/activate  # On Linux/Mac

# Install dependencies
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### Run Application

```bash
# Using Streamlit (Recommended)
streamlit run backend/src/ui/streamlit_app.py --server.port 8501

# Using Docker
docker-compose up -d
```

Visit http://localhost:8501 in your browser.

## 📊 Analysis Capabilities

| Feature | Description |
|---------|-------------|
| **Content Summary** | Short, medium, and long summaries with key points |
| **Sentiment Analysis** | Emotional tone and sentiment detection |
| **Topics & Keywords** | Main topics, entities, and keyword extraction |
| **SEO Analysis** | Meta tags, keywords optimization, recommendations |
| **Readability** | Readability formulas, accessibility checks |
| **Competitive Analysis** | Content gaps, unique value propositions, positioning |

## 🏗️ Project Structure

```
Web-Content-Analyzer/
├── backend/
│   ├── src/
│   │   ├── ai/              # AI/LLM services
│   │   ├── scrapers/        # Web scraping
│   │   ├── analyzers/       # Content analysis
│   │   ├── reports/         # Report generation
│   │   ├── storage/         # Database
│   │   ├── ui/              # Streamlit interface
│   │   └── services/        # Business logic
│   ├── tests/               # Unit tests
│   ├── examples/            # Usage examples
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── services/        # API services
│   │   └── utils/           # Utilities
│   ├── app.py               # Main app
│   └── requirements.txt     # Dependencies
├── docs/                    # Documentation
├── docker-compose.yml       # Docker setup
├── .env.example             # Environment template
└── README.md                # This file
```

## 🔧 Configuration

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# OpenAI Configuration
OPENAI_API_KEY=your-api-key-here
LLM_MODEL=gpt-3.5-turbo

# Or use Anthropic Claude
ANTHROPIC_API_KEY=your-api-key-here
```

## 💻 Usage

### Via Streamlit UI

1. Open http://localhost:8501
2. Enter a website URL
3. Select analysis options (SEO, Sentiment, Readability, etc.)
4. Add your API key in the sidebar
5. Click "Analyze"
6. View results and export reports

### Via API

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "analyze_seo": true,
    "analyze_sentiment": true,
    "analyze_readability": true
  }'
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.8+
- **Frontend**: Streamlit
- **AI/LLM**: OpenAI GPT, Anthropic Claude
- **Database**: SQLite
- **Web Scraping**: BeautifulSoup4, httpx
- **Visualization**: Plotly
- **Deployment**: Docker, Docker Compose

## 📦 Docker Deployment

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🧪 Testing

```bash
# Run tests
pytest backend/tests/

# Run with coverage
pytest --cov=backend backend/tests/
```

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/analyze` | Analyze single URL |
| POST | `/api/v1/batch-analyze` | Analyze multiple URLs |
| GET | `/api/v1/status` | Check API status |
| GET | `/docs` | API documentation (Swagger) |

## 🔒 Security

- ✅ SSRF Protection: Blocks access to private IP ranges
- ✅ Input Validation: Comprehensive input sanitization
- ✅ Rate Limiting: Prevents abuse
- ✅ Error Handling: Safe error messages without exposing internals

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🤖 AI Services Supported

- **OpenAI**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
- **Anthropic**: Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku

## 📞 Support

For issues and questions:
1. Check [GETTING_STARTED.md](GETTING_STARTED.md) for setup help
2. Review [docs/](docs/) for detailed documentation
3. Open an issue on GitHub

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI powered by [Streamlit](https://streamlit.io/)
- AI capabilities from [OpenAI](https://openai.com/) and [Anthropic](https://www.anthropic.com/)

---

**Made with ❤️ by Swapnil Banduke**

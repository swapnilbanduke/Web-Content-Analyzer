"""
Constants - Frontend application constants
"""

# API Configuration
DEFAULT_API_URL = "http://localhost:8000"
API_TIMEOUT = 60

# UI Configuration
APP_TITLE = "🌐 Web Content Analyzer"
APP_ICON = "🔍"
PAGE_TITLE = "Web Content Analyzer"

# Analysis Options
DEFAULT_INCLUDE_LLM = True
DEFAULT_AGGRESSIVE_CLEAN = False

# Display Limits
MAX_KEYWORDS_DISPLAY = 10
MAX_HEADINGS_DISPLAY = 10
MAX_HISTORY_ITEMS = 10

# Colors
COLOR_SUCCESS = "#28a745"
COLOR_ERROR = "#dc3545"
COLOR_WARNING = "#ffc107"
COLOR_INFO = "#17a2b8"

# Messages
MSG_WELCOME = """
Welcome to the Web Content Analyzer! 👋

This tool helps you analyze any website and extract comprehensive insights using AI-powered analysis.

**Features:**
- 📊 Content statistics (word count, readability, etc.)
- 🤖 AI-powered summaries and key points
- 🔍 SEO and metadata analysis
- 📈 Sentiment and topic analysis
- 📋 Comprehensive reports

Simply enter a URL above to get started!
"""

MSG_NO_RESULTS = "👆 Enter a URL above to start analyzing"

MSG_LOADING = "⏳ Analyzing website..."

MSG_ERROR_GENERIC = "An error occurred during analysis. Please try again."

# Help Text
HELP_URL_INPUT = "Enter the full URL of the website you want to analyze"
HELP_LLM_ANALYSIS = "Use LLM for advanced content analysis including summaries and key points"
HELP_AGGRESSIVE_CLEAN = "Remove URLs, emails, and special characters from text processing"

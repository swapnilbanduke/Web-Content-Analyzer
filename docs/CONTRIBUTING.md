# Contributing Guide - Content Analysis Platform

Thank you for your interest in contributing to the Content Analysis Platform! This guide will help you get started.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards others

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of async/await in Python
- (Optional) Docker for containerized development

### First-Time Setup

1. **Fork the Repository**

```bash
# Go to GitHub and click "Fork"
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/content-analyzer.git
cd content-analyzer
```

2. **Add Upstream Remote**

```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/content-analyzer.git
git remote -v
```

3. **Create Virtual Environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

4. **Install Dependencies**

```bash
# Install core dependencies
pip install -r backend/requirements.txt

# Install UI dependencies
pip install streamlit plotly

# Install development dependencies
pip install pytest pytest-asyncio pytest-cov pytest-mock black flake8 mypy
```

5. **Set Up Environment Variables**

```bash
# Copy example .env file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edit .env and add your API keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

6. **Run Tests**

```bash
cd backend
pytest tests/ -v
```

7. **Run Application**

```bash
streamlit run frontend/streamlit_app.py
```

---

## Development Setup

### Recommended IDE: VS Code

**Extensions:**
- Python (Microsoft)
- Pylance
- Python Test Explorer
- GitLens
- Docker (optional)

**VS Code Settings** (`.vscode/settings.json`):

```json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "editor.formatOnSave": true,
    "editor.rulers": [88],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

### Git Workflow

```bash
# Update your fork
git checkout main
git fetch upstream
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Add feature: description"

# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

---

## Project Structure

```
Web content analyzer/
│
├── frontend/
│   └── streamlit_app.py          # Main UI (1,300+ lines)
│
├── backend/
│   ├── src/                       # Source code
│   │   ├── scraper/              # Web scraping
│   │   ├── ai/                   # AI analysis
│   │   └── reports/              # Report generation
│   │
│   └── tests/                     # Test suite
│       ├── conftest.py           # Fixtures
│       ├── test_scraper.py
│       ├── test_ai_service.py
│       └── test_reports.py
│
├── docs/                          # Documentation
│   ├── TESTING.md
│   ├── API_REFERENCE.md
│   ├── DEPLOYMENT.md
│   ├── PROJECT_SUMMARY.md
│   └── CONTRIBUTING.md (this file)
│
├── README.md                      # Main documentation
├── .env.example                   # Environment template
└── requirements.txt               # Dependencies
```

---

## Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

**Line Length:**
- Maximum 88 characters (Black default)
- Use line breaks for readability

**Naming Conventions:**
```python
# Classes: PascalCase
class WebScraper:
    pass

# Functions/methods: snake_case
def analyze_content():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3

# Private: leading underscore
def _internal_helper():
    pass
```

**Type Hints:**
```python
from typing import List, Dict, Optional

async def scrape_url(
    url: str,
    timeout: int = 30
) -> Optional[ScrapeResult]:
    """
    Scrape content from URL.
    
    Args:
        url: The URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        ScrapeResult if successful, None otherwise
    """
    pass
```

**Docstrings:**
```python
def analyze(content: str, title: str) -> AnalysisResult:
    """
    Analyze content and generate insights.
    
    This function performs comprehensive analysis including
    sentiment, topics, SEO, and readability.
    
    Args:
        content: The text content to analyze
        title: Content title for context
        
    Returns:
        AnalysisResult with all analysis dimensions
        
    Raises:
        ValueError: If content is empty
        AIServiceError: If AI analysis fails
        
    Example:
        >>> result = await analyze("Sample text", "Title")
        >>> print(result.overall_quality_score)
        0.85
    """
    pass
```

### Code Formatting

**Use Black:**
```bash
# Format all Python files
black backend/src/ backend/tests/ frontend/

# Check without changes
black --check backend/src/
```

**Use Flake8:**
```bash
# Lint code
flake8 backend/src/ --max-line-length=88

# Ignore specific rules in .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503
```

**Use MyPy:**
```bash
# Type checking
mypy backend/src/ --strict
```

### Import Organization

```python
# Standard library
import asyncio
import json
from datetime import datetime
from typing import List, Optional

# Third-party
import aiohttp
from bs4 import BeautifulSoup
import streamlit as st

# Local
from src.scraper import WebScraper
from src.ai import create_ai_analysis_service
from src.reports import ReportGenerator
```

---

## Testing Guidelines

### Writing Tests

**Test File Naming:**
- Test files: `test_*.py`
- Test classes: `TestClassName`
- Test functions: `test_functionality`

**Test Structure:**
```python
import pytest

class TestWebScraper:
    """Test web scraping functionality"""
    
    @pytest.fixture
    def scraper(self):
        """Create scraper instance for tests"""
        return WebScraper(ScraperConfig())
    
    @pytest.mark.asyncio
    async def test_scrape_valid_url(self, scraper):
        """Test scraping a valid URL"""
        # Arrange
        url = "https://example.com"
        
        # Act
        result = await scraper.scrape_url(url)
        
        # Assert
        assert result.success is True
        assert len(result.content) > 0
    
    @pytest.mark.asyncio
    async def test_scrape_invalid_url(self, scraper):
        """Test handling of invalid URL"""
        # Arrange
        url = "invalid-url"
        
        # Act & Assert
        with pytest.raises(ValueError):
            await scraper.scrape_url(url)
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific file
pytest tests/test_scraper.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Stop on first failure
pytest tests/ -x

# Run in parallel
pytest tests/ -n auto
```

### Test Coverage Goals

- **Overall**: >80%
- **Critical paths**: >90%
- **Error handling**: 100%

### Mocking

```python
from unittest.mock import Mock, AsyncMock, patch

@pytest.mark.asyncio
async def test_with_mock_llm():
    """Test with mocked LLM service"""
    with patch('src.ai.llm_service.OpenAIService') as mock_llm:
        # Configure mock
        mock_llm.return_value.generate = AsyncMock(
            return_value={"result": "test"}
        )
        
        # Test code
        service = await create_ai_analysis_service()
        result = await service.analyze("content", "title")
        
        # Verify
        assert result is not None
        mock_llm.return_value.generate.assert_called_once()
```

---

## Pull Request Process

### Before Submitting

**1. Update Your Branch**
```bash
git checkout main
git pull upstream main
git checkout feature/your-feature
git rebase main
```

**2. Run Tests**
```bash
pytest tests/ -v
```

**3. Check Code Quality**
```bash
black backend/src/ backend/tests/ frontend/
flake8 backend/src/
mypy backend/src/
```

**4. Update Documentation**
- Add/update docstrings
- Update README if needed
- Add examples if applicable

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated
```

### Review Process

1. **Automated Checks**: CI/CD runs tests and linting
2. **Code Review**: Maintainer reviews code
3. **Feedback**: Address review comments
4. **Approval**: Maintainer approves PR
5. **Merge**: PR is merged to main

### After Merge

```bash
# Update your fork
git checkout main
git pull upstream main
git push origin main

# Delete feature branch
git branch -d feature/your-feature
git push origin --delete feature/your-feature
```

---

## Documentation

### Documentation Standards

**README Updates:**
- Keep README concise
- Link to detailed docs in `docs/`
- Update version numbers
- Add new features to feature list

**API Documentation:**
- Update `docs/API_REFERENCE.md` for new APIs
- Include examples
- Document all parameters and return types

**Inline Comments:**
```python
# Good: Explain WHY, not WHAT
# Retry with exponential backoff to handle transient network errors
await retry_with_backoff(scrape_url, url)

# Bad: Obvious comment
# Call scrape_url function
result = await scrape_url(url)
```

### Documentation Workflow

1. Write code with docstrings
2. Update API reference if needed
3. Add examples to README
4. Update CHANGELOG.md
5. Update version in `__init__.py`

---

## Issue Reporting

### Bug Reports

**Use this template:**

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: Windows 10
- Python: 3.10
- Version: 1.0.0

## Screenshots
(if applicable)

## Additional Context
Any other relevant information
```

### Feature Requests

**Use this template:**

```markdown
## Feature Description
Clear description of the feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should it work?

## Alternatives Considered
Other approaches you've thought of

## Additional Context
Any other relevant information
```

---

## Development Tips

### Debugging

**Print Debugging:**
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Processing URL: {url}")
logger.info(f"Analysis complete: {score}")
logger.error(f"Failed to scrape: {error}")
```

**VS Code Debugger:**
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Streamlit",
            "type": "python",
            "request": "launch",
            "module": "streamlit",
            "args": [
                "run",
                "frontend/streamlit_app.py"
            ]
        },
        {
            "name": "Python: Pytest",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": [
                "tests/",
                "-v"
            ]
        }
    ]
}
```

### Performance Optimization

**Profile Code:**
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile
await analyze_content(content, title)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

**Async Best Practices:**
```python
# Good: Concurrent execution
tasks = [scrape_url(url) for url in urls]
results = await asyncio.gather(*tasks)

# Bad: Sequential execution
results = []
for url in urls:
    result = await scrape_url(url)
    results.append(result)
```

---

## Questions?

### Getting Help

1. **Documentation**: Check docs/ folder
2. **Issues**: Search existing issues on GitHub
3. **Discussions**: Start a discussion on GitHub
4. **Discord**: Join our community (if available)

### Contact

- **GitHub Issues**: For bugs and features
- **GitHub Discussions**: For questions
- **Email**: maintainer@example.com (if applicable)

---

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in commit history

Thank you for contributing to Content Analysis Platform! 🎉

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Happy contributing!** 🚀

# Testing Guide - Content Analysis Platform

## Overview

This document provides comprehensive testing procedures for the Content Analysis Platform, including unit tests, integration tests, manual testing, and validation procedures.

## Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Unit Tests](#unit-tests)
- [Integration Tests](#integration-tests)
- [Manual Testing](#manual-testing)
- [Website Validation](#website-validation)
- [Performance Testing](#performance-testing)
- [Test Coverage](#test-coverage)
- [Continuous Integration](#continuous-integration)

---

## Testing Philosophy

### Goals
- **Reliability**: Ensure all features work as expected
- **Quality**: Maintain high code quality standards
- **Confidence**: Enable safe refactoring and updates
- **Documentation**: Tests serve as living documentation

### Principles
1. **Test Early**: Write tests during development
2. **Test Often**: Run tests before every commit
3. **Test Thoroughly**: Cover edge cases and error paths
4. **Test Realistically**: Use real-world scenarios

---

## Test Structure

### Directory Organization

```
backend/tests/
├── conftest.py                 # Pytest configuration and fixtures
├── test_scraper.py            # Web scraper tests
├── test_ai_service.py         # AI analysis service tests
├── test_analyzers.py          # Individual analyzer tests
├── test_reports.py            # Report generation tests
├── test_integration.py        # End-to-end integration tests
├── test_ui.py                 # Streamlit UI tests (optional)
└── mocks/                     # Mock data and responses
    ├── __init__.py
    ├── mock_llm_responses.py
    └── sample_content.py
```

### Test Categories

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows
4. **Manual Tests**: Human validation of features

---

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov pytest-mock

# Install project dependencies
pip install -r requirements.txt
```

### Basic Test Execution

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_scraper.py -v

# Run specific test function
pytest tests/test_scraper.py::TestWebScraper::test_scrape_valid_url -v

# Run tests with specific marker
pytest tests/ -m "not integration" -v
```

### Advanced Options

```bash
# Run with coverage report
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Run in parallel (faster)
pytest tests/ -n auto

# Stop on first failure
pytest tests/ -x

# Show print statements
pytest tests/ -s

# Run only failed tests from last run
pytest tests/ --lf

# Verbose output with full diff
pytest tests/ -vv
```

### Test Output

**Successful test:**
```
tests/test_scraper.py::TestWebScraper::test_scraper_initialization PASSED [10%]
```

**Failed test:**
```
tests/test_scraper.py::TestWebScraper::test_invalid_url FAILED [20%]
_____ TestWebScraper.test_invalid_url _____
AssertionError: Expected failure but got success
```

---

## Unit Tests

### Web Scraper Tests

**File**: `tests/test_scraper.py`

**Coverage**:
- Configuration validation
- URL validation
- Content extraction
- Metadata parsing
- Error handling
- Timeout handling
- Retry logic

**Example Test**:
```python
import pytest
from src.scraper import WebScraper, ScraperConfig

@pytest.mark.asyncio
async def test_scrape_valid_url():
    """Test scraping a valid URL"""
    scraper = WebScraper(ScraperConfig())
    result = await scraper.scrape_url("https://example.com")
    
    assert result.success is True
    assert len(result.content) > 0
    assert result.word_count > 0
```

**Run**:
```bash
pytest tests/test_scraper.py -v
```

### AI Service Tests

**File**: `tests/test_ai_service.py`

**Coverage**:
- Service initialization
- Configuration management
- Analyzer orchestration
- Error handling
- Cost tracking
- Processing time

**Example Test**:
```python
@pytest.mark.asyncio
async def test_analysis_with_mock_llm(mock_analysis_config, mocker):
    """Test analysis with mocked LLM responses"""
    # Mock LLM service
    mock_llm = mocker.patch('src.ai.llm_service.LLMService')
    mock_llm.return_value.generate.return_value = {"summary": "Test"}
    
    # Create service
    service = await create_ai_analysis_service()
    
    # Run analysis
    result = await service.analyze(
        content="Test content",
        title="Test",
        config=mock_analysis_config
    )
    
    assert result is not None
    assert result.overall_quality_score >= 0
```

### Analyzer Tests

**File**: `tests/test_analyzers.py`

**Coverage**:
- Summary analyzer
- Sentiment analyzer
- Topics analyzer
- SEO analyzer
- Readability analyzer
- Competitive analyzer

**Example Test**:
```python
@pytest.mark.asyncio
async def test_summary_analyzer(mock_llm_summary_response):
    """Test summary analyzer"""
    from src.ai.analyzers import ContentSummarizer
    
    analyzer = ContentSummarizer(mock_llm_service)
    result = await analyzer.analyze(
        content="Sample content",
        title="Test"
    )
    
    assert result.short_summary is not None
    assert result.medium_summary is not None
    assert result.long_summary is not None
    assert len(result.key_points) > 0
```

### Report Tests

**File**: `tests/test_reports.py`

**Coverage**:
- Report generation
- Format conversion (HTML, PDF, JSON, Markdown)
- Theme application
- Chart generation
- Export functionality

**Example Test**:
```python
@pytest.mark.asyncio
async def test_html_report_generation():
    """Test HTML report generation"""
    from src.reports import ReportGenerator, ReportConfig, ReportFormat
    
    config = ReportConfig(format=ReportFormat.HTML)
    generator = ReportGenerator(config)
    
    report = await generator.generate_report(
        analysis_result=mock_analysis,
        title="Test Report"
    )
    
    assert report.content is not None
    assert "<html>" in report.content
    assert report.file_size_bytes > 0
```

---

## Integration Tests

### End-to-End Workflow

**File**: `tests/test_integration.py`

**Test complete workflows**:

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_complete_analysis_workflow():
    """Test complete workflow from URL to report"""
    
    # 1. Scrape content
    scraper = WebScraper(ScraperConfig())
    scrape_result = await scraper.scrape_url(TEST_URL)
    assert scrape_result.success
    
    # 2. Analyze content
    ai_service = await create_ai_analysis_service()
    analysis = await ai_service.analyze(
        content=scrape_result.content,
        title=scrape_result.title,
        url=TEST_URL
    )
    assert analysis.overall_quality_score > 0
    
    # 3. Generate report
    generator = ReportGenerator(ReportConfig())
    report = await generator.generate_report(
        analysis_result=analysis,
        title=scrape_result.title
    )
    assert len(report.content) > 1000
    
    print(f"✅ Complete workflow successful")
```

**Run integration tests**:
```bash
pytest tests/ -m integration -v
```

---

## Manual Testing

### Checklist: Web Scraping

- [ ] Test with HTTPS URL
- [ ] Test with HTTP URL
- [ ] Test with URL containing query parameters
- [ ] Test with URL containing fragments
- [ ] Test with redirect URL
- [ ] Test with slow-loading page
- [ ] Test with JavaScript-heavy page
- [ ] Test with invalid URL
- [ ] Test with timeout
- [ ] Test error handling

### Checklist: AI Analysis

- [ ] Test with short content (<100 words)
- [ ] Test with medium content (100-1000 words)
- [ ] Test with long content (>1000 words)
- [ ] Test with different content types (blog, news, academic)
- [ ] Test with different tones (formal, casual, technical)
- [ ] Test with positive sentiment content
- [ ] Test with negative sentiment content
- [ ] Test with neutral sentiment content
- [ ] Test competitive analysis with competitors
- [ ] Test all analyzers enabled
- [ ] Test individual analyzers disabled

### Checklist: Report Generation

- [ ] Generate HTML report
- [ ] Generate PDF report (requires WeasyPrint)
- [ ] Generate JSON export
- [ ] Generate Markdown export
- [ ] Test Professional theme
- [ ] Test Modern theme
- [ ] Test Minimal theme
- [ ] Test Colorful theme
- [ ] Verify charts display correctly
- [ ] Verify executive summary
- [ ] Verify recommendations section
- [ ] Test report with missing data

### Checklist: Streamlit UI

- [ ] Launch application successfully
- [ ] Enter API key in sidebar
- [ ] Select AI provider (OpenAI)
- [ ] Select AI provider (Anthropic)
- [ ] Analyze single URL
- [ ] View all result tabs
- [ ] Export HTML report
- [ ] Export PDF report
- [ ] Export JSON data
- [ ] Process batch (5 URLs)
- [ ] View batch results table
- [ ] Export batch as CSV
- [ ] View analysis history
- [ ] Filter history by status
- [ ] Filter history by date
- [ ] Clear history
- [ ] Change theme
- [ ] Enable competitive analysis
- [ ] Test with invalid API key
- [ ] Test with network error
- [ ] Test mobile responsiveness

---

## Website Validation

### Pre-Analysis Validation

**Before analyzing a website, verify**:

1. **URL Accessibility**
```python
async def validate_url(url: str) -> bool:
    """Check if URL is accessible"""
    scraper = WebScraper(ScraperConfig())
    result = await scraper.scrape_url(url)
    return result.success
```

2. **Content Quality**
```python
def validate_content(content: str) -> dict:
    """Validate content meets minimum requirements"""
    words = len(content.split())
    
    return {
        'has_content': len(content) > 0,
        'min_words': words >= 50,
        'max_words': words <= 10000,
        'valid': len(content) > 0 and 50 <= words <= 10000
    }
```

3. **Metadata Presence**
```python
def validate_metadata(metadata: dict) -> bool:
    """Check if basic metadata exists"""
    required = ['title', 'description']
    return all(key in metadata for key in required)
```

### Post-Analysis Validation

**After analysis, verify**:

1. **Score Validity**
```python
def validate_scores(analysis) -> bool:
    """Verify all scores are in valid range"""
    scores = [
        analysis.overall_quality_score,
        analysis.seo_analysis.overall_score if analysis.seo_analysis else 0,
        analysis.readability_analysis.overall_score if analysis.readability_analysis else 0
    ]
    
    return all(0 <= score <= 1 for score in scores)
```

2. **Data Completeness**
```python
def validate_analysis_completeness(analysis, config) -> dict:
    """Check if all requested analyses are present"""
    return {
        'summary': analysis.content_summary is not None if config.include_summary else True,
        'sentiment': analysis.sentiment_analysis is not None if config.include_sentiment else True,
        'topics': analysis.topics_analysis is not None if config.include_topics else True,
        'seo': analysis.seo_analysis is not None if config.include_seo else True,
        'readability': analysis.readability_analysis is not None if config.include_readability else True
    }
```

3. **Cost Tracking**
```python
def validate_cost_tracking(analysis) -> bool:
    """Verify cost is tracked"""
    return (
        hasattr(analysis, 'total_cost') and
        analysis.total_cost >= 0 and
        analysis.processing_time_ms > 0
    )
```

### Sample Analysis Validation Script

```python
"""
Validate analysis results for quality assurance
"""

async def validate_analysis_pipeline(url: str):
    """Complete validation pipeline"""
    
    print(f"Validating: {url}")
    
    # 1. Validate URL accessibility
    if not await validate_url(url):
        print("❌ URL not accessible")
        return False
    print("✅ URL accessible")
    
    # 2. Scrape and validate content
    scraper = WebScraper(ScraperConfig())
    result = await scraper.scrape_url(url)
    
    content_validation = validate_content(result.content)
    if not content_validation['valid']:
        print(f"❌ Content validation failed: {content_validation}")
        return False
    print(f"✅ Content valid ({result.word_count} words)")
    
    # 3. Run analysis
    ai_service = await create_ai_analysis_service()
    analysis = await ai_service.analyze(
        content=result.content,
        title=result.title,
        url=url
    )
    
    # 4. Validate scores
    if not validate_scores(analysis):
        print("❌ Invalid scores detected")
        return False
    print("✅ Scores valid")
    
    # 5. Validate completeness
    completeness = validate_analysis_completeness(analysis, AnalysisConfig())
    if not all(completeness.values()):
        print(f"❌ Incomplete analysis: {completeness}")
        return False
    print("✅ Analysis complete")
    
    # 6. Validate cost tracking
    if not validate_cost_tracking(analysis):
        print("❌ Cost tracking failed")
        return False
    print(f"✅ Cost tracked: ${analysis.total_cost:.4f}")
    
    print("\n✅ All validations passed!")
    return True
```

---

## Performance Testing

### Load Testing

```python
async def load_test_analysis(num_requests: int = 10):
    """Test system under load"""
    import time
    
    start = time.time()
    
    tasks = []
    for i in range(num_requests):
        task = analyze_url(f"https://example.com/page{i}")
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    duration = time.time() - start
    successful = sum(1 for r in results if not isinstance(r, Exception))
    
    print(f"Load Test Results:")
    print(f"  Requests: {num_requests}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {num_requests - successful}")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Avg time: {duration/num_requests:.2f}s")
```

### Benchmark Tests

```python
async def benchmark_component(component_name: str, func, *args):
    """Benchmark a component"""
    import time
    
    iterations = 5
    times = []
    
    for i in range(iterations):
        start = time.time()
        await func(*args)
        duration = time.time() - start
        times.append(duration)
    
    avg = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"{component_name} Benchmark:")
    print(f"  Average: {avg:.2f}s")
    print(f"  Min: {min_time:.2f}s")
    print(f"  Max: {max_time:.2f}s")
```

---

## Test Coverage

### Measuring Coverage

```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=html --cov-report=term

# View HTML report
# Open htmlcov/index.html in browser
```

### Coverage Goals

- **Overall**: >80% code coverage
- **Critical paths**: >90% coverage
- **Error handling**: 100% coverage

### Coverage Report Example

```
Name                          Stmts   Miss  Cover
-------------------------------------------------
src/__init__.py                   2      0   100%
src/scraper/web_scraper.py      150     15    90%
src/ai/llm_service.py           200     25    88%
src/ai/analysis_service.py      180     20    89%
src/reports/report_generator.py 250     30    88%
-------------------------------------------------
TOTAL                          1500    150    90%
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
        pip install pytest pytest-cov pytest-asyncio
    
    - name: Run tests
      run: |
        cd backend
        pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./backend/coverage.xml
```

---

## Sample Test Runs

### Example: Running All Tests

```bash
$ pytest tests/ -v

tests/test_scraper.py::TestScraperConfiguration::test_default_config PASSED [5%]
tests/test_scraper.py::TestScraperConfiguration::test_custom_config PASSED [10%]
tests/test_scraper.py::TestWebScraper::test_scraper_initialization PASSED [15%]
tests/test_scraper.py::TestWebScraper::test_url_validation PASSED [20%]
tests/test_analyzers.py::TestSummaryAnalyzer::test_summary_generation PASSED [25%]
tests/test_analyzers.py::TestSentimentAnalyzer::test_sentiment_scoring PASSED [30%]
...
tests/test_integration.py::test_complete_workflow PASSED [100%]

================= 42 passed in 12.34s =================
```

### Example: With Coverage

```bash
$ pytest tests/ --cov=src --cov-report=term

---------- coverage: platform win32, python 3.10 ----------
Name                                Stmts   Miss  Cover
-------------------------------------------------------
src/__init__.py                         2      0   100%
src/scraper/web_scraper.py            150     15    90%
src/ai/llm_service.py                 200     25    88%
src/ai/analyzers/summary_analyzer.py  120     10    92%
src/reports/report_generator.py       250     30    88%
-------------------------------------------------------
TOTAL                                1500    150    90%

================= 42 passed in 12.34s =================
```

---

## Best Practices

### Writing Tests

1. **One assertion per test** (when possible)
2. **Clear test names** describing what is tested
3. **Arrange-Act-Assert** pattern
4. **Use fixtures** for common setup
5. **Mock external dependencies**
6. **Test edge cases** and error conditions

### Test Organization

1. **Group related tests** in classes
2. **Use descriptive class names**
3. **Order tests** logically
4. **Keep tests independent**
5. **Clean up resources** after tests

### Debugging Tests

```bash
# Run with debugger
pytest tests/ --pdb

# Print output
pytest tests/ -s

# Verbose traceback
pytest tests/ -vv

# Only failed tests
pytest tests/ --lf -v
```

---

## Troubleshooting

### Common Issues

**Tests not discovered:**
```bash
# Ensure test files start with 'test_'
# Ensure test functions start with 'test_'
# Check __init__.py files exist
```

**Async tests fail:**
```bash
# Install pytest-asyncio
pip install pytest-asyncio

# Mark async tests
@pytest.mark.asyncio
async def test_something():
    ...
```

**Import errors:**
```bash
# Run from backend directory
cd backend
pytest tests/

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
```

---

## Summary

### Test Execution Checklist

- [ ] Run unit tests: `pytest tests/test_*.py -v`
- [ ] Run integration tests: `pytest tests/ -m integration`
- [ ] Check coverage: `pytest tests/ --cov=src`
- [ ] Run manual tests from checklist
- [ ] Validate sample websites
- [ ] Test UI functionality
- [ ] Verify exports work
- [ ] Check error handling
- [ ] Validate performance
- [ ] Review coverage report

### Success Criteria

- ✅ All unit tests pass
- ✅ Integration tests pass
- ✅ Coverage >80%
- ✅ Manual tests verified
- ✅ No critical bugs
- ✅ Performance acceptable
- ✅ Documentation complete

---

**For more information**, see:
- `conftest.py` - Test fixtures
- `test_*.py` files - Individual test suites
- `examples/` - Working code examples

**Testing is essential for quality!** 🧪✅

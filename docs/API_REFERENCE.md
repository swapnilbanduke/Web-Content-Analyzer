# API Reference - Content Analysis Platform

Complete API documentation for all modules, classes, and functions.

## Table of Contents

- [Core Modules](#core-modules)
- [Web Scraping](#web-scraping)
- [AI Analysis](#ai-analysis)
- [Analyzers](#analyzers)
- [Report Generation](#report-generation)
- [Data Models](#data-models)
- [Configuration](#configuration)
- [Utilities](#utilities)

---

## Core Modules

### Module: `src.scraper`

Web scraping functionality for extracting content from URLs.

### Module: `src.ai`

AI-powered content analysis using LLM models.

### Module: `src.reports`

Report generation in multiple formats (HTML, PDF, JSON, Markdown).

---

## Web Scraping

### Class: `WebScraper`

**Location**: `src/scraper/web_scraper.py`

Main class for web content extraction.

#### Constructor

```python
WebScraper(config: ScraperConfig = None)
```

**Parameters**:
- `config` (ScraperConfig, optional): Scraper configuration. Defaults to `ScraperConfig()`.

**Example**:
```python
from src.scraper import WebScraper, ScraperConfig

config = ScraperConfig(timeout=60, max_retries=5)
scraper = WebScraper(config)
```

#### Methods

##### `scrape_url()`

```python
async def scrape_url(
    url: str,
    custom_headers: dict = None
) -> ScrapeResult
```

Scrape content from a URL.

**Parameters**:
- `url` (str): The URL to scrape
- `custom_headers` (dict, optional): Custom HTTP headers

**Returns**:
- `ScrapeResult`: Scraping result with content and metadata

**Raises**:
- `ValueError`: If URL is invalid
- `TimeoutError`: If request times out
- `Exception`: For other scraping errors

**Example**:
```python
result = await scraper.scrape_url("https://example.com/article")

if result.success:
    print(f"Title: {result.title}")
    print(f"Words: {result.word_count}")
    print(f"Content: {result.content[:500]}")
else:
    print(f"Error: {result.error_message}")
```

##### `scrape_multiple()`

```python
async def scrape_multiple(
    urls: List[str],
    max_concurrent: int = 5
) -> List[ScrapeResult]
```

Scrape multiple URLs concurrently.

**Parameters**:
- `urls` (List[str]): List of URLs to scrape
- `max_concurrent` (int): Maximum concurrent requests

**Returns**:
- `List[ScrapeResult]`: List of scrape results

**Example**:
```python
urls = [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3"
]

results = await scraper.scrape_multiple(urls, max_concurrent=3)

for result in results:
    if result.success:
        print(f"✅ {result.url}: {result.word_count} words")
    else:
        print(f"❌ {result.url}: {result.error_message}")
```

### Class: `ScraperConfig`

**Location**: `src/scraper/config.py`

Configuration for web scraper behavior.

```python
@dataclass
class ScraperConfig:
    timeout: int = 30                    # Request timeout in seconds
    max_retries: int = 3                 # Maximum retry attempts
    retry_delay: float = 1.0             # Delay between retries (seconds)
    follow_redirects: bool = True        # Follow HTTP redirects
    verify_ssl: bool = True              # Verify SSL certificates
    user_agent: str = "ContentAnalyzer"  # Custom user agent
```

**Example**:
```python
config = ScraperConfig(
    timeout=60,
    max_retries=5,
    retry_delay=2.0,
    user_agent="MyBot/1.0"
)
```

### Class: `ScrapeResult`

**Location**: `src/scraper/models.py`

Result of a web scraping operation.

```python
@dataclass
class ScrapeResult:
    url: str                           # Original URL
    success: bool                      # Whether scraping succeeded
    content: str = ""                  # Extracted text content
    html: str = ""                     # Raw HTML
    title: str = ""                    # Page title
    description: str = ""              # Meta description
    keywords: List[str] = field(default_factory=list)  # Meta keywords
    author: str = ""                   # Page author
    published_date: Optional[datetime] = None          # Publication date
    word_count: int = 0                # Word count
    images: List[str] = field(default_factory=list)    # Image URLs
    links: List[str] = field(default_factory=list)     # Link URLs
    metadata: dict = field(default_factory=dict)       # Additional metadata
    error_message: str = ""            # Error message if failed
    scrape_time_ms: int = 0            # Scraping duration
```

---

## AI Analysis

### Function: `create_ai_analysis_service()`

**Location**: `src/ai/analysis_service.py`

Factory function to create an AI analysis service.

```python
async def create_ai_analysis_service(
    provider: str = "openai",
    model: str = None,
    api_key: str = None
) -> AIAnalysisService
```

**Parameters**:
- `provider` (str): AI provider ("openai" or "anthropic")
- `model` (str, optional): Model name. Defaults to provider's default.
- `api_key` (str, optional): API key. Uses environment variable if not provided.

**Returns**:
- `AIAnalysisService`: Configured analysis service

**Example**:
```python
# OpenAI with GPT-4
service = await create_ai_analysis_service(
    provider="openai",
    model="gpt-4",
    api_key="sk-..."
)

# Anthropic with Claude
service = await create_ai_analysis_service(
    provider="anthropic",
    model="claude-3-opus-20240229"
)
```

### Class: `AIAnalysisService`

**Location**: `src/ai/analysis_service.py`

Main service for orchestrating AI-powered content analysis.

#### Methods

##### `analyze()`

```python
async def analyze(
    content: str,
    title: str,
    url: str = "",
    config: AnalysisConfig = None,
    competitors: List[str] = None
) -> AnalysisResult
```

Perform comprehensive content analysis.

**Parameters**:
- `content` (str): Text content to analyze
- `title` (str): Content title
- `url` (str, optional): Source URL
- `config` (AnalysisConfig, optional): Analysis configuration
- `competitors` (List[str], optional): Competitor URLs for comparison

**Returns**:
- `AnalysisResult`: Complete analysis results

**Example**:
```python
from src.ai import create_ai_analysis_service, AnalysisConfig

service = await create_ai_analysis_service()

config = AnalysisConfig(
    include_summary=True,
    include_sentiment=True,
    include_topics=True,
    include_seo=True,
    include_readability=True,
    include_competitive=False
)

result = await service.analyze(
    content="Your article content here...",
    title="Article Title",
    url="https://example.com/article",
    config=config
)

print(f"Quality Score: {result.overall_quality_score:.2f}")
print(f"Summary: {result.content_summary.short_summary}")
print(f"Sentiment: {result.sentiment_analysis.sentiment_score:.2f}")
```

##### `analyze_batch()`

```python
async def analyze_batch(
    items: List[dict],
    config: AnalysisConfig = None,
    max_concurrent: int = 3
) -> List[AnalysisResult]
```

Analyze multiple content items in batch.

**Parameters**:
- `items` (List[dict]): List of dicts with keys: content, title, url
- `config` (AnalysisConfig, optional): Analysis configuration
- `max_concurrent` (int): Maximum concurrent analyses

**Returns**:
- `List[AnalysisResult]`: List of analysis results

**Example**:
```python
items = [
    {"content": "Content 1", "title": "Title 1", "url": "https://example.com/1"},
    {"content": "Content 2", "title": "Title 2", "url": "https://example.com/2"},
]

results = await service.analyze_batch(items, max_concurrent=2)

for result in results:
    print(f"{result.title}: {result.overall_quality_score:.2f}")
```

### Class: `AnalysisConfig`

**Location**: `src/ai/config.py`

Configuration for analysis behavior.

```python
@dataclass
class AnalysisConfig:
    include_summary: bool = True         # Include summary analysis
    include_sentiment: bool = True       # Include sentiment analysis
    include_topics: bool = True          # Include topic extraction
    include_seo: bool = True             # Include SEO analysis
    include_readability: bool = True     # Include readability metrics
    include_competitive: bool = False    # Include competitive analysis
    
    # LLM parameters
    temperature: float = 0.3             # LLM temperature
    max_tokens: int = 4000               # Maximum tokens per request
    
    # Analysis parameters
    num_key_points: int = 5              # Number of key points to extract
    num_topics: int = 10                 # Number of topics to identify
    num_keywords: int = 20               # Number of SEO keywords
```

**Example**:
```python
# SEO-focused analysis
seo_config = AnalysisConfig(
    include_summary=True,
    include_sentiment=False,
    include_topics=True,
    include_seo=True,
    include_readability=True,
    num_keywords=30
)

# Quick analysis (minimal features)
quick_config = AnalysisConfig(
    include_summary=True,
    include_sentiment=True,
    include_topics=False,
    include_seo=False,
    include_readability=False
)
```

---

## Analyzers

### Summary Analyzer

**Class**: `ContentSummarizer`
**Location**: `src/ai/analyzers/summary_analyzer.py`

Generates summaries and extracts key points.

```python
async def analyze(
    content: str,
    title: str,
    num_key_points: int = 5
) -> SummaryAnalysis
```

**Returns**:
```python
@dataclass
class SummaryAnalysis:
    short_summary: str          # 1-sentence summary
    medium_summary: str         # 2-3 sentence summary
    long_summary: str           # Detailed paragraph
    main_takeaway: str          # Key takeaway
    key_points: List[KeyPoint]  # Important points
```

**Example**:
```python
summary = result.content_summary

print(f"Short: {summary.short_summary}")
print(f"Medium: {summary.medium_summary}")
print(f"Long: {summary.long_summary}")

for point in summary.key_points:
    print(f"• {point.text} (importance: {point.importance_score})")
```

### Sentiment Analyzer

**Class**: `SentimentAnalyzer`
**Location**: `src/ai/analyzers/sentiment_analyzer.py`

Analyzes emotional tone and sentiment.

```python
async def analyze(
    content: str,
    title: str
) -> SentimentAnalysis
```

**Returns**:
```python
@dataclass
class SentimentAnalysis:
    sentiment_score: float        # -1 (negative) to +1 (positive)
    confidence: float             # 0 to 1
    tone: List[str]               # ["professional", "optimistic", etc.]
    emotions: dict                # {"joy": 0.8, "anger": 0.1, ...}
    positive_ratio: float         # Ratio of positive content
    neutral_ratio: float          # Ratio of neutral content
    negative_ratio: float         # Ratio of negative content
```

**Example**:
```python
sentiment = result.sentiment_analysis

if sentiment.sentiment_score > 0.5:
    print("Positive content")
elif sentiment.sentiment_score < -0.5:
    print("Negative content")
else:
    print("Neutral content")

print(f"Confidence: {sentiment.confidence:.1%}")
print(f"Tone: {', '.join(sentiment.tone)}")
```

### Topics Analyzer

**Class**: `TopicsAnalyzer`
**Location**: `src/ai/analyzers/topics_analyzer.py`

Extracts topics, themes, entities, and keywords.

```python
async def analyze(
    content: str,
    title: str,
    num_topics: int = 10
) -> TopicsAnalysis
```

**Returns**:
```python
@dataclass
class TopicsAnalysis:
    topics: List[Topic]          # Main topics with relevance
    themes: List[Theme]          # Broader themes
    entities: List[Entity]       # Named entities
    keywords: List[Keyword]      # Important keywords
```

**Example**:
```python
topics = result.topics_analysis

print("Topics:")
for topic in topics.topics:
    print(f"  • {topic.name} ({topic.relevance_score:.0%})")
    for subtopic in topic.subtopics:
        print(f"    - {subtopic}")

print("\nEntities:")
for entity in topics.entities:
    print(f"  • {entity.text} ({entity.entity_type})")
```

### SEO Analyzer

**Class**: `SEOAnalyzer`
**Location**: `src/ai/analyzers/seo_analyzer.py`

Analyzes SEO factors and provides recommendations.

```python
async def analyze(
    content: str,
    title: str,
    url: str,
    num_keywords: int = 20
) -> SEOAnalysis
```

**Returns**:
```python
@dataclass
class SEOAnalysis:
    overall_score: float          # 0 to 1
    content_quality_score: float  # Content quality
    technical_seo_score: float    # Technical factors
    keyword_optimization_score: float  # Keyword usage
    structure_score: float        # Content structure
    links_score: float            # Internal/external links
    meta_tags_score: float        # Meta tag optimization
    keywords: List[SEOKeyword]    # Analyzed keywords
    issues: List[SEOIssue]        # Identified issues
    recommendations: List[str]    # Improvement suggestions
```

**Example**:
```python
seo = result.seo_analysis

print(f"Overall SEO Score: {seo.overall_score:.0%}")
print(f"  Content Quality: {seo.content_quality_score:.0%}")
print(f"  Technical SEO: {seo.technical_seo_score:.0%}")
print(f"  Keyword Optimization: {seo.keyword_optimization_score:.0%}")

print("\nTop Keywords:")
for kw in seo.keywords[:5]:
    print(f"  • {kw.keyword}: {kw.frequency} occurrences")

print("\nIssues:")
for issue in seo.issues:
    if issue.severity == "high":
        print(f"  ⚠️ {issue.description}")
```

### Readability Analyzer

**Class**: `ReadabilityAnalyzer`
**Location**: `src/ai/analyzers/readability_analyzer.py`

Calculates readability metrics and scores.

```python
async def analyze(
    content: str,
    title: str
) -> ReadabilityAnalysis
```

**Returns**:
```python
@dataclass
class ReadabilityAnalysis:
    overall_score: float          # 0 to 1
    reading_level: str            # "Elementary", "High School", etc.
    target_audience: str          # Recommended audience
    formulas: dict                # Readability formula scores
    metrics: dict                 # Text metrics
    accessibility_score: float    # Accessibility rating
    improvement_suggestions: List[str]  # Suggestions
```

**Example**:
```python
readability = result.readability_analysis

print(f"Reading Level: {readability.reading_level}")
print(f"Target Audience: {readability.target_audience}")
print(f"Flesch Reading Ease: {readability.formulas['flesch_reading_ease']}")
print(f"Grade Level: {readability.formulas['flesch_kincaid_grade']}")

print("\nMetrics:")
print(f"  Avg Sentence Length: {readability.metrics['avg_sentence_length']}")
print(f"  Complex Words: {readability.metrics['complex_words_ratio']:.1%}")
```

### Competitive Analyzer

**Class**: `CompetitiveAnalyzer`
**Location**: `src/ai/analyzers/competitive_analyzer.py`

Compares content against competitors.

```python
async def analyze(
    content: str,
    title: str,
    competitors: List[str]
) -> CompetitiveAnalysis
```

**Returns**:
```python
@dataclass
class CompetitiveAnalysis:
    overall_competitiveness: float     # 0 to 1
    strengths: List[str]               # Competitive advantages
    weaknesses: List[str]              # Areas to improve
    opportunities: List[str]           # Market opportunities
    threats: List[str]                 # Competitive threats
    competitor_comparisons: List[CompetitorComparison]
    recommendations: List[str]
```

---

## Report Generation

### Class: `ReportGenerator`

**Location**: `src/reports/report_generator.py`

Generates reports in multiple formats.

#### Constructor

```python
ReportGenerator(config: ReportConfig = None)
```

**Parameters**:
- `config` (ReportConfig, optional): Report configuration

#### Methods

##### `generate_report()`

```python
async def generate_report(
    analysis_result: AnalysisResult,
    title: str,
    format: ReportFormat = None
) -> Report
```

**Parameters**:
- `analysis_result` (AnalysisResult): Analysis results to include
- `title` (str): Report title
- `format` (ReportFormat, optional): Output format

**Returns**:
- `Report`: Generated report

**Example**:
```python
from src.reports import ReportGenerator, ReportConfig, ReportFormat, ReportTheme

config = ReportConfig(
    format=ReportFormat.HTML,
    theme=ReportTheme.PROFESSIONAL,
    include_charts=True,
    include_recommendations=True
)

generator = ReportGenerator(config)

report = await generator.generate_report(
    analysis_result=result,
    title="Content Analysis Report"
)

# Save report
with open("report.html", "w", encoding="utf-8") as f:
    f.write(report.content)

print(f"Report generated: {report.file_size_bytes} bytes")
```

##### `export_json()`

```python
def export_json(
    analysis_result: AnalysisResult
) -> str
```

Export analysis as JSON.

**Example**:
```python
json_data = generator.export_json(result)

with open("analysis.json", "w") as f:
    f.write(json_data)
```

##### `export_markdown()`

```python
def export_markdown(
    analysis_result: AnalysisResult,
    title: str
) -> str
```

Export analysis as Markdown.

**Example**:
```python
md_content = generator.export_markdown(result, "My Analysis")

with open("analysis.md", "w") as f:
    f.write(md_content)
```

### Class: `ReportConfig`

**Location**: `src/reports/config.py`

```python
@dataclass
class ReportConfig:
    format: ReportFormat = ReportFormat.HTML       # Output format
    theme: ReportTheme = ReportTheme.PROFESSIONAL  # Visual theme
    include_charts: bool = True                    # Include visualizations
    include_executive_summary: bool = True         # Include summary
    include_recommendations: bool = True           # Include suggestions
    include_raw_data: bool = False                 # Include raw JSON
    logo_url: str = ""                             # Custom logo URL
    company_name: str = ""                         # Company name
```

### Enums

```python
class ReportFormat(Enum):
    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    MARKDOWN = "markdown"

class ReportTheme(Enum):
    PROFESSIONAL = "professional"
    MODERN = "modern"
    MINIMAL = "minimal"
    COLORFUL = "colorful"
```

---

## Data Models

### Class: `AnalysisResult`

**Location**: `src/ai/models.py`

Complete analysis results.

```python
@dataclass
class AnalysisResult:
    # Meta information
    url: str
    title: str
    analyzed_at: datetime
    
    # Overall score
    overall_quality_score: float
    
    # Individual analyses
    content_summary: Optional[SummaryAnalysis] = None
    sentiment_analysis: Optional[SentimentAnalysis] = None
    topics_analysis: Optional[TopicsAnalysis] = None
    seo_analysis: Optional[SEOAnalysis] = None
    readability_analysis: Optional[ReadabilityAnalysis] = None
    competitive_analysis: Optional[CompetitiveAnalysis] = None
    
    # Metadata
    word_count: int = 0
    processing_time_ms: int = 0
    total_cost: float = 0.0
    provider: str = ""
    model: str = ""
```

---

## Configuration

### Environment Variables

```bash
# AI Provider API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Default AI Provider
DEFAULT_AI_PROVIDER=openai
DEFAULT_AI_MODEL=gpt-4

# Analysis Settings
ANALYSIS_TIMEOUT=300
MAX_CONCURRENT_ANALYSES=3

# Scraper Settings
SCRAPER_TIMEOUT=30
SCRAPER_MAX_RETRIES=3

# Report Settings
DEFAULT_REPORT_FORMAT=html
DEFAULT_REPORT_THEME=professional
```

### Configuration Files

**config.yaml** (optional):
```yaml
ai:
  provider: openai
  model: gpt-4
  temperature: 0.3
  max_tokens: 4000

scraper:
  timeout: 30
  max_retries: 3
  user_agent: "ContentAnalyzer/1.0"

reports:
  format: html
  theme: professional
  include_charts: true
```

---

## Utilities

### Cost Estimation

```python
def estimate_analysis_cost(
    content: str,
    config: AnalysisConfig,
    provider: str = "openai",
    model: str = "gpt-4"
) -> float:
    """
    Estimate the cost of analyzing content.
    
    Args:
        content: Text content to analyze
        config: Analysis configuration
        provider: AI provider
        model: Model name
        
    Returns:
        Estimated cost in USD
    """
```

### Token Counting

```python
def count_tokens(
    text: str,
    model: str = "gpt-4"
) -> int:
    """
    Count the number of tokens in text.
    
    Args:
        text: Text to count
        model: Model for tokenization
        
    Returns:
        Number of tokens
    """
```

---

## Error Handling

### Common Exceptions

```python
class AnalysisError(Exception):
    """Base exception for analysis errors"""
    pass

class ScrapingError(AnalysisError):
    """Raised when web scraping fails"""
    pass

class AIServiceError(AnalysisError):
    """Raised when AI service fails"""
    pass

class ReportGenerationError(AnalysisError):
    """Raised when report generation fails"""
    pass
```

### Error Handling Example

```python
from src.ai import create_ai_analysis_service, AnalysisError

try:
    service = await create_ai_analysis_service()
    result = await service.analyze(content, title)
except ScrapingError as e:
    print(f"Failed to scrape content: {e}")
except AIServiceError as e:
    print(f"AI analysis failed: {e}")
except ReportGenerationError as e:
    print(f"Report generation failed: {e}")
except AnalysisError as e:
    print(f"Analysis error: {e}")
```

---

## Complete Example

```python
import asyncio
from src.scraper import WebScraper, ScraperConfig
from src.ai import create_ai_analysis_service, AnalysisConfig
from src.reports import ReportGenerator, ReportConfig, ReportFormat

async def analyze_url_complete(url: str):
    """Complete analysis workflow"""
    
    # 1. Scrape content
    scraper = WebScraper(ScraperConfig(timeout=60))
    scrape_result = await scraper.scrape_url(url)
    
    if not scrape_result.success:
        print(f"Scraping failed: {scrape_result.error_message}")
        return
    
    print(f"Scraped: {scrape_result.word_count} words")
    
    # 2. Analyze content
    ai_service = await create_ai_analysis_service(
        provider="openai",
        model="gpt-4"
    )
    
    analysis_config = AnalysisConfig(
        include_summary=True,
        include_sentiment=True,
        include_topics=True,
        include_seo=True,
        include_readability=True
    )
    
    analysis = await ai_service.analyze(
        content=scrape_result.content,
        title=scrape_result.title,
        url=url,
        config=analysis_config
    )
    
    print(f"Quality Score: {analysis.overall_quality_score:.2f}")
    print(f"Cost: ${analysis.total_cost:.4f}")
    
    # 3. Generate report
    report_config = ReportConfig(
        format=ReportFormat.HTML,
        include_charts=True
    )
    
    generator = ReportGenerator(report_config)
    report = await generator.generate_report(
        analysis_result=analysis,
        title=scrape_result.title
    )
    
    # 4. Save report
    with open("report.html", "w", encoding="utf-8") as f:
        f.write(report.content)
    
    print(f"Report saved: report.html ({report.file_size_bytes} bytes)")

# Run
asyncio.run(analyze_url_complete("https://example.com/article"))
```

---

**For more examples**, see:
- `examples/` directory
- `tests/` directory
- Main README.md

**Happy coding!** 🚀

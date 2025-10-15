# Data Models API Reference

## Quick Reference

### Request Models

#### URLAnalysisRequest
Complete URL analysis request with validation.

```python
from models.data_models import URLAnalysisRequest

request = URLAnalysisRequest(
    url="https://example.com/article",
    timeout=60,                    # 1-300 seconds
    max_retries=3,                # 0-5 attempts
    extract_metadata=True,
    extract_images=True,
    extract_links=True,
    analyze_structure=True,
    extract_key_phrases=True,
    classify_content=True,
    tags=["article", "tech"]
)
```

**Fields:**
- `url` (HttpUrl, required): URL to analyze
- `timeout` (int, 1-300): Request timeout in seconds (default: 30)
- `max_retries` (int, 0-5): Maximum retry attempts (default: 3)
- `user_agent` (str, optional): Custom user agent
- `extract_metadata` (bool): Extract page metadata (default: True)
- `extract_images` (bool): Extract images (default: True)
- `extract_links` (bool): Extract links (default: True)
- `analyze_structure` (bool): Analyze document structure (default: True)
- `extract_key_phrases` (bool): Extract key phrases (default: True)
- `classify_content` (bool): Classify content type (default: True)
- `clean_html` (bool): Clean HTML content (default: True)
- `normalize_text` (bool): Normalize text (default: True)
- `detect_language` (bool): Detect language (default: True)
- `validate_ssl` (bool): Validate SSL certificates (default: True)
- `max_content_size` (int, 1KB-100MB): Max content size in bytes (default: 10MB)
- `request_id` (str, optional): Request identifier
- `tags` (List[str]): Tags for categorization (max 20)

**Validation:**
- URL must be valid HTTP/HTTPS
- Blocks javascript:, data:, file:, ftp: schemes
- Tags must be alphanumeric with hyphens/underscores
- Extra fields forbidden

#### BatchAnalysisRequest
Batch analysis for multiple URLs.

```python
from models.data_models import BatchAnalysisRequest

batch = BatchAnalysisRequest(
    urls=[
        "https://example.com/1",
        "https://example.com/2",
        "https://example.com/3"
    ],
    parallel_processing=True,
    max_workers=5,              # 1-10 workers
    batch_id="batch-2024-01"
)
```

**Fields:**
- `urls` (List[HttpUrl], 1-100): URLs to analyze (must be unique)
- `shared_config` (dict, optional): Shared configuration
- `parallel_processing` (bool): Process in parallel (default: True)
- `max_workers` (int, 1-10): Max parallel workers (default: 5)
- `batch_id` (str, optional): Batch identifier

**Validation:**
- URLs must be unique
- 1-100 URLs per batch

---

### Content Models

#### ScrapedContent
Raw scraped content with HTTP metadata.

```python
from models.data_models import ScrapedContent

scraped = ScrapedContent(
    url="https://example.com",
    html_content="<html>...</html>",
    status_code=200,
    headers={"Content-Type": "text/html"},
    encoding="utf-8",
    processing_time_ms=150.5
)
```

**Fields:**
- `url` (HttpUrl, required): Source URL
- `html_content` (str, required): Raw HTML content (10+ chars)
- `text_content` (str, optional): Extracted plain text
- `status_code` (int, 100-599): HTTP status code
- `headers` (dict): HTTP response headers
- `content_type` (str, optional): Content-Type header
- `content_length` (int, optional): Content length in bytes
- `encoding` (str): Content encoding (default: "utf-8")
- `scraped_at` (datetime): Scraping timestamp (auto)
- `scraper_version` (str): Scraper version
- `processing_time_ms` (float, optional): Processing time
- `redirect_chain` (List[str]): Redirect chain
- `is_valid_html` (bool): Whether HTML is valid
- `has_errors` (bool): Whether errors occurred
- `errors` (List[str]): Error messages

**Auto-correction:**
- If `errors` list not empty, `has_errors` auto-set to True

#### ProcessedContent
Cleaned and structured content.

```python
from models.data_models import ProcessedContent, Metadata, ContentType

processed = ProcessedContent(
    url="https://example.com",
    processed_text="Cleaned text...",
    word_count=150,
    metadata=Metadata(title="Article Title"),
    content_type=ContentType.BLOG_POST,
    content_type_confidence=0.85,
    language="en",
    language_confidence=0.95
)
```

**Fields:**
- `url` (HttpUrl, required): Source URL
- `processed_text` (str, required): Cleaned text
- `metadata` (Metadata): Extracted metadata
- `headings` (List[Heading]): Document headings
- `sections` (List[Section]): Document sections
- `content_type` (ContentType): Content classification
- `content_type_confidence` (float, 0-1): Classification confidence
- `images` (List[Image], max 1000): Extracted images
- `links` (List[Link], max 5000): Extracted links
- `word_count` (int, required): Word count
- `sentence_count` (int): Sentence count
- `paragraph_count` (int): Paragraph count
- `language` (str, optional): Detected language code
- `language_confidence` (float, 0-1): Language confidence
- `readability_score` (float, 0-100, optional): Readability score
- `key_phrases` (List[dict], max 100): Extracted key phrases
- `keywords` (List[str], max 50): Top keywords

**Auto-correction:**
- Word count auto-corrected if differs from actual by >10

---

### Analysis Models

#### QualityMetrics
Content quality assessment.

```python
from models.data_models import QualityMetrics

metrics = QualityMetrics(
    overall_score=85.5,
    structure_score=90.0,
    readability_score=80.0,
    completeness_score=85.0,
    metadata_score=87.0,
    has_title=True,
    has_description=True,
    has_headings=True,
    has_proper_structure=True,
    issues=["Missing alt text on 2 images"],
    warnings=["Consider adding more internal links"]
)
```

**Fields:**
- `overall_score` (float, 0-100, required): Overall quality score
- `structure_score` (float, 0-100): Structure quality
- `readability_score` (float, 0-100): Readability score
- `completeness_score` (float, 0-100): Completeness score
- `metadata_score` (float, 0-100): Metadata quality
- `has_title` (bool): Has title
- `has_description` (bool): Has description
- `has_headings` (bool): Has headings
- `has_images` (bool): Has images
- `has_proper_structure` (bool): Has proper structure
- `issues` (List[str], max 50): Quality issues
- `warnings` (List[str], max 50): Warnings

#### AnalysisReport
Complete analysis report.

```python
from models.data_models import AnalysisReport, AnalysisStatus

report = AnalysisReport(
    report_id="rpt-123",
    url="https://example.com",
    status=AnalysisStatus.COMPLETED,
    processed_content=processed,
    structure_analysis=structure,
    text_analysis=text,
    quality_metrics=metrics,
    total_processing_time_ms=2500.0,
    recommendations=["Add more headings", "Improve readability"]
)

# Export methods
summary = report.to_summary()           # Compact summary dict
full_dict = report.to_json_export()     # Complete dict
json_str = report.model_dump_json()     # JSON string
```

**Fields:**
- `report_id` (str, required): Unique report ID
- `url` (HttpUrl, required): Analyzed URL
- `status` (AnalysisStatus): Analysis status
- `processed_content` (ProcessedContent, required): Processed content
- `structure_analysis` (StructureAnalysis, required): Structure analysis
- `text_analysis` (TextAnalysis, required): Text analysis
- `quality_metrics` (QualityMetrics, required): Quality metrics
- `recommendations` (List[str], max 20): Recommendations
- `total_processing_time_ms` (float, required): Total time
- `scraping_time_ms` (float, optional): Scraping time
- `processing_time_ms` (float, optional): Processing time
- `analysis_time_ms` (float, optional): Analysis time
- `has_errors` (bool): Has errors
- `errors` (List[dict], max 50): Error details
- `warnings` (List[dict], max 50): Warning details
- `tags` (List[str], max 20): Tags

**Auto-correction:**
- Status changed to PARTIAL if errors exist but status is COMPLETED

**Methods:**
- `to_summary()`: Returns compact summary dict
- `to_json_export()`: Returns complete dict for JSON serialization

---

### Error Models

#### AnalysisError
Detailed error tracking.

```python
from models.data_models import AnalysisError, ErrorSeverity

error = AnalysisError(
    error_code="E001",
    error_type="ValidationError",
    message="Invalid URL format",
    severity=ErrorSeverity.ERROR,
    component="url_validator",
    context={"url": "invalid-url", "reason": "missing_protocol"}
)
```

**Fields:**
- `error_code` (str, required): Error code
- `error_type` (str, required): Error type
- `message` (str, required): Error message
- `severity` (ErrorSeverity): Error severity (default: ERROR)
- `occurred_at` (datetime): Timestamp (auto)
- `component` (str, optional): Component where error occurred
- `traceback` (str, optional): Stack traceback
- `context` (dict): Additional context

---

### Response Models

#### AnalysisResponse
API response wrapper.

```python
from models.data_models import AnalysisResponse

# Success response
response = AnalysisResponse(
    success=True,
    data=report,
    metadata={"version": "1.0.0"}
)

# Error response
response = AnalysisResponse(
    success=False,
    errors=[error],
    warnings=["Partial data available"]
)
```

**Fields:**
- `success` (bool, required): Success status
- `data` (AnalysisReport, optional): Analysis report
- `errors` (List[AnalysisError]): Errors
- `warnings` (List[str]): Warnings
- `metadata` (dict): Additional metadata
- `timestamp` (datetime): Response timestamp (auto)

#### BatchAnalysisResponse
Batch analysis response.

```python
from models.data_models import BatchAnalysisResponse

batch_response = BatchAnalysisResponse(
    success=True,
    batch_id="batch-123",
    total_urls=10,
    successful=8,
    failed=2,
    results=[response1, response2, ...],
    processing_time_ms=5000.0
)
```

**Fields:**
- `success` (bool, required): Overall success
- `batch_id` (str, required): Batch ID
- `total_urls` (int, required): Total URLs
- `successful` (int, required): Successful analyses
- `failed` (int, required): Failed analyses
- `results` (List[AnalysisResponse]): Individual results
- `errors` (List[AnalysisError]): Batch-level errors
- `processing_time_ms` (float, required): Total processing time
- `timestamp` (datetime): Response timestamp (auto)

---

### Enums

#### ContentType
```python
class ContentType(str, Enum):
    BLOG_POST = "blog_post"
    NEWS_ARTICLE = "news_article"
    TECHNICAL_DOCS = "technical_docs"
    ACADEMIC_PAPER = "academic_paper"
    PRODUCT_PAGE = "product_page"
    LANDING_PAGE = "landing_page"
    GENERAL = "general"
```

#### AnalysisStatus
```python
class AnalysisStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"
```

#### ErrorSeverity
```python
class ErrorSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
```

#### SectionType
```python
class SectionType(str, Enum):
    INTRODUCTION = "introduction"
    METHODOLOGY = "methodology"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    REFERENCES = "references"
    APPENDIX = "appendix"
    BODY = "body"
```

---

### Utility Functions

#### validate_url_format
```python
from models.data_models import validate_url_format

# Validates URL format
url = validate_url_format("https://example.com")  # ✓
validate_url_format("javascript:alert()")          # ✗ ValueError
validate_url_format("example.com")                 # ✗ ValueError
```

#### validate_content_length
```python
from models.data_models import validate_content_length

# Validates content length
content = validate_content_length("Long content...", min_length=10, max_length=10000)
```

#### serialize_report
```python
from models.data_models import serialize_report

# JSON string
json_str = serialize_report(report, format="json")

# Dictionary
dict_data = serialize_report(report, format="dict")

# Summary
summary = serialize_report(report, format="summary")
```

---

## Usage Examples

### Complete Analysis Workflow
```python
from models.data_models import (
    URLAnalysisRequest,
    ScrapedContent,
    ProcessedContent,
    StructureAnalysis,
    TextAnalysis,
    QualityMetrics,
    AnalysisReport,
    AnalysisResponse,
    AnalysisStatus,
    ContentType
)

# 1. Create request
request = URLAnalysisRequest(
    url="https://example.com/article",
    timeout=60,
    tags=["article", "tech"]
)

# 2. Scraped content
scraped = ScrapedContent(
    url=request.url,
    html_content="<html>...</html>",
    status_code=200
)

# 3. Processed content
processed = ProcessedContent(
    url=request.url,
    processed_text="Clean text...",
    word_count=150,
    content_type=ContentType.BLOG_POST,
    content_type_confidence=0.85
)

# 4. Analyses
structure = StructureAnalysis(
    total_headings=5,
    total_sections=3,
    hierarchy_depth=2
)

text = TextAnalysis(
    original_length=1000,
    processed_length=900,
    word_count=150,
    sentence_count=10,
    paragraph_count=3,
    character_count=900
)

metrics = QualityMetrics(
    overall_score=85.0,
    has_title=True,
    has_description=True
)

# 5. Create report
report = AnalysisReport(
    report_id="rpt-001",
    url=request.url,
    status=AnalysisStatus.COMPLETED,
    processed_content=processed,
    structure_analysis=structure,
    text_analysis=text,
    quality_metrics=metrics,
    total_processing_time_ms=2500.0
)

# 6. Create response
response = AnalysisResponse(
    success=True,
    data=report
)

# 7. Export
summary = report.to_summary()
json_export = serialize_report(report, format="json")
```

### Batch Processing
```python
from models.data_models import (
    BatchAnalysisRequest,
    BatchAnalysisResponse,
    AnalysisResponse
)

# Create batch request
batch_request = BatchAnalysisRequest(
    urls=[
        "https://example.com/1",
        "https://example.com/2",
        "https://example.com/3"
    ],
    max_workers=3
)

# Process and create batch response
batch_response = BatchAnalysisResponse(
    success=True,
    batch_id="batch-001",
    total_urls=3,
    successful=3,
    failed=0,
    results=[response1, response2, response3],
    processing_time_ms=7500.0
)
```

### Error Handling
```python
from models.data_models import AnalysisError, ErrorSeverity, AnalysisResponse

# Create error
error = AnalysisError(
    error_code="E001",
    error_type="ValidationError",
    message="Invalid URL format",
    severity=ErrorSeverity.ERROR,
    component="url_validator"
)

# Error response
response = AnalysisResponse(
    success=False,
    errors=[error],
    warnings=["Some data may be incomplete"]
)
```

---

## Validation Rules Summary

| Model | Key Validation Rules |
|-------|---------------------|
| URLAnalysisRequest | URL scheme check, timeout 1-300, retries 0-5, alphanumeric tags, max 20 tags |
| BatchAnalysisRequest | Unique URLs, 1-100 URLs, max_workers 1-10 |
| ScrapedContent | HTML length ≥10 chars, status 100-599, errors consistency |
| ProcessedContent | Text length ≥1, word count auto-correction, confidence 0-1 |
| QualityMetrics | All scores 0-100, max 50 issues/warnings |
| AnalysisReport | Status auto-correction on errors, time metrics ≥0 |

---

## Legacy Compatibility

For backward compatibility, legacy aliases are provided:
```python
# Legacy names (deprecated)
AnalysisRequest = URLAnalysisRequest
BatchRequest = BatchAnalysisRequest

# Use new names instead
from models.data_models import URLAnalysisRequest, BatchAnalysisRequest
```

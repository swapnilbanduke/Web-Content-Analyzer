"""
Pydantic Data Models for Web Content Analyzer
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
    ConfigDict
)
from pydantic.types import conint, constr, confloat
import re


# Enums
class ContentType(str, Enum):
    BLOG_POST = "blog_post"
    NEWS_ARTICLE = "news_article"
    TECHNICAL_DOCS = "technical_docs"
    ACADEMIC_PAPER = "academic_paper"
    PRODUCT_PAGE = "product_page"
    LANDING_PAGE = "landing_page"
    GENERAL = "general"


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class ErrorSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SectionType(str, Enum):
    INTRODUCTION = "introduction"
    METHODOLOGY = "methodology"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    REFERENCES = "references"
    APPENDIX = "appendix"
    BODY = "body"


# Validators
def validate_url_format(url: str) -> str:
    if not url:
        raise ValueError("URL cannot be empty")
    if not re.match(r"^https?://", url):
        raise ValueError("URL must start with http:// or https://")
    if not re.match(r"^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", url):
        raise ValueError("Invalid URL structure")
    return url


def validate_content_length(content: str, min_length: int = 10, max_length: int = 10_000_000) -> str:
    if not content:
        raise ValueError("Content cannot be empty")
    if len(content) < min_length:
        raise ValueError(f"Content too short (minimum {min_length} characters)")
    if len(content) > max_length:
        raise ValueError(f"Content too long (maximum {max_length} characters)")
    return content


# Request Models
class URLAnalysisRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")
    
    url: HttpUrl = Field(..., description="URL to analyze")
    user_agent: Optional[str] = Field(default=None, max_length=500)
    timeout: conint(ge=1, le=300) = Field(default=30)
    max_retries: conint(ge=0, le=5) = Field(default=3)
    follow_redirects: bool = Field(default=True)
    extract_metadata: bool = Field(default=True)
    extract_images: bool = Field(default=True)
    extract_links: bool = Field(default=True)
    analyze_structure: bool = Field(default=True)
    extract_key_phrases: bool = Field(default=True)
    classify_content: bool = Field(default=True)
    clean_html: bool = Field(default=True)
    normalize_text: bool = Field(default=True)
    detect_language: bool = Field(default=True)
    validate_ssl: bool = Field(default=True)
    max_content_size: conint(ge=1024, le=100_000_000) = Field(default=10_000_000)
    request_id: Optional[str] = Field(default=None, max_length=100)
    tags: List[str] = Field(default_factory=list, max_length=20)
    
    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        url_str = str(v)
        if "localhost" in url_str.lower() and not url_str.startswith("http://localhost"):
            raise ValueError("Localhost URLs must use http://")
        suspicious_patterns = ["javascript:", "data:", "file:", "ftp:"]
        if any(pattern in url_str.lower() for pattern in suspicious_patterns):
            raise ValueError(f"URL scheme not allowed")
        return v
    
    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        if len(v) > 20:
            raise ValueError("Maximum 20 tags allowed")
        for tag in v:
            if len(tag) > 50:
                raise ValueError("Tag length must be <= 50 characters")
            if not re.match(r"^[a-zA-Z0-9_-]+$", tag):
                raise ValueError("Tags must contain only alphanumeric characters, hyphens, and underscores")
        return v


class BatchAnalysisRequest(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    urls: List[HttpUrl] = Field(..., min_length=1, max_length=100)
    shared_config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    parallel_processing: bool = Field(default=True)
    max_workers: conint(ge=1, le=10) = Field(default=5)
    batch_id: Optional[str] = Field(default=None, max_length=100)
    
    @field_validator("urls")
    @classmethod
    def validate_unique_urls(cls, v):
        url_strings = [str(url) for url in v]
        if len(url_strings) != len(set(url_strings)):
            raise ValueError("URLs must be unique")
        return v


# Content Models
class ScrapedContent(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    
    url: HttpUrl = Field(...)
    html_content: str = Field(..., min_length=1)
    text_content: Optional[str] = Field(default=None)
    status_code: conint(ge=100, le=599) = Field(...)
    headers: Dict[str, str] = Field(default_factory=dict)
    content_type: Optional[str] = Field(default=None)
    content_length: Optional[int] = Field(default=None, ge=0)
    encoding: str = Field(default="utf-8")
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    scraper_version: str = Field(default="1.0.0")
    processing_time_ms: Optional[float] = Field(default=None, ge=0)
    redirect_chain: List[str] = Field(default_factory=list)
    is_valid_html: bool = Field(default=True)
    has_errors: bool = Field(default=False)
    errors: List[str] = Field(default_factory=list)
    
    @field_validator("html_content")
    @classmethod
    def validate_html_content(cls, v):
        return validate_content_length(v, min_length=10, max_length=10_000_000)
    
    @model_validator(mode="after")
    def validate_consistency(self):
        if self.has_errors and not self.errors:
            raise ValueError("has_errors is True but errors list is empty")
        if self.errors and not self.has_errors:
            self.has_errors = True
        return self


class Metadata(BaseModel):
    title: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    keywords: List[str] = Field(default_factory=list, max_length=50)
    author: Optional[str] = Field(default=None, max_length=200)
    published_date: Optional[datetime] = Field(default=None)
    modified_date: Optional[datetime] = Field(default=None)
    language: Optional[str] = Field(default=None, max_length=10)
    canonical_url: Optional[HttpUrl] = Field(default=None)
    og_title: Optional[str] = Field(default=None, max_length=500)
    og_description: Optional[str] = Field(default=None, max_length=2000)
    og_image: Optional[HttpUrl] = Field(default=None)
    og_type: Optional[str] = Field(default=None, max_length=50)
    twitter_card: Optional[str] = Field(default=None, max_length=50)
    twitter_title: Optional[str] = Field(default=None, max_length=500)
    twitter_description: Optional[str] = Field(default=None, max_length=2000)
    twitter_image: Optional[HttpUrl] = Field(default=None)
    robots: Optional[str] = Field(default=None, max_length=100)
    viewport: Optional[str] = Field(default=None, max_length=200)
    favicon: Optional[HttpUrl] = Field(default=None)


class Image(BaseModel):
    src: HttpUrl = Field(...)
    alt: Optional[str] = Field(default=None, max_length=500)
    title: Optional[str] = Field(default=None, max_length=500)
    width: Optional[int] = Field(default=None, ge=0)
    height: Optional[int] = Field(default=None, ge=0)
    file_size: Optional[int] = Field(default=None, ge=0)
    format: Optional[str] = Field(default=None, max_length=10)


class Link(BaseModel):
    href: HttpUrl = Field(...)
    text: Optional[str] = Field(default=None, max_length=500)
    title: Optional[str] = Field(default=None, max_length=500)
    rel: Optional[str] = Field(default=None, max_length=100)
    is_internal: bool = Field(default=False)
    is_external: bool = Field(default=False)


class Heading(BaseModel):
    level: conint(ge=1, le=6) = Field(...)
    text: str = Field(..., max_length=1000)
    id: Optional[str] = Field(default=None, max_length=200)
    position: int = Field(..., ge=0)


class Section(BaseModel):
    heading: Optional[Heading] = Field(default=None)
    content: str = Field(...)
    word_count: int = Field(..., ge=0)
    section_type: SectionType = Field(default=SectionType.BODY)
    start_position: int = Field(..., ge=0)
    end_position: int = Field(..., ge=0)


class ProcessedContent(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    
    url: HttpUrl = Field(...)
    original_content: Optional[str] = Field(default=None)
    processed_text: str = Field(..., min_length=0)  # Changed from min_length=1 to allow empty fallback
    metadata: Metadata = Field(default_factory=Metadata)
    headings: List[Heading] = Field(default_factory=list)
    sections: List[Section] = Field(default_factory=list)
    hierarchy_depth: int = Field(default=0, ge=0)
    content_type: ContentType = Field(default=ContentType.GENERAL)
    content_type_confidence: confloat(ge=0.0, le=1.0) = Field(default=0.0)
    images: List[Image] = Field(default_factory=list, max_length=1000)
    links: List[Link] = Field(default_factory=list, max_length=5000)
    word_count: int = Field(..., ge=0)
    sentence_count: int = Field(default=0, ge=0)
    paragraph_count: int = Field(default=0, ge=0)
    character_count: int = Field(default=0, ge=0)
    language: Optional[str] = Field(default=None, max_length=10)
    language_confidence: confloat(ge=0.0, le=1.0) = Field(default=0.0)
    readability_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    key_phrases: List[Dict[str, Any]] = Field(default_factory=list, max_length=100)
    keywords: List[str] = Field(default_factory=list, max_length=50)
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: Optional[float] = Field(default=None, ge=0)
    processor_version: str = Field(default="1.0.0")
    
    @model_validator(mode="after")
    def validate_processed_content(self):
        actual_word_count = len(self.processed_text.split())
        if abs(self.word_count - actual_word_count) > 10:
            self.word_count = actual_word_count
        return self


# Analysis Models
class StructureAnalysis(BaseModel):
    title: Optional[str] = Field(default=None, max_length=500)
    total_headings: int = Field(..., ge=0)
    total_sections: int = Field(..., ge=0)
    hierarchy_depth: int = Field(..., ge=0)
    heading_distribution: Dict[int, int] = Field(default_factory=dict)
    has_clear_structure: bool = Field(default=False)
    avg_section_length: float = Field(default=0.0, ge=0.0)
    table_of_contents: Optional[str] = Field(default=None)


class TextAnalysis(BaseModel):
    original_length: int = Field(..., ge=0)
    processed_length: int = Field(..., ge=0)
    word_count: int = Field(..., ge=0)
    sentence_count: int = Field(..., ge=0)
    paragraph_count: int = Field(..., ge=0)
    character_count: int = Field(..., ge=0)
    reading_time_minutes: float = Field(default=0.0, ge=0.0)
    readability_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    readability_level: Optional[str] = Field(default=None, max_length=50)
    detected_language: Optional[str] = Field(default=None, max_length=10)
    language_confidence: confloat(ge=0.0, le=1.0) = Field(default=0.0)
    steps_applied: List[str] = Field(default_factory=list)


class QualityMetrics(BaseModel):
    overall_score: confloat(ge=0.0, le=100.0) = Field(...)
    structure_score: confloat(ge=0.0, le=100.0) = Field(default=0.0)
    readability_score: confloat(ge=0.0, le=100.0) = Field(default=0.0)
    completeness_score: confloat(ge=0.0, le=100.0) = Field(default=0.0)
    metadata_score: confloat(ge=0.0, le=100.0) = Field(default=0.0)
    has_title: bool = Field(default=False)
    has_description: bool = Field(default=False)
    has_headings: bool = Field(default=False)
    has_images: bool = Field(default=False)
    has_proper_structure: bool = Field(default=False)
    issues: List[str] = Field(default_factory=list, max_length=50)
    warnings: List[str] = Field(default_factory=list, max_length=50)


class AnalysisReport(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    
    report_id: str = Field(...)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    analyzer_version: str = Field(default="1.0.0")
    url: HttpUrl = Field(...)
    request_id: Optional[str] = Field(default=None)
    status: AnalysisStatus = Field(default=AnalysisStatus.COMPLETED)
    scraped_content: Optional[ScrapedContent] = Field(default=None)
    processed_content: ProcessedContent = Field(...)
    structure_analysis: StructureAnalysis = Field(...)
    text_analysis: TextAnalysis = Field(...)
    quality_metrics: QualityMetrics = Field(...)
    recommendations: List[str] = Field(default_factory=list, max_length=20)
    total_processing_time_ms: float = Field(..., ge=0)
    scraping_time_ms: Optional[float] = Field(default=None, ge=0)
    processing_time_ms: Optional[float] = Field(default=None, ge=0)
    analysis_time_ms: Optional[float] = Field(default=None, ge=0)
    has_errors: bool = Field(default=False)
    has_warnings: bool = Field(default=False)
    errors: List[Dict[str, Any]] = Field(default_factory=list, max_length=50)
    warnings: List[Dict[str, Any]] = Field(default_factory=list, max_length=50)
    tags: List[str] = Field(default_factory=list, max_length=20)
    
    @model_validator(mode="after")
    def validate_report(self):
        if self.errors and self.status == AnalysisStatus.COMPLETED:
            self.status = AnalysisStatus.PARTIAL
        if self.has_errors and not self.errors:
            raise ValueError("has_errors is True but errors list is empty")
        return self
    
    def to_summary(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "url": str(self.url),
            "status": self.status.value,
            "generated_at": self.generated_at.isoformat(),
            "quality_score": self.quality_metrics.overall_score,
            "word_count": self.processed_content.word_count,
            "content_type": self.processed_content.content_type.value,
            "processing_time_ms": self.total_processing_time_ms,
            "has_errors": self.has_errors,
            "has_warnings": self.has_warnings
        }
    
    def to_json_export(self) -> Dict[str, Any]:
        return self.model_dump(mode="json", exclude_none=True)


# Error Models
class AnalysisError(BaseModel):
    error_code: str = Field(...)
    error_type: str = Field(...)
    message: str = Field(...)
    severity: ErrorSeverity = Field(default=ErrorSeverity.ERROR)
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    component: Optional[str] = Field(default=None)
    traceback: Optional[str] = Field(default=None)
    context: Dict[str, Any] = Field(default_factory=dict)


class ValidationError(BaseModel):
    field: str = Field(...)
    message: str = Field(...)
    invalid_value: Optional[Any] = Field(default=None)
    expected_type: Optional[str] = Field(default=None)
    constraint: Optional[str] = Field(default=None)


# Response Models
class AnalysisResponse(BaseModel):
    success: bool = Field(...)
    data: Optional[AnalysisReport] = Field(default=None)
    errors: List[AnalysisError] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BatchAnalysisResponse(BaseModel):
    success: bool = Field(...)
    batch_id: str = Field(...)
    total_urls: int = Field(..., ge=0)
    successful: int = Field(..., ge=0)
    failed: int = Field(..., ge=0)
    results: List[AnalysisResponse] = Field(default_factory=list)
    errors: List[AnalysisError] = Field(default_factory=list)
    processing_time_ms: float = Field(..., ge=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Health Check
class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Legacy aliases
AnalysisRequest = URLAnalysisRequest
BatchRequest = BatchAnalysisRequest


# Utilities
def serialize_report(report: AnalysisReport, format: str = "json") -> Union[str, Dict]:
    if format == "summary":
        return report.to_summary()
    elif format == "dict":
        return report.model_dump()
    elif format == "json":
        return report.model_dump_json(indent=2)
    else:
        raise ValueError(f"Unsupported format: {format}")

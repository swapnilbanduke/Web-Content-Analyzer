"""
Comprehensive Tests for Data Models

Tests all Pydantic models including:
- Request validation
- Content models
- Analysis models
- Error handling
- Serialization
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from pydantic import HttpUrl, ValidationError as PydanticValidationError

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from models.data_models import (
    # Enums
    ContentType, AnalysisStatus, ErrorSeverity, SectionType,
    
    # Request Models
    URLAnalysisRequest, BatchAnalysisRequest,
    
    # Content Models
    ScrapedContent, Metadata, Image, Link, Heading, Section, ProcessedContent,
    
    # Analysis Models
    StructureAnalysis, TextAnalysis, QualityMetrics, AnalysisReport,
    
    # Error Models
    AnalysisError, ValidationError,
    
    # Response Models
    AnalysisResponse, BatchAnalysisResponse,
    
    # Utilities
    validate_url_format, validate_content_length, serialize_report
)


# ============================================================================
# Test Enums
# ============================================================================

class TestEnums:
    """Test enum definitions"""
    
    def test_content_type_enum(self):
        """Test ContentType enum values"""
        assert ContentType.BLOG_POST == "blog_post"
        assert ContentType.NEWS_ARTICLE == "news_article"
        assert ContentType.TECHNICAL_DOCS == "technical_docs"
        assert len(ContentType) == 7
    
    def test_analysis_status_enum(self):
        """Test AnalysisStatus enum"""
        assert AnalysisStatus.PENDING == "pending"
        assert AnalysisStatus.COMPLETED == "completed"
        assert AnalysisStatus.FAILED == "failed"
    
    def test_error_severity_enum(self):
        """Test ErrorSeverity enum"""
        assert ErrorSeverity.INFO == "info"
        assert ErrorSeverity.ERROR == "error"
        assert ErrorSeverity.CRITICAL == "critical"
    
    def test_section_type_enum(self):
        """Test SectionType enum"""
        assert SectionType.INTRODUCTION == "introduction"
        assert SectionType.CONCLUSION == "conclusion"


# ============================================================================
# Test Custom Validators
# ============================================================================

class TestCustomValidators:
    """Test custom validation functions"""
    
    def test_validate_url_format_valid(self):
        """Test URL validation with valid URLs"""
        valid_urls = [
            "https://example.com",
            "http://example.com/path",
            "https://subdomain.example.com/path?query=value"
        ]
        
        for url in valid_urls:
            result = validate_url_format(url)
            assert result == url
    
    def test_validate_url_format_invalid(self):
        """Test URL validation with invalid URLs"""
        invalid_urls = [
            "",
            "example.com",  # Missing protocol
            "ftp://example.com",  # Wrong protocol
            "http://",  # Incomplete
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValueError):
                validate_url_format(url)
    
    def test_validate_content_length_valid(self):
        """Test content length validation"""
        content = "A" * 100
        result = validate_content_length(content, min_length=10, max_length=200)
        assert result == content
    
    def test_validate_content_length_too_short(self):
        """Test content too short"""
        with pytest.raises(ValueError, match="too short"):
            validate_content_length("ABC", min_length=10)
    
    def test_validate_content_length_too_long(self):
        """Test content too long"""
        with pytest.raises(ValueError, match="too long"):
            validate_content_length("A" * 1000, max_length=500)
    
    def test_validate_content_length_empty(self):
        """Test empty content"""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_content_length("")


# ============================================================================
# Test Request Models
# ============================================================================

class TestURLAnalysisRequest:
    """Test URLAnalysisRequest model"""
    
    def test_create_minimal_request(self):
        """Test creating request with minimal fields"""
        request = URLAnalysisRequest(url="https://example.com")
        
        assert str(request.url) == "https://example.com/"
        assert request.timeout == 30
        assert request.max_retries == 3
        assert request.follow_redirects is True
    
    def test_create_full_request(self):
        """Test creating request with all fields"""
        request = URLAnalysisRequest(
            url="https://example.com/article",
            user_agent="CustomBot/1.0",
            timeout=60,
            max_retries=5,
            follow_redirects=False,
            extract_metadata=True,
            tags=["test", "article"]
        )
        
        assert request.user_agent == "CustomBot/1.0"
        assert request.timeout == 60
        assert request.max_retries == 5
        assert request.follow_redirects is False
        assert len(request.tags) == 2
    
    def test_invalid_timeout(self):
        """Test timeout validation"""
        with pytest.raises(PydanticValidationError):
            URLAnalysisRequest(url="https://example.com", timeout=0)
        
        with pytest.raises(PydanticValidationError):
            URLAnalysisRequest(url="https://example.com", timeout=500)
    
    def test_invalid_retries(self):
        """Test max_retries validation"""
        with pytest.raises(PydanticValidationError):
            URLAnalysisRequest(url="https://example.com", max_retries=-1)
        
        with pytest.raises(PydanticValidationError):
            URLAnalysisRequest(url="https://example.com", max_retries=10)
    
    def test_invalid_url_scheme(self):
        """Test URL scheme validation"""
        with pytest.raises(PydanticValidationError):
            URLAnalysisRequest(url="javascript:alert('xss')")
        
        with pytest.raises(PydanticValidationError):
            URLAnalysisRequest(url="data:text/html,<script>alert('xss')</script>")
    
    def test_tag_validation(self):
        """Test tag validation"""
        # Valid tags
        request = URLAnalysisRequest(
            url="https://example.com",
            tags=["tag1", "tag-2", "tag_3"]
        )
        assert len(request.tags) == 3
        
        # Too many tags
        with pytest.raises(PydanticValidationError):
            URLAnalysisRequest(
                url="https://example.com",
                tags=[f"tag{i}" for i in range(25)]
            )
        
        # Invalid tag characters
        with pytest.raises(PydanticValidationError):
            URLAnalysisRequest(
                url="https://example.com",
                tags=["invalid tag with spaces"]
            )
    
    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden"""
        with pytest.raises(PydanticValidationError):
            URLAnalysisRequest(
                url="https://example.com",
                unknown_field="value"
            )


class TestBatchAnalysisRequest:
    """Test BatchAnalysisRequest model"""
    
    def test_create_batch_request(self):
        """Test creating batch request"""
        urls = [
            "https://example.com/1",
            "https://example.com/2",
            "https://example.com/3"
        ]
        
        request = BatchAnalysisRequest(urls=urls)
        
        assert len(request.urls) == 3
        assert request.parallel_processing is True
        assert request.max_workers == 5
    
    def test_unique_urls_validation(self):
        """Test unique URL validation"""
        with pytest.raises(PydanticValidationError, match="URLs must be unique"):
            BatchAnalysisRequest(urls=[
                "https://example.com",
                "https://example.com"
            ])
    
    def test_batch_size_limits(self):
        """Test batch size validation"""
        # Too few URLs
        with pytest.raises(PydanticValidationError):
            BatchAnalysisRequest(urls=[])
        
        # Too many URLs
        with pytest.raises(PydanticValidationError):
            BatchAnalysisRequest(urls=[
                f"https://example.com/{i}" for i in range(101)
            ])
    
    def test_max_workers_validation(self):
        """Test max_workers validation"""
        # Valid
        request = BatchAnalysisRequest(
            urls=["https://example.com"],
            max_workers=3
        )
        assert request.max_workers == 3
        
        # Invalid - too low
        with pytest.raises(PydanticValidationError):
            BatchAnalysisRequest(
                urls=["https://example.com"],
                max_workers=0
            )
        
        # Invalid - too high
        with pytest.raises(PydanticValidationError):
            BatchAnalysisRequest(
                urls=["https://example.com"],
                max_workers=15
            )


# ============================================================================
# Test Content Models
# ============================================================================

class TestScrapedContent:
    """Test ScrapedContent model"""
    
    def test_create_scraped_content(self):
        """Test creating scraped content"""
        content = ScrapedContent(
            url="https://example.com",
            html_content="<html><body>Test</body></html>",
            status_code=200
        )
        
        assert str(content.url) == "https://example.com/"
        assert content.status_code == 200
        assert content.is_valid_html is True
        assert content.has_errors is False
    
    def test_scraped_content_with_errors(self):
        """Test scraped content with errors"""
        content = ScrapedContent(
            url="https://example.com",
            html_content="<html><body>Test</body></html>",
            status_code=200,
            has_errors=True,
            errors=["Error 1", "Error 2"]
        )
        
        assert content.has_errors is True
        assert len(content.errors) == 2
    
    def test_consistency_validation(self):
        """Test consistency validation"""
        # has_errors True but no errors - should fail
        with pytest.raises(PydanticValidationError):
            ScrapedContent(
                url="https://example.com",
                html_content="<html><body>Test</body></html>",
                status_code=200,
                has_errors=True,
                errors=[]
            )
    
    def test_auto_correct_errors_flag(self):
        """Test automatic correction of has_errors flag"""
        content = ScrapedContent(
            url="https://example.com",
            html_content="<html><body>Test</body></html>",
            status_code=200,
            has_errors=False,
            errors=["Error occurred"]
        )
        
        # Should auto-correct has_errors to True
        assert content.has_errors is True
    
    def test_html_content_validation(self):
        """Test HTML content length validation"""
        # Too short
        with pytest.raises(PydanticValidationError):
            ScrapedContent(
                url="https://example.com",
                html_content="ABC",
                status_code=200
            )
    
    def test_status_code_validation(self):
        """Test status code validation"""
        # Valid status codes
        for code in [200, 301, 404, 500]:
            content = ScrapedContent(
                url="https://example.com",
                html_content="<html><body>Test content</body></html>",
                status_code=code
            )
            assert content.status_code == code
        
        # Invalid status codes
        with pytest.raises(PydanticValidationError):
            ScrapedContent(
                url="https://example.com",
                html_content="<html><body>Test content</body></html>",
                status_code=99
            )


class TestMetadata:
    """Test Metadata model"""
    
    def test_create_metadata(self):
        """Test creating metadata"""
        metadata = Metadata(
            title="Test Article",
            description="Test description",
            keywords=["test", "article"],
            author="John Doe"
        )
        
        assert metadata.title == "Test Article"
        assert len(metadata.keywords) == 2
        assert metadata.author == "John Doe"
    
    def test_metadata_with_og_data(self):
        """Test metadata with Open Graph data"""
        metadata = Metadata(
            title="Test",
            og_title="OG Title",
            og_description="OG Description",
            og_image="https://example.com/image.jpg"
        )
        
        assert metadata.og_title == "OG Title"
        assert str(metadata.og_image) == "https://example.com/image.jpg"


class TestProcessedContent:
    """Test ProcessedContent model"""
    
    def test_create_processed_content(self):
        """Test creating processed content"""
        content = ProcessedContent(
            url="https://example.com",
            processed_text="This is processed text content with multiple words.",
            word_count=8
        )
        
        assert content.word_count == 8
        assert content.content_type == ContentType.GENERAL
    
    def test_word_count_auto_correction(self):
        """Test automatic word count correction"""
        content = ProcessedContent(
            url="https://example.com",
            processed_text="One two three four five",
            word_count=999  # Wrong count
        )
        
        # Should auto-correct to actual count
        assert content.word_count == 5
    
    def test_content_classification(self):
        """Test content classification"""
        content = ProcessedContent(
            url="https://example.com",
            processed_text="Test content",
            word_count=2,
            content_type=ContentType.BLOG_POST,
            content_type_confidence=0.85
        )
        
        assert content.content_type == ContentType.BLOG_POST
        assert content.content_type_confidence == 0.85


# ============================================================================
# Test Analysis Models
# ============================================================================

class TestQualityMetrics:
    """Test QualityMetrics model"""
    
    def test_create_quality_metrics(self):
        """Test creating quality metrics"""
        metrics = QualityMetrics(
            overall_score=75.5,
            structure_score=80.0,
            readability_score=70.0,
            completeness_score=75.0,
            metadata_score=80.0
        )
        
        assert metrics.overall_score == 75.5
        assert metrics.structure_score == 80.0
    
    def test_score_validation(self):
        """Test score range validation"""
        # Valid scores
        metrics = QualityMetrics(overall_score=50.0)
        assert metrics.overall_score == 50.0
        
        # Invalid - too low
        with pytest.raises(PydanticValidationError):
            QualityMetrics(overall_score=-1.0)
        
        # Invalid - too high
        with pytest.raises(PydanticValidationError):
            QualityMetrics(overall_score=101.0)
    
    def test_quality_indicators(self):
        """Test quality indicators"""
        metrics = QualityMetrics(
            overall_score=80.0,
            has_title=True,
            has_description=True,
            has_headings=True,
            has_proper_structure=True,
            issues=["Minor formatting issue"],
            warnings=["Consider adding more images"]
        )
        
        assert metrics.has_title is True
        assert len(metrics.issues) == 1
        assert len(metrics.warnings) == 1


class TestAnalysisReport:
    """Test AnalysisReport model"""
    
    @pytest.fixture
    def sample_processed_content(self):
        """Create sample processed content"""
        return ProcessedContent(
            url="https://example.com",
            processed_text="Test content",
            word_count=2
        )
    
    @pytest.fixture
    def sample_structure_analysis(self):
        """Create sample structure analysis"""
        return StructureAnalysis(
            total_headings=5,
            total_sections=3,
            hierarchy_depth=2
        )
    
    @pytest.fixture
    def sample_text_analysis(self):
        """Create sample text analysis"""
        return TextAnalysis(
            original_length=1000,
            processed_length=900,
            word_count=150,
            sentence_count=10,
            paragraph_count=3,
            character_count=900
        )
    
    @pytest.fixture
    def sample_quality_metrics(self):
        """Create sample quality metrics"""
        return QualityMetrics(overall_score=75.0)
    
    def test_create_analysis_report(
        self,
        sample_processed_content,
        sample_structure_analysis,
        sample_text_analysis,
        sample_quality_metrics
    ):
        """Test creating analysis report"""
        report = AnalysisReport(
            report_id="test-123",
            url="https://example.com",
            processed_content=sample_processed_content,
            structure_analysis=sample_structure_analysis,
            text_analysis=sample_text_analysis,
            quality_metrics=sample_quality_metrics,
            total_processing_time_ms=1500.0
        )
        
        assert report.report_id == "test-123"
        assert report.status == AnalysisStatus.COMPLETED
        assert report.total_processing_time_ms == 1500.0
    
    def test_report_to_summary(
        self,
        sample_processed_content,
        sample_structure_analysis,
        sample_text_analysis,
        sample_quality_metrics
    ):
        """Test report summary generation"""
        report = AnalysisReport(
            report_id="test-123",
            url="https://example.com",
            processed_content=sample_processed_content,
            structure_analysis=sample_structure_analysis,
            text_analysis=sample_text_analysis,
            quality_metrics=sample_quality_metrics,
            total_processing_time_ms=1500.0
        )
        
        summary = report.to_summary()
        
        assert summary['report_id'] == "test-123"
        assert summary['quality_score'] == 75.0
        assert summary['word_count'] == 2
        assert summary['status'] == "completed"
    
    def test_report_status_auto_correction(
        self,
        sample_processed_content,
        sample_structure_analysis,
        sample_text_analysis,
        sample_quality_metrics
    ):
        """Test automatic status correction when errors exist"""
        report = AnalysisReport(
            report_id="test-123",
            url="https://example.com",
            processed_content=sample_processed_content,
            structure_analysis=sample_structure_analysis,
            text_analysis=sample_text_analysis,
            quality_metrics=sample_quality_metrics,
            total_processing_time_ms=1500.0,
            status=AnalysisStatus.COMPLETED,
            errors=[{"code": "E001", "message": "Test error"}]
        )
        
        # Status should be auto-corrected to PARTIAL
        assert report.status == AnalysisStatus.PARTIAL
    
    def test_report_serialization(
        self,
        sample_processed_content,
        sample_structure_analysis,
        sample_text_analysis,
        sample_quality_metrics
    ):
        """Test report JSON export"""
        report = AnalysisReport(
            report_id="test-123",
            url="https://example.com",
            processed_content=sample_processed_content,
            structure_analysis=sample_structure_analysis,
            text_analysis=sample_text_analysis,
            quality_metrics=sample_quality_metrics,
            total_processing_time_ms=1500.0
        )
        
        json_data = report.to_json_export()
        
        assert isinstance(json_data, dict)
        assert json_data['report_id'] == "test-123"


# ============================================================================
# Test Error Models
# ============================================================================

class TestAnalysisError:
    """Test AnalysisError model"""
    
    def test_create_error(self):
        """Test creating analysis error"""
        error = AnalysisError(
            error_code="E001",
            error_type="ValidationError",
            message="Test error message",
            severity=ErrorSeverity.ERROR
        )
        
        assert error.error_code == "E001"
        assert error.severity == ErrorSeverity.ERROR
        assert isinstance(error.occurred_at, datetime)
    
    def test_error_with_context(self):
        """Test error with context"""
        error = AnalysisError(
            error_code="E002",
            error_type="ProcessingError",
            message="Failed to process",
            component="text_processor",
            context={"step": "normalization", "reason": "invalid_input"}
        )
        
        assert error.component == "text_processor"
        assert error.context['step'] == "normalization"


class TestValidationError:
    """Test ValidationError model"""
    
    def test_create_validation_error(self):
        """Test creating validation error"""
        error = ValidationError(
            field="url",
            message="Invalid URL format",
            invalid_value="not-a-url",
            expected_type="HttpUrl"
        )
        
        assert error.field == "url"
        assert error.message == "Invalid URL format"


# ============================================================================
# Test Response Models
# ============================================================================

class TestAnalysisResponse:
    """Test AnalysisResponse model"""
    
    def test_create_success_response(self):
        """Test creating success response"""
        response = AnalysisResponse(
            success=True,
            data=None
        )
        
        assert response.success is True
        assert len(response.errors) == 0
    
    def test_create_error_response(self):
        """Test creating error response"""
        error = AnalysisError(
            error_code="E001",
            error_type="ValidationError",
            message="Test error"
        )
        
        response = AnalysisResponse(
            success=False,
            errors=[error]
        )
        
        assert response.success is False
        assert len(response.errors) == 1


class TestBatchAnalysisResponse:
    """Test BatchAnalysisResponse model"""
    
    def test_create_batch_response(self):
        """Test creating batch response"""
        response = BatchAnalysisResponse(
            success=True,
            batch_id="batch-123",
            total_urls=10,
            successful=8,
            failed=2,
            processing_time_ms=5000.0
        )
        
        assert response.total_urls == 10
        assert response.successful == 8
        assert response.failed == 2


# ============================================================================
# Test Serialization
# ============================================================================

class TestSerialization:
    """Test serialization functions"""
    
    @pytest.fixture
    def sample_report(self):
        """Create sample report for testing"""
        return AnalysisReport(
            report_id="test-123",
            url="https://example.com",
            processed_content=ProcessedContent(
                url="https://example.com",
                processed_text="Test",
                word_count=1
            ),
            structure_analysis=StructureAnalysis(
                total_headings=0,
                total_sections=0,
                hierarchy_depth=0
            ),
            text_analysis=TextAnalysis(
                original_length=100,
                processed_length=90,
                word_count=1,
                sentence_count=1,
                paragraph_count=1,
                character_count=4
            ),
            quality_metrics=QualityMetrics(overall_score=50.0),
            total_processing_time_ms=1000.0
        )
    
    def test_serialize_report_json(self, sample_report):
        """Test JSON serialization"""
        result = serialize_report(sample_report, format="json")
        assert isinstance(result, str)
        assert "test-123" in result
    
    def test_serialize_report_dict(self, sample_report):
        """Test dict serialization"""
        result = serialize_report(sample_report, format="dict")
        assert isinstance(result, dict)
        assert result['report_id'] == "test-123"
    
    def test_serialize_report_summary(self, sample_report):
        """Test summary serialization"""
        result = serialize_report(sample_report, format="summary")
        assert isinstance(result, dict)
        assert 'report_id' in result
        assert 'quality_score' in result
    
    def test_serialize_invalid_format(self, sample_report):
        """Test invalid format"""
        with pytest.raises(ValueError, match="Unsupported format"):
            serialize_report(sample_report, format="invalid")


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for model interactions"""
    
    def test_full_analysis_workflow(self):
        """Test complete analysis workflow"""
        # 1. Create request
        request = URLAnalysisRequest(
            url="https://example.com/article",
            timeout=60,
            tags=["test", "integration"]
        )
        
        # 2. Create scraped content
        scraped = ScrapedContent(
            url=request.url,
            html_content="<html><body><h1>Test</h1><p>Content</p></body></html>",
            status_code=200
        )
        
        # 3. Create processed content
        processed = ProcessedContent(
            url=request.url,
            processed_text="Test Content",
            word_count=2,
            metadata=Metadata(title="Test Article")
        )
        
        # 4. Create analyses
        structure = StructureAnalysis(
            total_headings=1,
            total_sections=1,
            hierarchy_depth=1
        )
        
        text = TextAnalysis(
            original_length=100,
            processed_length=90,
            word_count=2,
            sentence_count=1,
            paragraph_count=1,
            character_count=12
        )
        
        quality = QualityMetrics(
            overall_score=80.0,
            has_title=True
        )
        
        # 5. Create report
        report = AnalysisReport(
            report_id="test-integration",
            url=request.url,
            scraped_content=scraped,
            processed_content=processed,
            structure_analysis=structure,
            text_analysis=text,
            quality_metrics=quality,
            total_processing_time_ms=2000.0
        )
        
        # 6. Create response
        response = AnalysisResponse(
            success=True,
            data=report
        )
        
        # Assertions
        assert response.success is True
        assert response.data.report_id == "test-integration"
        assert response.data.quality_metrics.overall_score == 80.0
    
    def test_batch_workflow(self):
        """Test batch analysis workflow"""
        # Create batch request
        batch_request = BatchAnalysisRequest(
            urls=[
                "https://example.com/1",
                "https://example.com/2",
                "https://example.com/3"
            ],
            max_workers=3
        )
        
        # Create individual responses
        responses = []
        for i, url in enumerate(batch_request.urls):
            report = AnalysisReport(
                report_id=f"batch-{i}",
                url=url,
                processed_content=ProcessedContent(
                    url=url,
                    processed_text="Test",
                    word_count=1
                ),
                structure_analysis=StructureAnalysis(
                    total_headings=0,
                    total_sections=0,
                    hierarchy_depth=0
                ),
                text_analysis=TextAnalysis(
                    original_length=10,
                    processed_length=10,
                    word_count=1,
                    sentence_count=1,
                    paragraph_count=1,
                    character_count=4
                ),
                quality_metrics=QualityMetrics(overall_score=70.0),
                total_processing_time_ms=1000.0
            )
            
            responses.append(AnalysisResponse(success=True, data=report))
        
        # Create batch response
        batch_response = BatchAnalysisResponse(
            success=True,
            batch_id="batch-123",
            total_urls=3,
            successful=3,
            failed=0,
            results=responses,
            processing_time_ms=3000.0
        )
        
        # Assertions
        assert batch_response.total_urls == 3
        assert batch_response.successful == 3
        assert len(batch_response.results) == 3

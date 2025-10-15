"""
Comprehensive Security Tests

Tests for:
- URL validation and SSRF prevention
- Content size validation
- File type validation
- XSS prevention and HTML sanitization
- Malicious content detection
- Integration scenarios
"""

import pytest
from typing import Dict, Any
from backend.src.utils.security import (
    URLValidator,
    ContentSizeValidator,
    FileTypeValidator,
    ContentSanitizer,
    MaliciousContentDetector,
    ContentFilter,
    sanitize_url,
    sanitize_html,
    is_safe_url,
    validate_content_length,
    remove_sensitive_data,
    create_secure_validator,
    validate_request,
    sanitize_and_validate_content,
)


# ============================================================================
# URL Validation and SSRF Prevention Tests
# ============================================================================

class TestURLValidator:
    """Test URL validation and SSRF prevention"""
    
    def test_valid_http_url(self):
        """Test valid HTTP URL"""
        validator = URLValidator()
        is_valid, error = validator.validate_url("http://example.com", raise_exception=False)
        assert is_valid is True
        assert error is None
    
    def test_valid_https_url(self):
        """Test valid HTTPS URL"""
        validator = URLValidator()
        is_valid, error = validator.validate_url("https://example.com", raise_exception=False)
        assert is_valid is True
        assert error is None
    
    def test_dangerous_protocol_javascript(self):
        """Test blocking javascript: protocol"""
        validator = URLValidator()
        is_valid, error = validator.validate_url("javascript:alert(1)", raise_exception=False)
        assert is_valid is False
        assert "Dangerous protocol" in error
    
    def test_dangerous_protocol_data(self):
        """Test blocking data: protocol"""
        validator = URLValidator()
        is_valid, error = validator.validate_url("data:text/html,<script>alert(1)</script>", raise_exception=False)
        assert is_valid is False
        assert "Dangerous protocol" in error
    
    def test_dangerous_protocol_file(self):
        """Test blocking file: protocol"""
        validator = URLValidator()
        is_valid, error = validator.validate_url("file:///etc/passwd", raise_exception=False)
        assert is_valid is False
        assert "Dangerous protocol" in error
    
    def test_block_localhost(self):
        """Test blocking localhost"""
        validator = URLValidator()
        is_valid, error = validator.validate_url("http://localhost:8080", raise_exception=False)
        assert is_valid is False
        assert "Localhost access is blocked" in error
    
    def test_block_127_0_0_1(self):
        """Test blocking 127.0.0.1"""
        validator = URLValidator()
        is_valid, error = validator.validate_url("http://127.0.0.1:8080", raise_exception=False)
        assert is_valid is False
        assert "Private IP range" in error or "Localhost" in error
    
    def test_block_ipv6_localhost(self):
        """Test blocking ::1"""
        validator = URLValidator()
        is_valid, error = validator.validate_url("http://[::1]:8080", raise_exception=False)
        assert is_valid is False
        assert "Private IP range" in error or "Localhost" in error
    
    def test_block_private_ip_10(self):
        """Test blocking 10.x.x.x"""
        validator = URLValidator()
        is_valid, error = validator.validate_url("http://10.0.0.1", raise_exception=False)
        assert is_valid is False
        assert "Private IP range" in error
    
    def test_block_private_ip_192(self):
        """Test blocking 192.168.x.x"""
        validator = URLValidator()
        is_valid, error = validator.validate_url("http://192.168.1.1", raise_exception=False)
        assert is_valid is False
        assert "Private IP range" in error
    
    def test_block_private_ip_172(self):
        """Test blocking 172.16-31.x.x"""
        validator = URLValidator()
        is_valid, error = validator.validate_url("http://172.16.0.1", raise_exception=False)
        assert is_valid is False
        assert "Private IP range" in error
    
    def test_block_link_local(self):
        """Test blocking 169.254.x.x"""
        validator = URLValidator()
        is_valid, error = validator.validate_url("http://169.254.169.254", raise_exception=False)
        assert is_valid is False
        assert "Private IP range" in error
    
    def test_suspicious_pattern_at_sign(self):
        """Test detecting @ in URL (credentials)"""
        validator = URLValidator()
        is_valid, error = validator.validate_url("http://user:pass@example.com", raise_exception=False)
        assert is_valid is False
        assert "Suspicious pattern" in error
    
    def test_suspicious_pattern_directory_traversal(self):
        """Test detecting ../ in URL"""
        validator = URLValidator()
        is_valid, error = validator.validate_url("http://example.com/../etc/passwd", raise_exception=False)
        assert is_valid is False
        assert "Suspicious pattern" in error
    
    def test_suspicious_pattern_null_byte(self):
        """Test detecting null byte"""
        validator = URLValidator()
        is_valid, error = validator.validate_url("http://example.com/file%00.jpg", raise_exception=False)
        assert is_valid is False
        assert "Suspicious pattern" in error
    
    def test_url_too_long(self):
        """Test URL length limit"""
        validator = URLValidator()
        long_url = "http://example.com/" + "a" * 3000
        is_valid, error = validator.validate_url(long_url, raise_exception=False)
        assert is_valid is False
        assert "maximum length" in error
    
    def test_empty_url(self):
        """Test empty URL"""
        validator = URLValidator()
        is_valid, error = validator.validate_url("", raise_exception=False)
        assert is_valid is False
        assert "non-empty string" in error
    
    def test_domain_whitelist(self):
        """Test domain whitelist"""
        validator = URLValidator(allowed_domains={"example.com", "test.com"})
        
        # Allowed domain
        is_valid, _ = validator.validate_url("http://example.com", raise_exception=False)
        assert is_valid is True
        
        # Not allowed domain
        is_valid, error = validator.validate_url("http://other.com", raise_exception=False)
        assert is_valid is False
        assert "not in whitelist" in error
    
    def test_domain_blacklist(self):
        """Test domain blacklist"""
        validator = URLValidator(blocked_domains={"malicious.com", "spam.com"})
        
        # Blocked domain
        is_valid, error = validator.validate_url("http://malicious.com", raise_exception=False)
        assert is_valid is False
        assert "is blocked" in error
        
        # Allowed domain
        is_valid, _ = validator.validate_url("http://example.com", raise_exception=False)
        assert is_valid is True
    
    def test_raise_exception_mode(self):
        """Test exception raising mode"""
        validator = URLValidator()
        
        with pytest.raises(ValueError) as exc_info:
            validator.validate_url("javascript:alert(1)", raise_exception=True)
        
        assert "Dangerous protocol" in str(exc_info.value)


# ============================================================================
# Content Size Validation Tests
# ============================================================================

class TestContentSizeValidator:
    """Test content size validation"""
    
    def test_valid_content_size(self):
        """Test valid content size"""
        validator = ContentSizeValidator(max_size=1000)
        is_valid, error = validator.validate_size(500, raise_exception=False)
        assert is_valid is True
        assert error is None
    
    def test_content_too_large(self):
        """Test content exceeding max size"""
        validator = ContentSizeValidator(max_size=1000)
        is_valid, error = validator.validate_size(2000, raise_exception=False)
        assert is_valid is False
        assert "exceeds maximum" in error
    
    def test_content_at_limit(self):
        """Test content at exact limit"""
        validator = ContentSizeValidator(max_size=1000)
        is_valid, error = validator.validate_size(1000, raise_exception=False)
        assert is_valid is True
    
    def test_warning_threshold(self):
        """Test warning threshold"""
        validator = ContentSizeValidator(max_size=1000, warning_size=500)
        # Should pass but log warning
        is_valid, error = validator.validate_size(750, raise_exception=False)
        assert is_valid is True
    
    def test_validate_actual_content(self):
        """Test validating actual string content"""
        validator = ContentSizeValidator(max_size=100)
        
        # Small content
        is_valid, _ = validator.validate_content("Hello World", raise_exception=False)
        assert is_valid is True
        
        # Large content
        large_content = "x" * 200
        is_valid, error = validator.validate_content(large_content, raise_exception=False)
        assert is_valid is False
    
    def test_unicode_content_size(self):
        """Test Unicode content size calculation"""
        validator = ContentSizeValidator(max_size=100)
        
        # Unicode characters can be multiple bytes
        unicode_content = "你好世界" * 20  # Chinese characters
        is_valid, _ = validator.validate_content(unicode_content, raise_exception=False)
        # Should fail because Unicode chars are multiple bytes
        assert is_valid is False
    
    def test_none_content_length(self):
        """Test None content length"""
        validator = ContentSizeValidator()
        is_valid, error = validator.validate_size(None, raise_exception=False)
        assert is_valid is True  # Should allow unknown size with warning
    
    def test_raise_exception_mode(self):
        """Test exception raising mode"""
        validator = ContentSizeValidator(max_size=100)
        
        with pytest.raises(ValueError) as exc_info:
            validator.validate_size(200, raise_exception=True)
        
        assert "exceeds maximum" in str(exc_info.value)


# ============================================================================
# File Type Validation Tests
# ============================================================================

class TestFileTypeValidator:
    """Test file type validation"""
    
    def test_valid_html_mime(self):
        """Test valid text/html MIME type"""
        validator = FileTypeValidator()
        is_valid, error = validator.validate_mime_type("text/html", raise_exception=False)
        assert is_valid is True
    
    def test_valid_xml_mime(self):
        """Test valid application/xml MIME type"""
        validator = FileTypeValidator()
        is_valid, error = validator.validate_mime_type("application/xml", raise_exception=False)
        assert is_valid is True
    
    def test_html_with_charset(self):
        """Test HTML with charset parameter"""
        validator = FileTypeValidator()
        is_valid, error = validator.validate_mime_type("text/html; charset=utf-8", raise_exception=False)
        assert is_valid is True
    
    def test_invalid_mime_type(self):
        """Test invalid MIME type"""
        validator = FileTypeValidator()
        is_valid, error = validator.validate_mime_type("application/pdf", raise_exception=False)
        assert is_valid is False
        assert "not allowed" in error
    
    def test_executable_mime_blocked(self):
        """Test blocking executable MIME types"""
        validator = FileTypeValidator()
        is_valid, error = validator.validate_mime_type("application/x-msdownload", raise_exception=False)
        assert is_valid is False
    
    def test_valid_extension_html(self):
        """Test valid .html extension"""
        validator = FileTypeValidator()
        is_valid, error = validator.validate_extension("http://example.com/page.html", raise_exception=False)
        assert is_valid is True
    
    def test_valid_extension_xml(self):
        """Test valid .xml extension"""
        validator = FileTypeValidator()
        is_valid, error = validator.validate_extension("http://example.com/data.xml", raise_exception=False)
        assert is_valid is True
    
    def test_invalid_extension(self):
        """Test invalid extension"""
        validator = FileTypeValidator()
        is_valid, error = validator.validate_extension("http://example.com/file.exe", raise_exception=False)
        assert is_valid is False
        assert "not allowed" in error
    
    def test_no_extension(self):
        """Test URL without extension"""
        validator = FileTypeValidator()
        is_valid, error = validator.validate_extension("http://example.com/page", raise_exception=False)
        assert is_valid is True  # Should allow
    
    def test_detect_html_content_type(self):
        """Test detecting HTML from magic numbers"""
        validator = FileTypeValidator()
        html_content = b"<!DOCTYPE html><html><body>Test</body></html>"
        content_type = validator.detect_content_type(html_content)
        assert content_type == "html"
    
    def test_detect_xml_content_type(self):
        """Test detecting XML from magic numbers"""
        validator = FileTypeValidator()
        xml_content = b"<?xml version='1.0'?><root></root>"
        content_type = validator.detect_content_type(xml_content)
        assert content_type == "xml"
    
    def test_custom_allowed_types(self):
        """Test custom allowed MIME types"""
        validator = FileTypeValidator(allowed_mime_types={"application/json"})
        
        is_valid, _ = validator.validate_mime_type("application/json", raise_exception=False)
        assert is_valid is True
        
        is_valid, _ = validator.validate_mime_type("text/html", raise_exception=False)
        assert is_valid is False


# ============================================================================
# XSS Prevention and Content Sanitization Tests
# ============================================================================

class TestContentSanitizer:
    """Test XSS prevention and content sanitization"""
    
    def test_strict_mode_escapes_all_html(self):
        """Test strict mode escapes all HTML"""
        sanitizer = ContentSanitizer(strict_mode=True)
        content = "<script>alert('xss')</script>"
        sanitized = sanitizer.sanitize_html(content)
        assert "&lt;script&gt;" in sanitized
        assert "<script>" not in sanitized
    
    def test_strict_mode_escapes_entities(self):
        """Test strict mode escapes HTML entities"""
        sanitizer = ContentSanitizer(strict_mode=True)
        content = "<div>Test & 'quotes' \"double\"</div>"
        sanitized = sanitizer.sanitize_html(content)
        assert "&lt;" in sanitized
        assert "&gt;" in sanitized
        assert "&amp;" in sanitized
    
    def test_remove_script_tags(self):
        """Test removing script tags"""
        sanitizer = ContentSanitizer(strict_mode=False)
        content = "<div>Hello <script>alert('xss')</script> World</div>"
        sanitized = sanitizer.sanitize_html(content)
        assert "<script>" not in sanitized.lower()
        assert "alert" not in sanitized.lower()
    
    def test_remove_iframe_tags(self):
        """Test removing iframe tags"""
        sanitizer = ContentSanitizer(strict_mode=False)
        content = "<div>Content <iframe src='evil.com'></iframe></div>"
        sanitized = sanitizer.sanitize_html(content)
        assert "<iframe" not in sanitized.lower()
    
    def test_remove_event_handlers(self):
        """Test removing event handlers"""
        sanitizer = ContentSanitizer(strict_mode=False)
        content = "<img src='x' onerror='alert(1)' />"
        sanitized = sanitizer.sanitize_html(content)
        assert "onerror" not in sanitized.lower()
    
    def test_remove_javascript_urls(self):
        """Test removing javascript: URLs"""
        sanitizer = ContentSanitizer(strict_mode=False)
        content = "<a href='javascript:alert(1)'>Click</a>"
        sanitized = sanitizer.sanitize_html(content)
        assert "javascript:" not in sanitized.lower()
    
    def test_remove_data_urls(self):
        """Test removing data: URLs"""
        sanitizer = ContentSanitizer(strict_mode=False)
        content = "<img src='data:image/svg+xml,<svg>...</svg>' />"
        sanitized = sanitizer.sanitize_html(content)
        assert "data:" not in sanitized.lower()
    
    def test_sanitize_plain_text(self):
        """Test sanitizing plain text"""
        sanitizer = ContentSanitizer()
        text = "<script>alert('xss')</script>"
        sanitized = sanitizer.sanitize_text(text)
        assert "&lt;" in sanitized
        assert "<" not in sanitized
    
    def test_strip_dangerous_content(self):
        """Test aggressively stripping dangerous content"""
        sanitizer = ContentSanitizer()
        content = """
        <div>
            <script>alert('xss')</script>
            <style>body { display: none; }</style>
            <iframe src="evil.com"></iframe>
            <img src="x" onerror="alert(1)" />
            <a href="javascript:void(0)">Link</a>
        </div>
        """
        sanitized = sanitizer.strip_dangerous_content(content)
        
        assert "<script" not in sanitized.lower()
        assert "<style" not in sanitized.lower()
        assert "<iframe" not in sanitized.lower()
        assert "onerror" not in sanitized.lower()
        assert "javascript:" not in sanitized.lower()
    
    def test_multiple_script_tags(self):
        """Test removing multiple script tags"""
        sanitizer = ContentSanitizer(strict_mode=False)
        content = "<script>bad1()</script><div>Good</div><script>bad2()</script>"
        sanitized = sanitizer.sanitize_html(content)
        assert "bad1" not in sanitized.lower()
        assert "bad2" not in sanitized.lower()


# ============================================================================
# Malicious Content Detection Tests
# ============================================================================

class TestMaliciousContentDetector:
    """Test malicious content detection"""
    
    def test_detect_sql_injection_select(self):
        """Test detecting SQL SELECT injection"""
        detector = MaliciousContentDetector()
        content = "SELECT * FROM users WHERE id=1"
        detected = detector.detect_malicious_patterns(content, check_types=['sql'])
        assert 'sql' in detected
    
    def test_detect_sql_injection_union(self):
        """Test detecting UNION SELECT injection"""
        detector = MaliciousContentDetector()
        content = "1' UNION SELECT password FROM users--"
        detected = detector.detect_malicious_patterns(content, check_types=['sql'])
        assert 'sql' in detected
    
    def test_detect_sql_injection_or(self):
        """Test detecting OR injection"""
        detector = MaliciousContentDetector()
        content = "' OR 1=1--"
        detected = detector.detect_malicious_patterns(content, check_types=['sql'])
        assert 'sql' in detected
    
    def test_detect_xss_script_tag(self):
        """Test detecting XSS script tag"""
        detector = MaliciousContentDetector()
        content = "<script>alert('xss')</script>"
        detected = detector.detect_malicious_patterns(content, check_types=['xss'])
        assert 'xss' in detected
    
    def test_detect_xss_javascript_protocol(self):
        """Test detecting XSS javascript: protocol"""
        detector = MaliciousContentDetector()
        content = "javascript:alert(1)"
        detected = detector.detect_malicious_patterns(content, check_types=['xss'])
        assert 'xss' in detected
    
    def test_detect_xss_event_handler(self):
        """Test detecting XSS event handler"""
        detector = MaliciousContentDetector()
        content = "<img onerror=alert(1)>"
        detected = detector.detect_malicious_patterns(content, check_types=['xss'])
        assert 'xss' in detected
    
    def test_detect_path_traversal(self):
        """Test detecting path traversal"""
        detector = MaliciousContentDetector()
        content = "../../etc/passwd"
        detected = detector.detect_malicious_patterns(content, check_types=['path'])
        assert 'path' in detected
    
    def test_detect_path_traversal_encoded(self):
        """Test detecting encoded path traversal"""
        detector = MaliciousContentDetector()
        content = "%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        detected = detector.detect_malicious_patterns(content, check_types=['path'])
        assert 'path' in detected
    
    def test_detect_command_injection(self):
        """Test detecting command injection"""
        detector = MaliciousContentDetector()
        content = "; ls -la"
        detected = detector.detect_malicious_patterns(content, check_types=['command'])
        assert 'command' in detected
    
    def test_detect_command_injection_pipe(self):
        """Test detecting command injection with pipe"""
        detector = MaliciousContentDetector()
        content = "| cat /etc/passwd"
        detected = detector.detect_malicious_patterns(content, check_types=['command'])
        assert 'command' in detected
    
    def test_detect_multiple_patterns(self):
        """Test detecting multiple malicious patterns"""
        detector = MaliciousContentDetector()
        content = "<script>alert(1)</script> SELECT * FROM users"
        detected = detector.detect_malicious_patterns(content)
        assert 'xss' in detected
        assert 'sql' in detected
    
    def test_is_malicious(self):
        """Test is_malicious helper"""
        detector = MaliciousContentDetector()
        
        # Malicious content
        assert detector.is_malicious("<script>alert(1)</script>") is True
        
        # Safe content
        assert detector.is_malicious("Hello, World!") is False
    
    def test_clean_content_not_flagged(self):
        """Test clean content is not flagged"""
        detector = MaliciousContentDetector()
        content = "This is a normal article about web security."
        detected = detector.detect_malicious_patterns(content)
        assert len(detected) == 0


# ============================================================================
# Legacy Function Tests
# ============================================================================

class TestLegacyFunctions:
    """Test legacy compatibility functions"""
    
    def test_sanitize_url_legacy(self):
        """Test legacy sanitize_url function"""
        # Valid URL
        result = sanitize_url("http://example.com")
        assert result == "http://example.com"
        
        # Invalid URL
        result = sanitize_url("javascript:alert(1)")
        assert result == ""
    
    def test_sanitize_html_legacy(self):
        """Test legacy sanitize_html function"""
        content = "<script>alert('xss')</script>"
        sanitized = sanitize_html(content)
        assert "&lt;" in sanitized
        assert "<script>" not in sanitized
    
    def test_is_safe_url_legacy(self):
        """Test legacy is_safe_url function"""
        # Safe URL
        assert is_safe_url("http://example.com") is True
        
        # Unsafe URL
        assert is_safe_url("http://localhost") is False
        assert is_safe_url("javascript:alert(1)") is False
    
    def test_validate_content_length_legacy(self):
        """Test legacy validate_content_length function"""
        # Valid length
        assert validate_content_length("Hello", max_length=100) is True
        
        # Exceeds length
        assert validate_content_length("x" * 200, max_length=100) is False
    
    def test_remove_sensitive_data(self):
        """Test removing sensitive data"""
        text = "Contact: user@example.com or 555-123-4567 Card: 1234-5678-9012-3456"
        cleaned = remove_sensitive_data(text)
        
        assert "user@example.com" not in cleaned
        assert "[EMAIL]" in cleaned
        assert "555-123-4567" not in cleaned
        assert "[PHONE]" in cleaned
        assert "1234-5678-9012-3456" not in cleaned
        assert "[CARD]" in cleaned


class TestContentFilter:
    """Test legacy ContentFilter class"""
    
    def test_validate_content_type(self):
        """Test content type validation"""
        filter = ContentFilter()
        
        # Valid types
        assert filter.validate_content_type("text/html") is True
        assert filter.validate_content_type("application/xml") is True
        
        # Invalid types
        assert filter.validate_content_type("application/pdf") is False
    
    def test_validate_size(self):
        """Test size validation"""
        filter = ContentFilter(max_size=1000)
        
        # Valid size
        assert filter.validate_size(500) is True
        
        # Invalid size
        assert filter.validate_size(2000) is False


# ============================================================================
# Utility Function Tests
# ============================================================================

class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_create_secure_validator(self):
        """Test creating secure validator set"""
        validators = create_secure_validator(
            max_size=5000,
            block_private_ips=True,
            strict_sanitization=True
        )
        
        assert 'url_validator' in validators
        assert 'size_validator' in validators
        assert 'file_validator' in validators
        assert 'sanitizer' in validators
        assert 'malicious_detector' in validators
    
    def test_validate_request_valid(self):
        """Test validating a valid request"""
        is_valid, error = validate_request(
            url="http://example.com",
            content_length=1000,
            content_type="text/html"
        )
        assert is_valid is True
        assert error is None
    
    def test_validate_request_invalid_url(self):
        """Test validating request with invalid URL"""
        is_valid, error = validate_request(
            url="http://localhost",
            content_length=1000,
            content_type="text/html"
        )
        assert is_valid is False
        assert "URL validation failed" in error
    
    def test_validate_request_too_large(self):
        """Test validating request with content too large"""
        validators = create_secure_validator(max_size=100)
        is_valid, error = validate_request(
            url="http://example.com",
            content_length=10000,
            validators=validators
        )
        assert is_valid is False
        assert "Size validation failed" in error
    
    def test_validate_request_invalid_content_type(self):
        """Test validating request with invalid content type"""
        is_valid, error = validate_request(
            url="http://example.com",
            content_type="application/exe"
        )
        assert is_valid is False
        assert "Content type validation failed" in error
    
    def test_sanitize_and_validate_content_safe(self):
        """Test sanitizing and validating safe content"""
        content = "<p>This is a normal paragraph.</p>"
        sanitized, results = sanitize_and_validate_content(
            content,
            check_malicious=True,
            sanitize=True
        )
        
        assert results['safe'] is True
        assert len(results['malicious_patterns']) == 0
        assert results['sanitized'] is True
    
    def test_sanitize_and_validate_content_malicious(self):
        """Test sanitizing and validating malicious content"""
        content = "<script>alert('xss')</script> SELECT * FROM users"
        sanitized, results = sanitize_and_validate_content(
            content,
            check_malicious=True,
            sanitize=True
        )
        
        assert results['safe'] is False
        assert len(results['malicious_patterns']) > 0
        assert results['sanitized'] is True
        assert "<script>" not in sanitized.lower()


# ============================================================================
# Integration Tests
# ============================================================================

class TestSecurityIntegration:
    """Test integrated security scenarios"""
    
    def test_full_request_validation_success(self):
        """Test complete request validation with all checks"""
        validators = create_secure_validator()
        
        # Validate URL
        url = "http://example.com/page.html"
        is_valid, _ = validators['url_validator'].validate_url(url, raise_exception=False)
        assert is_valid is True
        
        # Validate size
        is_valid, _ = validators['size_validator'].validate_size(5000, raise_exception=False)
        assert is_valid is True
        
        # Validate file type
        is_valid, _ = validators['file_validator'].validate_mime_type("text/html", raise_exception=False)
        assert is_valid is True
    
    def test_full_request_validation_failure(self):
        """Test complete request validation with failures"""
        validators = create_secure_validator(max_size=100)
        
        # Invalid URL (localhost)
        url = "http://localhost/page.html"
        is_valid, _ = validators['url_validator'].validate_url(url, raise_exception=False)
        assert is_valid is False
        
        # Too large
        is_valid, _ = validators['size_validator'].validate_size(50000, raise_exception=False)
        assert is_valid is False
        
        # Invalid content type
        is_valid, _ = validators['file_validator'].validate_mime_type("application/exe", raise_exception=False)
        assert is_valid is False
    
    def test_content_pipeline(self):
        """Test complete content processing pipeline"""
        # Step 1: Validate request
        is_valid, error = validate_request(
            url="http://example.com",
            content_length=5000,
            content_type="text/html"
        )
        assert is_valid is True
        
        # Step 2: Process content
        html_content = """
        <div>
            <h1>Article Title</h1>
            <p>This is the content.</p>
            <script>alert('xss')</script>
        </div>
        """
        
        sanitized, results = sanitize_and_validate_content(
            html_content,
            check_malicious=True,
            sanitize=True
        )
        
        # Should detect XSS
        assert results['safe'] is False
        assert 'xss' in results['malicious_patterns']
        
        # Should sanitize
        assert results['sanitized'] is True
        assert "<script>" not in sanitized.lower()
    
    def test_whitelist_configuration(self):
        """Test whitelist-based security"""
        validators = create_secure_validator(
            allowed_domains={"example.com", "trusted.org"}
        )
        
        # Allowed domain
        is_valid, _ = validators['url_validator'].validate_url(
            "http://example.com",
            raise_exception=False
        )
        assert is_valid is True
        
        # Not allowed domain
        is_valid, error = validators['url_validator'].validate_url(
            "http://untrusted.com",
            raise_exception=False
        )
        assert is_valid is False
        assert "whitelist" in error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Security Integration Examples

This module demonstrates how to integrate the comprehensive security features
into the web scraping workflow.
"""

import asyncio
from typing import Dict, Any, Optional
from backend.src.utils.security import (
    create_secure_validator,
    validate_request,
    sanitize_and_validate_content,
    URLValidator,
    ContentSizeValidator,
    FileTypeValidator,
    ContentSanitizer,
    MaliciousContentDetector,
)
from backend.src.utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# Example 1: Basic URL Validation
# ============================================================================

async def example_1_basic_url_validation():
    """
    Example 1: Basic URL validation before scraping
    
    Demonstrates:
    - URL validation
    - SSRF prevention
    - Error handling
    """
    print("\n" + "="*70)
    print("Example 1: Basic URL Validation")
    print("="*70)
    
    validator = URLValidator()
    
    test_urls = [
        ("http://example.com", "Valid public URL"),
        ("http://localhost:8080", "Localhost (should block)"),
        ("http://127.0.0.1", "Loopback (should block)"),
        ("http://192.168.1.1", "Private IP (should block)"),
        ("http://169.254.169.254", "AWS metadata (should block)"),
        ("javascript:alert(1)", "Dangerous protocol (should block)"),
        ("http://10.0.0.1", "Private IP (should block)"),
    ]
    
    for url, description in test_urls:
        is_valid, error = validator.validate_url(url, raise_exception=False)
        status = "✅ ALLOWED" if is_valid else f"❌ BLOCKED: {error}"
        print(f"{description:30} {url:40} {status}")


# ============================================================================
# Example 2: Complete Request Validation
# ============================================================================

async def example_2_complete_request_validation():
    """
    Example 2: Complete request validation
    
    Demonstrates:
    - URL validation
    - Content size validation
    - Content type validation
    - Comprehensive error handling
    """
    print("\n" + "="*70)
    print("Example 2: Complete Request Validation")
    print("="*70)
    
    test_requests = [
        {
            "url": "http://example.com/page.html",
            "content_length": 5000,
            "content_type": "text/html",
            "description": "Valid request"
        },
        {
            "url": "http://localhost/admin",
            "content_length": 5000,
            "content_type": "text/html",
            "description": "Localhost URL (should fail)"
        },
        {
            "url": "http://example.com/large.html",
            "content_length": 50 * 1024 * 1024,  # 50 MB
            "content_type": "text/html",
            "description": "Content too large (should fail)"
        },
        {
            "url": "http://example.com/file.exe",
            "content_length": 5000,
            "content_type": "application/octet-stream",
            "description": "Invalid content type (should fail)"
        },
    ]
    
    for request in test_requests:
        is_valid, error = validate_request(
            url=request["url"],
            content_length=request["content_length"],
            content_type=request["content_type"]
        )
        
        status = "✅ VALID" if is_valid else f"❌ INVALID: {error}"
        print(f"{request['description']:40} {status}")


# ============================================================================
# Example 3: Content Sanitization
# ============================================================================

async def example_3_content_sanitization():
    """
    Example 3: Content sanitization and XSS prevention
    
    Demonstrates:
    - HTML sanitization
    - XSS prevention
    - Malicious pattern detection
    """
    print("\n" + "="*70)
    print("Example 3: Content Sanitization")
    print("="*70)
    
    test_contents = [
        (
            "<div><h1>Safe Content</h1><p>This is normal text.</p></div>",
            "Safe HTML content"
        ),
        (
            "<div><script>alert('xss')</script><p>Content</p></div>",
            "XSS attack (script tag)"
        ),
        (
            "<img src='x' onerror='alert(1)' />",
            "XSS attack (event handler)"
        ),
        (
            "<a href='javascript:void(0)'>Click</a>",
            "JavaScript protocol"
        ),
        (
            "SELECT * FROM users WHERE id=1 OR 1=1",
            "SQL injection attempt"
        ),
    ]
    
    for content, description in test_contents:
        sanitized, results = sanitize_and_validate_content(
            content,
            check_malicious=True,
            sanitize=True
        )
        
        print(f"\n{description}")
        print(f"Original:  {content[:60]}...")
        print(f"Sanitized: {sanitized[:60]}...")
        print(f"Safe: {results['safe']}")
        if results['malicious_patterns']:
            print(f"Detected patterns: {results['malicious_patterns']}")


# ============================================================================
# Example 4: Domain Whitelist Configuration
# ============================================================================

async def example_4_domain_whitelist():
    """
    Example 4: Domain whitelist configuration
    
    Demonstrates:
    - Configuring allowed domains
    - Blocking unapproved domains
    - Use case: Only scraping from trusted sources
    """
    print("\n" + "="*70)
    print("Example 4: Domain Whitelist Configuration")
    print("="*70)
    
    # Configure validator with whitelist
    validator = URLValidator(
        allowed_domains={"example.com", "trusted.org", "safe.net"}
    )
    
    test_urls = [
        ("http://example.com/page", "Whitelisted domain"),
        ("http://trusted.org/article", "Whitelisted domain"),
        ("http://safe.net/data", "Whitelisted domain"),
        ("http://untrusted.com/page", "Not whitelisted"),
        ("http://malicious.com/page", "Not whitelisted"),
    ]
    
    print("\nAllowed domains: example.com, trusted.org, safe.net\n")
    
    for url, description in test_urls:
        is_valid, error = validator.validate_url(url, raise_exception=False)
        status = "✅ ALLOWED" if is_valid else f"❌ BLOCKED: {error}"
        print(f"{description:25} {url:40} {status}")


# ============================================================================
# Example 5: Malicious Content Detection
# ============================================================================

async def example_5_malicious_detection():
    """
    Example 5: Malicious content detection
    
    Demonstrates:
    - SQL injection detection
    - XSS detection
    - Path traversal detection
    - Command injection detection
    """
    print("\n" + "="*70)
    print("Example 5: Malicious Content Detection")
    print("="*70)
    
    detector = MaliciousContentDetector()
    
    test_contents = [
        (
            "SELECT * FROM users WHERE username='admin'",
            "SQL injection",
            ['sql']
        ),
        (
            "<script>alert('xss')</script>",
            "XSS attack",
            ['xss']
        ),
        (
            "../../etc/passwd",
            "Path traversal",
            ['path']
        ),
        (
            "; ls -la /root",
            "Command injection",
            ['command']
        ),
        (
            "This is normal content about web security",
            "Clean content",
            None
        ),
    ]
    
    for content, description, expected_types in test_contents:
        patterns = detector.detect_malicious_patterns(content)
        is_malicious = detector.is_malicious(content)
        
        print(f"\n{description}")
        print(f"Content: {content[:60]}...")
        print(f"Malicious: {is_malicious}")
        if patterns:
            print(f"Detected: {list(patterns.keys())}")


# ============================================================================
# Example 6: Integrated Secure Scraping Workflow
# ============================================================================

class SecureWebScraper:
    """
    Example secure web scraper with integrated security
    
    Demonstrates:
    - Complete security integration
    - Multi-layer validation
    - Error handling
    - Logging
    """
    
    def __init__(
        self,
        max_size: int = 10 * 1024 * 1024,
        allowed_domains: Optional[set] = None,
        strict_sanitization: bool = True
    ):
        """
        Initialize secure scraper
        
        Args:
            max_size: Maximum content size
            allowed_domains: Allowed domains (None = all)
            strict_sanitization: Use strict HTML sanitization
        """
        self.validators = create_secure_validator(
            max_size=max_size,
            allowed_domains=allowed_domains,
            strict_sanitization=strict_sanitization
        )
        
        logger.info("SecureWebScraper initialized")
    
    async def scrape(self, url: str) -> Dict[str, Any]:
        """
        Securely scrape a URL
        
        Args:
            url: URL to scrape
            
        Returns:
            Scraping results with security information
            
        Raises:
            ValueError: If security validation fails
        """
        result = {
            'url': url,
            'success': False,
            'content': None,
            'security': {
                'url_valid': False,
                'content_safe': False,
                'sanitized': False,
                'patterns': {}
            }
        }
        
        # Step 1: Validate URL
        logger.info(f"Validating URL: {url}")
        is_valid, error = self.validators['url_validator'].validate_url(
            url, 
            raise_exception=False
        )
        
        if not is_valid:
            logger.error(f"URL validation failed: {error}")
            result['error'] = f"URL validation failed: {error}"
            return result
        
        result['security']['url_valid'] = True
        
        # Step 2: Simulate fetch (in real implementation, use httpx)
        # For demo purposes, use sample content
        logger.info(f"Fetching content from: {url}")
        sample_content = """
        <html>
            <head><title>Example Page</title></head>
            <body>
                <h1>Article Title</h1>
                <p>This is the main content of the article.</p>
                <script>console.log('tracking')</script>
            </body>
        </html>
        """
        content_length = len(sample_content)
        content_type = "text/html"
        
        # Step 3: Validate content size
        logger.info(f"Validating content size: {content_length} bytes")
        is_valid, error = self.validators['size_validator'].validate_size(
            content_length,
            raise_exception=False
        )
        
        if not is_valid:
            logger.error(f"Content size validation failed: {error}")
            result['error'] = f"Content size validation failed: {error}"
            return result
        
        # Step 4: Validate content type
        logger.info(f"Validating content type: {content_type}")
        is_valid, error = self.validators['file_validator'].validate_mime_type(
            content_type,
            raise_exception=False
        )
        
        if not is_valid:
            logger.error(f"Content type validation failed: {error}")
            result['error'] = f"Content type validation failed: {error}"
            return result
        
        # Step 5: Sanitize and validate content
        logger.info("Sanitizing and validating content")
        sanitized, validation_results = sanitize_and_validate_content(
            sample_content,
            check_malicious=True,
            sanitize=True,
            validators=self.validators
        )
        
        result['content'] = sanitized
        result['security']['content_safe'] = validation_results['safe']
        result['security']['sanitized'] = validation_results['sanitized']
        result['security']['patterns'] = validation_results['malicious_patterns']
        
        if not validation_results['safe']:
            logger.warning(
                f"Malicious patterns detected: {validation_results['malicious_patterns']}"
            )
        
        result['success'] = True
        logger.info(f"Successfully scraped: {url}")
        
        return result


async def example_6_integrated_workflow():
    """
    Example 6: Integrated secure scraping workflow
    
    Demonstrates:
    - Complete scraping workflow with security
    - Multi-layer validation
    - Error handling
    - Result inspection
    """
    print("\n" + "="*70)
    print("Example 6: Integrated Secure Scraping Workflow")
    print("="*70)
    
    # Create secure scraper
    scraper = SecureWebScraper(
        max_size=10 * 1024 * 1024,
        allowed_domains=None,  # Allow all (for demo)
        strict_sanitization=True
    )
    
    # Test URLs
    test_urls = [
        "http://example.com/article",
        "http://localhost:8080/admin",
        "http://malicious.com/page",
    ]
    
    for url in test_urls:
        print(f"\n{'─'*70}")
        print(f"Scraping: {url}")
        print(f"{'─'*70}")
        
        result = await scraper.scrape(url)
        
        print(f"Success: {result['success']}")
        print(f"URL Valid: {result['security']['url_valid']}")
        
        if result['success']:
            print(f"Content Safe: {result['security']['content_safe']}")
            print(f"Sanitized: {result['security']['sanitized']}")
            if result['security']['patterns']:
                print(f"Patterns Detected: {result['security']['patterns']}")
            print(f"Content Length: {len(result['content'])} chars")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")


# ============================================================================
# Example 7: Custom Security Configuration
# ============================================================================

async def example_7_custom_configuration():
    """
    Example 7: Custom security configuration
    
    Demonstrates:
    - Custom validators
    - Flexible configuration
    - Production vs development settings
    """
    print("\n" + "="*70)
    print("Example 7: Custom Security Configuration")
    print("="*70)
    
    # Production configuration (strict)
    print("\n--- Production Configuration (Strict) ---")
    prod_validators = create_secure_validator(
        max_size=5 * 1024 * 1024,  # 5 MB limit
        allowed_domains={"example.com", "trusted.org"},
        block_private_ips=True,
        strict_sanitization=True
    )
    
    # Development configuration (relaxed)
    print("\n--- Development Configuration (Relaxed) ---")
    dev_validators = create_secure_validator(
        max_size=20 * 1024 * 1024,  # 20 MB limit
        allowed_domains=None,  # Allow all
        block_private_ips=False,  # Allow localhost
        strict_sanitization=False
    )
    
    # Test with both configurations
    test_url = "http://localhost:8080/test"
    
    print(f"\nTesting URL: {test_url}")
    
    # Production
    is_valid, error = prod_validators['url_validator'].validate_url(
        test_url, 
        raise_exception=False
    )
    print(f"Production: {'✅ Valid' if is_valid else f'❌ Blocked - {error}'}")
    
    # Development
    is_valid, error = dev_validators['url_validator'].validate_url(
        test_url,
        raise_exception=False
    )
    print(f"Development: {'✅ Valid' if is_valid else f'❌ Blocked - {error}'}")


# ============================================================================
# Main Example Runner
# ============================================================================

async def run_all_examples():
    """Run all security integration examples"""
    print("\n" + "="*70)
    print("SECURITY INTEGRATION EXAMPLES")
    print("="*70)
    print("\nThese examples demonstrate how to integrate comprehensive security")
    print("into the web scraping workflow.")
    print("="*70)
    
    # Run all examples
    await example_1_basic_url_validation()
    await example_2_complete_request_validation()
    await example_3_content_sanitization()
    await example_4_domain_whitelist()
    await example_5_malicious_detection()
    await example_6_integrated_workflow()
    await example_7_custom_configuration()
    
    print("\n" + "="*70)
    print("ALL EXAMPLES COMPLETED")
    print("="*70)


if __name__ == "__main__":
    # Run examples
    asyncio.run(run_all_examples())

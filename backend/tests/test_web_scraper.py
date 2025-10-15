"""
Test Web Scraper Service
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import httpx

from src.scrapers.web_scraper import WebScraperService
from src.utils.exceptions import ScrapingError


@pytest.fixture
def scraper():
    """Create a WebScraperService instance"""
    return WebScraperService(timeout=10.0, max_retries=2)


@pytest.mark.asyncio
async def test_scrape_url_success(scraper):
    """Test successful URL scraping"""
    with patch('httpx.AsyncClient') as mock_client:
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html; charset=utf-8"}
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.raise_for_status = Mock()
        
        # Configure mock client
        mock_client_instance = Mock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Test scraping
        result = await scraper.scrape_url("https://example.com")
        
        assert result == "<html><body>Test content</body></html>"
        assert scraper.request_count == 1


@pytest.mark.asyncio
async def test_scrape_url_invalid_url(scraper):
    """Test scraping with invalid URL"""
    with pytest.raises(ScrapingError) as exc_info:
        await scraper.scrape_url("javascript:alert('xss')")
    
    assert "Invalid or unsafe URL" in str(exc_info.value)


@pytest.mark.asyncio
async def test_scrape_url_timeout(scraper):
    """Test scraping with timeout"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_client_instance = Mock()
        mock_client_instance.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        with pytest.raises(ScrapingError) as exc_info:
            await scraper.scrape_url("https://example.com")
        
        assert "Timeout" in str(exc_info.value)


@pytest.mark.asyncio
async def test_scrape_url_http_error(scraper):
    """Test scraping with HTTP error"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 404
        
        mock_client_instance = Mock()
        mock_client_instance.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Not Found",
                request=Mock(),
                response=mock_response
            )
        )
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        with pytest.raises(ScrapingError) as exc_info:
            await scraper.scrape_url("https://example.com/notfound")
        
        assert "404" in str(exc_info.value)


@pytest.mark.asyncio
async def test_scrape_url_invalid_content_type(scraper):
    """Test scraping with invalid content type"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.raise_for_status = Mock()
        
        mock_client_instance = Mock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        with pytest.raises(ScrapingError) as exc_info:
            await scraper.scrape_url("https://example.com")
        
        assert "Invalid content type" in str(exc_info.value)


@pytest.mark.asyncio
async def test_scrape_url_content_too_large(scraper):
    """Test scraping with content size limit"""
    with patch('httpx.AsyncClient') as mock_client:
        large_content = "x" * (scraper.max_content_size + 1000)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "content-type": "text/html",
            "content-length": str(len(large_content))
        }
        mock_response.text = large_content
        mock_response.raise_for_status = Mock()
        
        mock_client_instance = Mock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        with pytest.raises(ScrapingError) as exc_info:
            await scraper.scrape_url("https://example.com")
        
        assert "Content too large" in str(exc_info.value)


def test_validate_url_valid(scraper):
    """Test URL validation with valid URLs"""
    assert scraper._validate_url("https://example.com") == True
    assert scraper._validate_url("http://example.com") == True
    assert scraper._validate_url("https://example.com/path?query=value") == True


def test_validate_url_invalid(scraper):
    """Test URL validation with invalid URLs"""
    assert scraper._validate_url("javascript:alert(1)") == False
    assert scraper._validate_url("data:text/html,<script>") == False
    assert scraper._validate_url("file:///etc/passwd") == False
    assert scraper._validate_url("not-a-url") == False
    assert scraper._validate_url("") == False


def test_get_headers(scraper):
    """Test header generation with user-agent rotation"""
    headers1 = scraper._get_headers()
    headers2 = scraper._get_headers()
    
    # Check required headers
    assert "User-Agent" in headers1
    assert "Accept" in headers1
    assert "Accept-Language" in headers1
    
    # User-Agent should be from the pool
    assert headers1["User-Agent"] in scraper.USER_AGENTS
    
    # Test custom headers
    custom_options = {"custom_headers": {"X-Custom": "value"}}
    headers3 = scraper._get_headers(custom_options)
    assert headers3["X-Custom"] == "value"


@pytest.mark.asyncio
async def test_rate_limiting(scraper):
    """Test rate limiting delay"""
    import time
    
    start_time = time.time()
    
    # First request - no delay
    await scraper._apply_rate_limit()
    
    # Second request - should have delay
    await scraper._apply_rate_limit()
    
    elapsed = time.time() - start_time
    
    # Should have at least MIN_REQUEST_DELAY
    assert elapsed >= scraper.MIN_REQUEST_DELAY


def test_validate_content(scraper):
    """Test content validation"""
    # Valid HTML content
    valid_html = "<html><body>Content</body></html>"
    scraper._validate_content(valid_html, "https://example.com")
    
    # Empty content should raise error
    with pytest.raises(ScrapingError):
        scraper._validate_content("", "https://example.com")
    
    # Whitespace only should raise error
    with pytest.raises(ScrapingError):
        scraper._validate_content("   ", "https://example.com")


def test_get_stats(scraper):
    """Test scraper statistics"""
    scraper.request_count = 5
    
    stats = scraper.get_stats()
    
    assert stats["total_requests"] == 5
    assert stats["max_retries"] == scraper.max_retries
    assert stats["timeout"] == scraper.timeout
    assert stats["max_content_size"] == scraper.max_content_size
    assert stats["user_agents_pool"] == len(scraper.USER_AGENTS)


@pytest.mark.asyncio
async def test_retry_logic(scraper):
    """Test retry logic with exponential backoff"""
    with patch('httpx.AsyncClient') as mock_client:
        # First two attempts fail, third succeeds
        mock_response_fail = Mock()
        mock_response_fail.status_code = 503
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.headers = {"content-type": "text/html"}
        mock_response_success.text = "<html>Success</html>"
        mock_response_success.raise_for_status = Mock()
        
        call_count = 0
        
        async def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise httpx.HTTPStatusError(
                    "Service Unavailable",
                    request=Mock(),
                    response=mock_response_fail
                )
            return mock_response_success
        
        mock_client_instance = Mock()
        mock_client_instance.get = mock_get
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        result = await scraper.scrape_url("https://example.com")
        
        assert result == "<html>Success</html>"
        assert call_count == 2  # Failed once, then succeeded


@pytest.mark.asyncio
async def test_rate_limit_429_handling(scraper):
    """Test handling of 429 Rate Limit responses"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {"Retry-After": "2"}
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.headers = {"content-type": "text/html"}
        mock_response_success.text = "<html>Success</html>"
        mock_response_success.raise_for_status = Mock()
        
        call_count = 0
        
        async def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise httpx.HTTPStatusError(
                    "Rate Limited",
                    request=Mock(),
                    response=mock_response_429
                )
            return mock_response_success
        
        mock_client_instance = Mock()
        mock_client_instance.get = mock_get
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        result = await scraper.scrape_url("https://example.com")
        
        assert result == "<html>Success</html>"
        assert call_count == 2

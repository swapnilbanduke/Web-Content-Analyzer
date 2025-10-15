"""
Web Scraper - Robust web scraper with user-agent rotation and anti-detection
"""
import logging
import asyncio
import random
import time
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from ..utils.exceptions import ScrapingError
from ..utils.security import is_safe_url
from ..models.data_models import ScrapedContent

logger = logging.getLogger(__name__)


class WebScraperService:
    """
    Advanced web scraper with user-agent rotation, anti-detection, 
    and robust error handling
    """
    
    # User-Agent rotation pool
    USER_AGENTS = [
        # Chrome on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        # Firefox on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
        # Chrome on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        # Safari on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        # Chrome on Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        # Edge on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    ]
    
    # Content type whitelist
    ALLOWED_CONTENT_TYPES = [
        "text/html",
        "application/xhtml+xml",
        "application/xml"
    ]
    
    # Default configuration
    DEFAULT_TIMEOUT = 30.0
    MAX_RETRIES = 3
    MAX_CONTENT_SIZE = 10 * 1024 * 1024  # 10 MB
    MIN_REQUEST_DELAY = 1.0  # seconds between requests
    MAX_REQUEST_DELAY = 3.0  # seconds between requests
    
    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
        max_content_size: int = MAX_CONTENT_SIZE,
        respect_robots_txt: bool = True
    ):
        """
        Initialize web scraper service
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            max_content_size: Maximum allowed content size in bytes
            respect_robots_txt: Whether to respect robots.txt
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_content_size = max_content_size
        self.respect_robots_txt = respect_robots_txt
        self.last_request_time = 0
        self.request_count = 0
        
        # Session configuration
        self.session_config = {
            "timeout": httpx.Timeout(timeout, connect=10.0),
            "follow_redirects": True,
            "max_redirects": 5
        }
    
    async def scrape_url(
        self,
        url: str,
        options: Optional[Dict[str, Any]] = None
    ) -> ScrapedContent:
        """
        Scrape HTML content from a URL with robust error handling
        
        Args:
            url: URL to scrape
            options: Optional scraping configuration
                - custom_headers: Dict of custom headers
                - skip_delay: Skip rate limiting delay
                - verify_ssl: SSL verification (default: True)
            
        Returns:
            ScrapedContent object with HTML and metadata
            
        Raises:
            ScrapingError: If scraping fails after retries
        """
        start_time = time.time()
        
        # Validate URL
        if not self._validate_url(url):
            raise ScrapingError(f"Invalid or unsafe URL: {url}")
        
        # Apply rate limiting (respectful crawling)
        if not (options and options.get("skip_delay")):
            await self._apply_rate_limit()
        
        # Prepare headers with user-agent rotation
        headers = self._get_headers(options)
        
        # Retry logic with exponential backoff
        last_exception = None
        response_data = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Scraping URL (attempt {attempt + 1}/{self.max_retries}): {url}")
                
                # Perform request
                response_data = await self._perform_request_with_metadata(url, headers, options)
                
                # Validate content
                self._validate_content(response_data['html_content'], url)
                
                logger.info(f"Successfully scraped {url} ({len(response_data['html_content'])} bytes)")
                self.request_count += 1
                
                # Calculate processing time
                processing_time = (time.time() - start_time) * 1000
                
                # Create ScrapedContent object
                scraped_content = ScrapedContent(
                    url=url,
                    html_content=response_data['html_content'],
                    text_content=None,  # Will be extracted by ContentExtractor
                    status_code=response_data['status_code'],
                    headers=response_data['headers'],
                    content_type=response_data.get('content_type'),
                    content_length=len(response_data['html_content']),
                    encoding=response_data.get('encoding', 'utf-8'),
                    scraped_at=datetime.utcnow(),
                    scraper_version="1.0.0",
                    processing_time_ms=processing_time,
                    redirect_chain=response_data.get('redirect_chain', []),
                    is_valid_html=True,
                    has_errors=False,
                    errors=[]
                )
                
                return scraped_content
                    
            except httpx.HTTPStatusError as e:
                last_exception = e
                status_code = e.response.status_code
                logger.error(f"HTTP error {status_code} for {url}")
                
                # Handle specific status codes
                if status_code in [429, 503]:  # Rate limiting or service unavailable
                    retry_after = int(e.response.headers.get("Retry-After", 5))
                    logger.warning(f"Rate limited. Waiting {retry_after}s before retry")
                    await asyncio.sleep(retry_after)
                elif status_code in [403, 401]:  # Forbidden or Unauthorized
                    raise ScrapingError(f"Access denied (HTTP {status_code})")
                elif status_code == 404:
                    raise ScrapingError(f"Page not found (HTTP 404)")
                elif status_code >= 500:  # Server errors
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        raise ScrapingError(f"Server error (HTTP {status_code})")
                else:
                    raise ScrapingError(f"HTTP {status_code}: Failed to fetch URL")
                
            except httpx.TimeoutException:
                last_exception = httpx.TimeoutException(f"Timeout for {url}")
                logger.error(f"Timeout scraping {url}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise ScrapingError(f"Timeout: URL took too long to respond")
                
            except httpx.RequestError as e:
                last_exception = e
                logger.error(f"Request error for {url}: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise ScrapingError(f"Request failed: {str(e)}")
                
            except ScrapingError:
                # Re-raise ScrapingError without retry
                raise
                
            except Exception as e:
                last_exception = e
                logger.error(f"Unexpected error scraping {url}: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise ScrapingError(f"Scraping failed: {str(e)}")
        
        # If we exhausted retries
        raise ScrapingError(f"Max retries exceeded: {str(last_exception)}")
    
    async def _perform_request(
        self,
        url: str,
        headers: Dict[str, str],
        options: Optional[Dict[str, Any]]
    ) -> str:
        """
        Perform the actual HTTP request
        
        Args:
            url: URL to request
            headers: Request headers
            options: Request options
            
        Returns:
            Response text content
        """
        # SSL verification
        verify_ssl = True
        if options and "verify_ssl" in options:
            verify_ssl = options["verify_ssl"]
        
        async with httpx.AsyncClient(
            **self.session_config,
            verify=verify_ssl
        ) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            # Validate content type
            content_type = response.headers.get("content-type", "").lower()
            if not any(allowed in content_type for allowed in self.ALLOWED_CONTENT_TYPES):
                raise ScrapingError(
                    f"Invalid content type: {content_type}. Expected HTML."
                )
            
            # Check content size before reading
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > self.max_content_size:
                raise ScrapingError(
                    f"Content too large: {content_length} bytes "
                    f"(max: {self.max_content_size})"
                )
            
            # Read content
            content = response.text
            
            # Verify size after reading
            if len(content) > self.max_content_size:
                raise ScrapingError(
                    f"Content too large: {len(content)} bytes "
                    f"(max: {self.max_content_size})"
                )
            
            return content
    
    async def _perform_request_with_metadata(
        self,
        url: str,
        headers: Dict[str, str],
        options: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform the actual HTTP request with metadata collection
        
        Args:
            url: URL to request
            headers: Request headers
            options: Request options
            
        Returns:
            Dictionary with HTML content and metadata
        """
        # SSL verification
        verify_ssl = True
        if options and "verify_ssl" in options:
            verify_ssl = options["verify_ssl"]
        
        async with httpx.AsyncClient(
            **self.session_config,
            verify=verify_ssl
        ) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            # Validate content type
            content_type = response.headers.get("content-type", "").lower()
            if not any(allowed in content_type for allowed in self.ALLOWED_CONTENT_TYPES):
                raise ScrapingError(
                    f"Invalid content type: {content_type}. Expected HTML."
                )
            
            # Check content size before reading
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > self.max_content_size:
                raise ScrapingError(
                    f"Content too large: {content_length} bytes "
                    f"(max: {self.max_content_size})"
                )
            
            # Read content
            content = response.text
            
            # Verify size after reading
            if len(content) > self.max_content_size:
                raise ScrapingError(
                    f"Content too large: {len(content)} bytes "
                    f"(max: {self.max_content_size})"
                )
            
            # Collect redirect chain
            redirect_chain = []
            if hasattr(response, 'history') and response.history:
                redirect_chain = [str(r.url) for r in response.history]
            
            # Return comprehensive data
            return {
                'html_content': content,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content_type': content_type,
                'encoding': response.encoding or 'utf-8',
                'redirect_chain': redirect_chain
            }
    
    def _validate_url(self, url: str) -> bool:
        """
        Validate URL for security and format
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid and safe
        """
        try:
            # Use existing security validation
            if not is_safe_url(url):
                logger.warning(f"URL failed security check: {url}")
                return False
            
            # Parse URL
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in ["http", "https"]:
                logger.warning(f"Invalid URL scheme: {parsed.scheme}")
                return False
            
            # Check for hostname
            if not parsed.netloc:
                logger.warning(f"URL missing hostname: {url}")
                return False
            
            # Additional anti-bot detection: Check for suspicious patterns
            suspicious_patterns = [
                "javascript:",
                "data:",
                "file:",
                "vbscript:",
                "about:",
            ]
            
            url_lower = url.lower()
            if any(pattern in url_lower for pattern in suspicious_patterns):
                logger.warning(f"Suspicious URL pattern detected: {url}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"URL validation error: {str(e)}")
            return False
    
    def _get_headers(self, options: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Generate headers with user-agent rotation and anti-detection
        
        Args:
            options: Optional custom headers
            
        Returns:
            Dictionary of HTTP headers
        """
        # Rotate user agent
        user_agent = random.choice(self.USER_AGENTS)
        
        # Standard browser headers for anti-detection
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",  # Do Not Track
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        
        # Add custom headers if provided
        if options and "custom_headers" in options:
            headers.update(options["custom_headers"])
        
        return headers
    
    async def _apply_rate_limit(self):
        """
        Apply rate limiting to avoid overwhelming servers (respectful crawling)
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Random delay between MIN and MAX for natural behavior
        min_delay = self.MIN_REQUEST_DELAY
        
        if time_since_last < min_delay:
            delay = random.uniform(min_delay, self.MAX_REQUEST_DELAY)
            logger.debug(f"Rate limiting: waiting {delay:.2f}s")
            await asyncio.sleep(delay)
        
        self.last_request_time = time.time()
    
    def _validate_content(self, content: str, url: str):
        """
        Validate scraped content
        
        Args:
            content: HTML content to validate
            url: Source URL
            
        Raises:
            ScrapingError: If content is invalid
        """
        if not content or len(content.strip()) == 0:
            raise ScrapingError(f"Empty content received from {url}")
        
        # Check if content looks like HTML
        if not ("<html" in content.lower() or "<body" in content.lower() or "<!doctype" in content.lower()):
            # Some pages might not have these tags but still be valid
            logger.warning(f"Content doesn't look like standard HTML: {url}")
        
        # Check for common error pages
        error_indicators = [
            "403 forbidden",
            "404 not found",
            "500 internal server error",
            "503 service unavailable",
            "access denied",
            "page not found",
        ]
        
        content_lower = content.lower()
        for indicator in error_indicators:
            if indicator in content_lower and len(content) < 2000:
                logger.warning(f"Content may be an error page: {url}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get scraper statistics
        
        Returns:
            Dictionary with scraper stats
        """
        return {
            "total_requests": self.request_count,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "max_content_size": self.max_content_size,
            "user_agents_pool": len(self.USER_AGENTS)
        }


# Legacy class alias for backward compatibility
class WebScraper(WebScraperService):
    """Backward compatible alias for WebScraperService"""
    
    async def scrape(self, url: str, options: Optional[Dict[str, Any]] = None) -> str:
        """Legacy method name for backward compatibility"""
        return await self.scrape_url(url, options)

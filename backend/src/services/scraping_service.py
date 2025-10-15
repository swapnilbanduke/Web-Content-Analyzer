"""
Scraping Service - High-level scraping operations with enhanced features
"""
import logging
from typing import Optional, Dict, Any
from ..scrapers.web_scraper import WebScraperService
from ..scrapers.content_extractor import ContentExtractor
from ..scrapers.robots_checker import RobotsChecker
from ..utils.security import sanitize_url
from ..utils.exceptions import ScrapingError

logger = logging.getLogger(__name__)


class ScrapingService:
    """
    Service for managing web scraping operations with robots.txt support
    """
    
    def __init__(
        self,
        respect_robots_txt: bool = True,
        max_content_size: int = 10 * 1024 * 1024,
        timeout: float = 30.0
    ):
        """
        Initialize scraping service
        
        Args:
            respect_robots_txt: Whether to check robots.txt
            max_content_size: Maximum content size in bytes
            timeout: Request timeout in seconds
        """
        self.web_scraper = WebScraperService(
            timeout=timeout,
            max_retries=3,
            max_content_size=max_content_size,
            respect_robots_txt=respect_robots_txt
        )
        self.content_extractor = ContentExtractor()
        self.robots_checker = RobotsChecker() if respect_robots_txt else None
        self.respect_robots_txt = respect_robots_txt
    
    async def scrape_and_extract(
        self,
        url: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Scrape a URL and extract structured content
        
        Args:
            url: URL to scrape
            options: Scraping options
                - timeout: Request timeout
                - custom_headers: Custom HTTP headers
                - skip_delay: Skip rate limiting
                - verify_ssl: SSL verification
                - skip_robots_check: Skip robots.txt check
            
        Returns:
            Extracted content with metadata
        """
        try:
            # Sanitize URL
            safe_url = sanitize_url(url)
            
            # Check robots.txt if enabled
            if self.respect_robots_txt and not (options and options.get("skip_robots_check")):
                if not await self._check_robots_txt(safe_url):
                    raise ScrapingError(
                        f"robots.txt disallows scraping this URL: {safe_url}"
                    )
            
            # Scrape the page with enhanced scraper
            html_content = await self.web_scraper.scrape_url(safe_url, options)
            
            # Extract structured content
            extracted = self.content_extractor.extract(html_content, safe_url)
            
            # Get scraper stats
            scraper_stats = self.web_scraper.get_stats()
            
            return {
                "url": safe_url,
                "content": extracted.main_content,
                "metadata": extracted.metadata,
                "links": extracted.links,
                "images": extracted.images,
                "scraper_stats": {
                    "content_size": len(html_content),
                    "total_requests": scraper_stats["total_requests"]
                }
            }
            
        except Exception as e:
            logger.error(f"Scraping service error for {url}: {str(e)}")
            raise ScrapingError(f"Failed to scrape URL: {str(e)}")
    
    async def _check_robots_txt(self, url: str) -> bool:
        """
        Check if URL is allowed by robots.txt
        
        Args:
            url: URL to check
            
        Returns:
            True if allowed, False otherwise
        """
        if not self.robots_checker:
            return True
        
        try:
            allowed = await self.robots_checker.can_fetch(url)
            
            if allowed:
                # Check for crawl delay
                delay = self.robots_checker.get_crawl_delay(url)
                if delay:
                    logger.info(f"robots.txt specifies crawl delay of {delay}s")
            
            return allowed
            
        except Exception as e:
            logger.warning(f"Error checking robots.txt: {str(e)}")
            # On error, allow by default
            return True
    
    def get_scraper_stats(self) -> Dict[str, Any]:
        """
        Get scraping service statistics
        
        Returns:
            Dictionary with service stats
        """
        return {
            "web_scraper": self.web_scraper.get_stats(),
            "robots_txt_enabled": self.respect_robots_txt,
            "robots_cache_size": len(self.robots_checker.cache) if self.robots_checker else 0
        }
    
    def clear_caches(self):
        """Clear all caches"""
        if self.robots_checker:
            self.robots_checker.clear_cache()
        logger.info("Cleared scraping service caches")

"""
Robots.txt Parser - Respect website crawling rules
"""
import logging
from typing import Optional, Dict, Set
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
import httpx

logger = logging.getLogger(__name__)


class RobotsChecker:
    """
    Checks robots.txt rules for respectful crawling
    """
    
    def __init__(self, user_agent: str = "WebContentAnalyzer"):
        """
        Initialize robots.txt checker
        
        Args:
            user_agent: User agent string to check rules for
        """
        self.user_agent = user_agent
        self.cache: Dict[str, RobotFileParser] = {}
        self.timeout = 10.0
    
    async def can_fetch(self, url: str) -> bool:
        """
        Check if URL can be fetched according to robots.txt
        
        Args:
            url: URL to check
            
        Returns:
            True if fetching is allowed, False otherwise
        """
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            # Get or create parser for this domain
            if robots_url not in self.cache:
                await self._fetch_robots(robots_url)
            
            # Check if URL is allowed
            parser = self.cache.get(robots_url)
            if parser is None:
                # If robots.txt doesn't exist or failed to parse, allow by default
                return True
            
            can_fetch = parser.can_fetch(self.user_agent, url)
            
            if not can_fetch:
                logger.warning(f"robots.txt disallows fetching: {url}")
            
            return can_fetch
            
        except Exception as e:
            logger.error(f"Error checking robots.txt for {url}: {str(e)}")
            # On error, allow by default (conservative approach)
            return True
    
    async def _fetch_robots(self, robots_url: str):
        """
        Fetch and parse robots.txt
        
        Args:
            robots_url: URL to robots.txt file
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(robots_url)
                
                if response.status_code == 200:
                    parser = RobotFileParser()
                    parser.parse(response.text.splitlines())
                    self.cache[robots_url] = parser
                    logger.info(f"Loaded robots.txt from {robots_url}")
                else:
                    # robots.txt doesn't exist, store None to cache the result
                    self.cache[robots_url] = None
                    logger.debug(f"No robots.txt found at {robots_url}")
                    
        except Exception as e:
            logger.warning(f"Failed to fetch robots.txt from {robots_url}: {str(e)}")
            self.cache[robots_url] = None
    
    def get_crawl_delay(self, url: str) -> Optional[float]:
        """
        Get crawl delay from robots.txt if specified
        
        Args:
            url: URL to check
            
        Returns:
            Crawl delay in seconds, or None if not specified
        """
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            parser = self.cache.get(robots_url)
            if parser:
                delay = parser.crawl_delay(self.user_agent)
                if delay:
                    return float(delay)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting crawl delay: {str(e)}")
            return None
    
    def clear_cache(self):
        """Clear the robots.txt cache"""
        self.cache.clear()
        logger.debug("Cleared robots.txt cache")

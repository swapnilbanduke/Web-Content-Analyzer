"""
Data Layer - Scrapers

Web scraping services for extracting content from websites.
"""

from .web_scraper import WebScraperService
from .content_extractor import ContentExtractor
from .metadata_extractor import MetadataExtractor
from .media_extractor import MediaExtractor
from .cms_detector import CMSDetector
from .structured_data_extractor import StructuredDataExtractor
from .robots_checker import RobotsChecker


class ScraperConfig:
    """Configuration for web scraper - wrapper for WebScraperService parameters"""
    def __init__(
        self,
        timeout: float = 30.0,
        max_retries: int = 3,
        max_content_size: int = 10 * 1024 * 1024,
        respect_robots_txt: bool = True
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_content_size = max_content_size
        self.respect_robots_txt = respect_robots_txt


# Aliases for backward compatibility
WebScraper = WebScraperService

__all__ = [
    'WebScraperService',
    'WebScraper',
    'ScraperConfig',
    'ContentExtractor',
    'MetadataExtractor',
    'MediaExtractor',
    'CMSDetector',
    'StructuredDataExtractor',
    'RobotsChecker',
]

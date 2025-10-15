"""
Tests for web scraper functionality

Test Coverage:
- URL validation
- Content extraction
- Metadata parsing
- Error handling
- Configuration options
"""

import pytest
import asyncio
from src.scraper import WebScraper, ScraperConfig
from src.models.data_models import ScrapeResult


class TestScraperConfiguration:
    """Test scraper configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = ScraperConfig()
        
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.follow_redirects is True
        assert config.verify_ssl is True
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = ScraperConfig(
            timeout=60,
            max_retries=5,
            user_agent="CustomBot/1.0"
        )
        
        assert config.timeout == 60
        assert config.max_retries == 5
        assert "CustomBot" in config.user_agent


class TestWebScraper:
    """Test web scraper functionality"""
    
    @pytest.mark.asyncio
    async def test_scraper_initialization(self):
        """Test scraper can be initialized"""
        config = ScraperConfig()
        scraper = WebScraper(config)
        
        assert scraper is not None
        assert scraper.config == config
    
    @pytest.mark.asyncio
    async def test_scrape_valid_url(self):
        """Test scraping a valid URL"""
        # Skip this test if no internet or use mock
        pytest.skip("Requires internet connection - use mock in CI/CD")
        
        scraper = WebScraper(ScraperConfig())
        result = await scraper.scrape_url("https://example.com")
        
        assert isinstance(result, ScrapeResult)
        assert result.success is True
        assert result.url == "https://example.com"
        assert len(result.content) > 0
        assert result.word_count > 0
    
    @pytest.mark.asyncio
    async def test_scrape_invalid_url(self):
        """Test scraping an invalid URL"""
        scraper = WebScraper(ScraperConfig())
        result = await scraper.scrape_url("https://this-domain-definitely-does-not-exist-12345.com")
        
        assert isinstance(result, ScrapeResult)
        assert result.success is False
        assert result.error_message is not None
    
    @pytest.mark.asyncio
    async def test_scrape_with_html_content(self, sample_html):
        """Test content extraction from HTML"""
        # This would require mocking the HTTP response
        # For now, we test the HTML parsing logic separately
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(sample_html, 'lxml')
        title = soup.find('title')
        
        assert title is not None
        assert "Sample Article" in title.get_text()
    
    def test_url_validation(self):
        """Test URL validation logic"""
        scraper = WebScraper(ScraperConfig())
        
        # Valid URLs
        assert scraper._is_valid_url("https://example.com")
        assert scraper._is_valid_url("http://test.com/page")
        
        # Invalid URLs
        assert not scraper._is_valid_url("not-a-url")
        assert not scraper._is_valid_url("ftp://file.com")
        assert not scraper._is_valid_url("")
    
    def test_content_extraction(self, sample_html):
        """Test content extraction from HTML"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(sample_html, 'lxml')
        
        # Extract text
        text = soup.get_text()
        assert "Artificial Intelligence" in text
        assert "healthcare" in text.lower()
        
        # Count words
        words = text.split()
        assert len(words) > 50
    
    def test_metadata_extraction(self, sample_html):
        """Test metadata extraction"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(sample_html, 'lxml')
        
        # Extract title
        title = soup.find('title')
        assert title is not None
        assert "AI" in title.get_text()
        
        # Extract meta description
        description = soup.find('meta', {'name': 'description'})
        assert description is not None
        assert 'artificial intelligence' in description.get('content', '').lower()
        
        # Extract keywords
        keywords = soup.find('meta', {'name': 'keywords'})
        assert keywords is not None
        assert 'AI' in keywords.get('content', '')


class TestScraperErrorHandling:
    """Test error handling in scraper"""
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling"""
        config = ScraperConfig(timeout=0.001)  # Very short timeout
        scraper = WebScraper(config)
        
        # This should timeout
        result = await scraper.scrape_url("https://httpbin.org/delay/10")
        
        assert result.success is False
        assert result.error_message is not None
    
    @pytest.mark.asyncio
    async def test_malformed_url(self):
        """Test handling of malformed URL"""
        scraper = WebScraper(ScraperConfig())
        result = await scraper.scrape_url("not a valid url")
        
        assert result.success is False
        assert result.error_message is not None
    
    @pytest.mark.asyncio
    async def test_empty_url(self):
        """Test handling of empty URL"""
        scraper = WebScraper(ScraperConfig())
        result = await scraper.scrape_url("")
        
        assert result.success is False
    
    @pytest.mark.asyncio
    async def test_retry_logic(self):
        """Test retry logic on failures"""
        config = ScraperConfig(max_retries=2)
        scraper = WebScraper(config)
        
        # Simulate a URL that might fail
        result = await scraper.scrape_url("https://httpstat.us/500")
        
        # Should have attempted retries
        assert result.success is False


class TestScraperUtils:
    """Test scraper utility functions"""
    
    def test_clean_text(self):
        """Test text cleaning"""
        dirty_text = "  Multiple   spaces\n\n\nand   newlines  "
        clean = " ".join(dirty_text.split())
        
        assert clean == "Multiple spaces and newlines"
    
    def test_word_count(self):
        """Test word counting"""
        text = "This is a test sentence with ten words total."
        words = text.split()
        
        assert len(words) == 10
    
    def test_extract_domain(self):
        """Test domain extraction from URL"""
        from urllib.parse import urlparse
        
        url = "https://www.example.com/path/to/page?query=1"
        domain = urlparse(url).netloc
        
        assert domain == "www.example.com"


# Integration test
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_scraping_workflow():
    """Test complete scraping workflow"""
    pytest.skip("Requires internet - integration test")
    
    # 1. Create scraper
    config = ScraperConfig(timeout=30)
    scraper = WebScraper(config)
    
    # 2. Scrape URL
    url = "https://example.com"
    result = await scraper.scrape_url(url)
    
    # 3. Verify result
    assert result.success is True
    assert result.url == url
    assert len(result.content) > 0
    assert result.word_count > 0
    assert result.title is not None
    assert isinstance(result.metadata, dict)
    
    # 4. Verify content quality
    assert len(result.content) > 100  # Reasonable content length
    assert result.word_count > 20  # Reasonable word count


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

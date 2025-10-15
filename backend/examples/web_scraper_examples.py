"""
Web Scraper Service - Usage Examples
Demonstrates various ways to use the enhanced web scraping service
"""
import asyncio
import logging
from src.scrapers.web_scraper import WebScraperService
from src.services.scraping_service import ScrapingService
from src.scrapers.robots_checker import RobotsChecker
from src.utils.exceptions import ScrapingError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_1_basic_scraping():
    """Example 1: Basic URL scraping"""
    print("\n" + "="*60)
    print("Example 1: Basic URL Scraping")
    print("="*60)
    
    # Initialize scraper
    scraper = WebScraperService()
    
    try:
        # Scrape a URL
        html = await scraper.scrape_url("https://example.com")
        
        print(f"✅ Successfully scraped {len(html)} bytes")
        print(f"📊 First 200 characters:\n{html[:200]}...")
        
        # Get statistics
        stats = scraper.get_stats()
        print(f"\n📈 Stats: {stats}")
        
    except ScrapingError as e:
        print(f"❌ Scraping failed: {e}")


async def example_2_custom_options():
    """Example 2: Scraping with custom options"""
    print("\n" + "="*60)
    print("Example 2: Scraping with Custom Options")
    print("="*60)
    
    scraper = WebScraperService(
        timeout=45.0,  # Longer timeout
        max_retries=5,  # More retries
        max_content_size=20 * 1024 * 1024  # 20 MB limit
    )
    
    # Custom options
    options = {
        "custom_headers": {
            "X-Custom-Header": "MyApp/1.0",
            "Referer": "https://google.com"
        },
        "verify_ssl": True,
        "skip_delay": False  # Respect rate limiting
    }
    
    try:
        html = await scraper.scrape_url("https://example.com", options)
        print(f"✅ Scraped with custom options: {len(html)} bytes")
        
    except ScrapingError as e:
        print(f"❌ Error: {e}")


async def example_3_error_handling():
    """Example 3: Error handling and retries"""
    print("\n" + "="*60)
    print("Example 3: Error Handling")
    print("="*60)
    
    scraper = WebScraperService(max_retries=2)
    
    test_urls = [
        "https://example.com",           # Valid URL
        "https://httpstat.us/404",       # 404 error
        "https://httpstat.us/500",       # 500 error
        "javascript:alert('xss')",       # Invalid URL
    ]
    
    for url in test_urls:
        try:
            print(f"\n🔍 Testing: {url}")
            html = await scraper.scrape_url(url)
            print(f"✅ Success: {len(html)} bytes")
            
        except ScrapingError as e:
            print(f"❌ Failed: {e}")


async def example_4_user_agent_rotation():
    """Example 4: User-Agent rotation demonstration"""
    print("\n" + "="*60)
    print("Example 4: User-Agent Rotation")
    print("="*60)
    
    scraper = WebScraperService()
    
    print(f"📋 User-Agent Pool Size: {len(scraper.USER_AGENTS)}")
    print(f"\n🔄 Making 5 requests to see rotation:")
    
    for i in range(5):
        headers = scraper._get_headers()
        print(f"\nRequest {i+1}:")
        print(f"  User-Agent: {headers['User-Agent'][:80]}...")


async def example_5_rate_limiting():
    """Example 5: Rate limiting in action"""
    print("\n" + "="*60)
    print("Example 5: Rate Limiting")
    print("="*60)
    
    scraper = WebScraperService()
    
    print(f"⏱️  Min delay: {scraper.MIN_REQUEST_DELAY}s")
    print(f"⏱️  Max delay: {scraper.MAX_REQUEST_DELAY}s")
    
    import time
    start = time.time()
    
    # Make 3 requests (should have delays between them)
    for i in range(3):
        await scraper._apply_rate_limit()
        print(f"Request {i+1} at {time.time() - start:.2f}s")
    
    total_time = time.time() - start
    print(f"\n⏱️  Total time: {total_time:.2f}s")


async def example_6_content_validation():
    """Example 6: Content type and size validation"""
    print("\n" + "="*60)
    print("Example 6: Content Validation")
    print("="*60)
    
    scraper = WebScraperService(max_content_size=1024 * 1024)  # 1 MB limit
    
    print(f"📏 Max content size: {scraper.max_content_size} bytes")
    print(f"✅ Allowed content types: {scraper.ALLOWED_CONTENT_TYPES}")
    
    # Test with different content
    valid_html = "<html><body>Test</body></html>"
    
    try:
        scraper._validate_content(valid_html, "https://example.com")
        print("✅ Valid HTML passed validation")
    except ScrapingError as e:
        print(f"❌ Validation failed: {e}")
    
    # Test empty content
    try:
        scraper._validate_content("", "https://example.com")
        print("✅ Empty content passed (shouldn't happen)")
    except ScrapingError as e:
        print(f"❌ Empty content rejected: {e}")


async def example_7_robots_txt():
    """Example 7: Robots.txt checking"""
    print("\n" + "="*60)
    print("Example 7: Robots.txt Support")
    print("="*60)
    
    checker = RobotsChecker(user_agent="WebContentAnalyzer")
    
    test_urls = [
        "https://www.google.com/search",
        "https://example.com",
    ]
    
    for url in test_urls:
        try:
            can_fetch = await checker.can_fetch(url)
            delay = checker.get_crawl_delay(url)
            
            print(f"\n🔍 URL: {url}")
            print(f"  ✅ Can fetch: {can_fetch}")
            if delay:
                print(f"  ⏱️  Crawl delay: {delay}s")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")


async def example_8_full_service():
    """Example 8: Using the complete ScrapingService"""
    print("\n" + "="*60)
    print("Example 8: Complete Scraping Service")
    print("="*60)
    
    # Initialize service with all features
    service = ScrapingService(
        respect_robots_txt=True,
        max_content_size=10 * 1024 * 1024,
        timeout=30.0
    )
    
    try:
        # Scrape and extract content
        result = await service.scrape_and_extract("https://example.com")
        
        print(f"✅ Successfully scraped and extracted content")
        print(f"\n📄 Results:")
        print(f"  URL: {result['url']}")
        print(f"  Content length: {len(result['content'])} chars")
        print(f"  Title: {result['metadata'].get('title', 'N/A')}")
        print(f"  Links found: {len(result['links'])}")
        print(f"  Images found: {len(result['images'])}")
        print(f"  Content size: {result['scraper_stats']['content_size']} bytes")
        
        # Get service stats
        stats = service.get_scraper_stats()
        print(f"\n📊 Service Stats:")
        print(f"  Total requests: {stats['web_scraper']['total_requests']}")
        print(f"  Robots.txt enabled: {stats['robots_txt_enabled']}")
        print(f"  Robots cache size: {stats['robots_cache_size']}")
        
    except ScrapingError as e:
        print(f"❌ Service error: {e}")


async def example_9_url_validation():
    """Example 9: URL validation and security"""
    print("\n" + "="*60)
    print("Example 9: URL Validation & Security")
    print("="*60)
    
    scraper = WebScraperService()
    
    test_urls = [
        ("https://example.com", True),
        ("http://example.com", True),
        ("javascript:alert('xss')", False),
        ("data:text/html,<script>", False),
        ("file:///etc/passwd", False),
        ("https://localhost/admin", False),
        ("https://192.168.1.1", False),
        ("not-a-valid-url", False),
    ]
    
    print("🔒 Testing URL validation:")
    for url, expected in test_urls:
        result = scraper._validate_url(url)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {url[:50]:<50} -> {result}")


async def example_10_batch_scraping():
    """Example 10: Scraping multiple URLs"""
    print("\n" + "="*60)
    print("Example 10: Batch Scraping")
    print("="*60)
    
    scraper = WebScraperService()
    
    urls = [
        "https://example.com",
        "https://www.iana.org",
        "https://httpbin.org/html",
    ]
    
    results = []
    
    for i, url in enumerate(urls, 1):
        try:
            print(f"\n🔍 [{i}/{len(urls)}] Scraping: {url}")
            html = await scraper.scrape_url(url)
            results.append({
                "url": url,
                "success": True,
                "size": len(html)
            })
            print(f"  ✅ Success: {len(html)} bytes")
            
        except ScrapingError as e:
            results.append({
                "url": url,
                "success": False,
                "error": str(e)
            })
            print(f"  ❌ Failed: {e}")
    
    # Summary
    print(f"\n📊 Batch Summary:")
    successful = sum(1 for r in results if r['success'])
    print(f"  ✅ Successful: {successful}/{len(urls)}")
    print(f"  ❌ Failed: {len(urls) - successful}/{len(urls)}")
    
    stats = scraper.get_stats()
    print(f"  📈 Total requests made: {stats['total_requests']}")


async def main():
    """Run all examples"""
    print("\n" + "🕷️" * 30)
    print("WEB SCRAPER SERVICE - USAGE EXAMPLES")
    print("🕷️" * 30)
    
    examples = [
        example_1_basic_scraping,
        example_2_custom_options,
        example_3_error_handling,
        example_4_user_agent_rotation,
        example_5_rate_limiting,
        example_6_content_validation,
        example_7_robots_txt,
        example_8_full_service,
        example_9_url_validation,
        example_10_batch_scraping,
    ]
    
    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"\n❌ Example failed: {e}")
            logger.exception("Example error")
        
        # Small delay between examples
        await asyncio.sleep(1)
    
    print("\n" + "="*60)
    print("🎉 All examples completed!")
    print("="*60)


if __name__ == "__main__":
    # Run all examples
    asyncio.run(main())

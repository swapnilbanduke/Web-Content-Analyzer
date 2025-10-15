"""
Content Extraction Engine - Usage Examples
Demonstrates various content extraction capabilities
"""
import asyncio
from bs4 import BeautifulSoup

from src.processors.content_processor import ContentProcessor
from src.scrapers.content_extractor import ContentExtractor
from src.scrapers.metadata_extractor import MetadataExtractor
from src.scrapers.structured_data_extractor import StructuredDataExtractor
from src.scrapers.media_extractor import MediaExtractor
from src.scrapers.cms_detector import CMSDetector


# Sample HTML for demonstration
BLOG_POST_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>How to Build a Web Scraper - Tech Blog</title>
    <meta name="description" content="Learn how to build a robust web scraper with Python">
    <meta name="author" content="Jane Developer">
    <meta property="og:title" content="How to Build a Web Scraper">
    <meta property="og:description" content="Complete guide to web scraping">
    <meta property="og:image" content="https://blog.example.com/scraper-guide.jpg">
    <meta name="twitter:card" content="summary_large_image">
    
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": "How to Build a Web Scraper",
        "author": {
            "@type": "Person",
            "name": "Jane Developer"
        },
        "datePublished": "2024-01-15",
        "image": "https://blog.example.com/scraper-guide.jpg"
    }
    </script>
</head>
<body>
    <header>
        <nav>
            <a href="/">Home</a>
            <a href="/blog">Blog</a>
            <a href="/about">About</a>
        </nav>
    </header>
    
    <main>
        <article>
            <h1>How to Build a Web Scraper</h1>
            <p class="meta">By Jane Developer | January 15, 2024</p>
            
            <figure>
                <img src="/images/scraper-diagram.png" alt="Web scraper architecture diagram" width="800" height="600">
                <figcaption>Figure 1: Web scraper architecture</figcaption>
            </figure>
            
            <p>Web scraping is a powerful technique for extracting data from websites. In this comprehensive guide, 
            we'll explore how to build a robust, production-ready web scraper using Python.</p>
            
            <h2>Why Web Scraping?</h2>
            <p>Web scraping enables you to automate data collection from websites, saving countless hours of manual work. 
            Common use cases include price monitoring, content aggregation, and market research.</p>
            
            <h2>Core Components</h2>
            <p>A good web scraper consists of several key components:</p>
            <ul>
                <li>HTTP client for making requests</li>
                <li>HTML parser for extracting data</li>
                <li>Rate limiting to be respectful</li>
                <li>Error handling for robustness</li>
            </ul>
            
            <h2>Best Practices</h2>
            <p>Always respect robots.txt, implement proper rate limiting, and use appropriate user agents. 
            Your scraper should be a good citizen of the web.</p>
            
            <figure>
                <img src="/images/code-example.png" alt="Python code example">
                <figcaption>Figure 2: Example scraper code</figcaption>
            </figure>
        </article>
    </main>
    
    <aside class="sidebar">
        <h3>Related Posts</h3>
        <ul>
            <li><a href="/post/1">Introduction to Python</a></li>
            <li><a href="/post/2">API Development</a></li>
        </ul>
        <div class="advertisement">
            <p>Advertisement: Buy our course!</p>
        </div>
    </aside>
    
    <footer>
        <p>© 2024 Tech Blog. All rights reserved.</p>
    </footer>
</body>
</html>
"""


def example_1_basic_extraction():
    """Example 1: Basic content extraction"""
    print("\n" + "="*70)
    print("Example 1: Basic Content Extraction")
    print("="*70)
    
    extractor = ContentExtractor()
    result = extractor.extract(BLOG_POST_HTML, "https://blog.example.com/scraper-guide")
    
    print(f"\n📄 Title: {result['metadata']['title']}")
    print(f"📊 Word Count: {result['text_stats']['word_count']}")
    print(f"📏 Characters: {result['text_stats']['character_count']}")
    print(f"\n📝 Content Preview:")
    print(result['main_content'][:300] + "...")
    
    print(f"\n📋 Headings Found:")
    for heading in result['headings'][:5]:
        indent = "  " * (heading['level'] - 1)
        print(f"{indent}H{heading['level']}: {heading['text']}")


def example_2_metadata_extraction():
    """Example 2: Comprehensive metadata extraction"""
    print("\n" + "="*70)
    print("Example 2: Comprehensive Metadata Extraction")
    print("="*70)
    
    soup = BeautifulSoup(BLOG_POST_HTML, 'html.parser')
    extractor = MetadataExtractor()
    metadata = extractor.extract(soup, "https://blog.example.com/scraper-guide")
    
    print(f"\n📄 Basic Metadata:")
    print(f"  Title: {metadata.get('title')}")
    print(f"  Description: {metadata.get('description')}")
    print(f"  Author: {metadata.get('author')}")
    print(f"  Language: {metadata.get('language')}")
    
    if 'open_graph' in metadata:
        print(f"\n🌐 Open Graph Data:")
        og = metadata['open_graph']
        print(f"  OG Title: {og.get('title')}")
        print(f"  OG Description: {og.get('description')}")
        print(f"  OG Image: {og.get('image')}")
    
    if 'twitter_card' in metadata:
        print(f"\n🐦 Twitter Card Data:")
        twitter = metadata['twitter_card']
        print(f"  Card Type: {twitter.get('card')}")


def example_3_structured_data():
    """Example 3: Structured data extraction"""
    print("\n" + "="*70)
    print("Example 3: Structured Data Extraction (JSON-LD, Microdata)")
    print("="*70)
    
    soup = BeautifulSoup(BLOG_POST_HTML, 'html.parser')
    extractor = StructuredDataExtractor()
    data = extractor.extract(soup)
    
    if 'json_ld' in data and data['json_ld']:
        print(f"\n📊 JSON-LD Found: {len(data['json_ld'])} item(s)")
        
        for idx, item in enumerate(data['json_ld'], 1):
            print(f"\n  Item {idx}:")
            print(f"    Type: {item.get('@type')}")
            print(f"    Headline: {item.get('headline')}")
            if 'author' in item:
                author = item['author']
                if isinstance(author, dict):
                    print(f"    Author: {author.get('name')}")
            print(f"    Published: {item.get('datePublished')}")
    
    if 'schema_types' in data:
        print(f"\n🏷️  Schema Types Detected: {', '.join(data['schema_types'])}")
    
    # Extract article-specific data
    article_data = extractor.extract_article_data(data)
    if article_data:
        print(f"\n📰 Normalized Article Data:")
        print(f"  Headline: {article_data.get('headline')}")
        print(f"  Author: {article_data.get('author')}")
        print(f"  Published: {article_data.get('datePublished')}")


def example_4_media_extraction():
    """Example 4: Media content extraction"""
    print("\n" + "="*70)
    print("Example 4: Media Content Extraction")
    print("="*70)
    
    soup = BeautifulSoup(BLOG_POST_HTML, 'html.parser')
    extractor = MediaExtractor()
    media = extractor.extract(soup, "https://blog.example.com/scraper-guide")
    
    print(f"\n📸 Images Found: {len(media['images'])}")
    for idx, img in enumerate(media['images'], 1):
        print(f"\n  Image {idx}:")
        print(f"    URL: {img['src']}")
        print(f"    Alt: {img['alt']}")
        if img.get('width'):
            print(f"    Dimensions: {img['width']}x{img['height']}")
        if 'caption' in img:
            print(f"    Caption: {img['caption']}")
    
    if media['videos']:
        print(f"\n🎥 Videos Found: {len(media['videos'])}")
    
    if media['embeds']:
        print(f"\n🎬 Embeds Found: {len(media['embeds'])}")


def example_5_cms_detection():
    """Example 5: CMS detection"""
    print("\n" + "="*70)
    print("Example 5: CMS Detection and Optimization")
    print("="*70)
    
    wordpress_html = """
    <html>
    <head>
        <meta name="generator" content="WordPress 6.0">
    </head>
    <body class="wordpress">
        <article class="post">
            <h1 class="entry-title">WordPress Post</h1>
            <div class="entry-content">
                <p>This is WordPress content.</p>
            </div>
        </article>
        <link rel="stylesheet" href="/wp-content/themes/theme/style.css">
    </body>
    </html>
    """
    
    soup = BeautifulSoup(wordpress_html, 'html.parser')
    detector = CMSDetector()
    result = detector.detect(soup, "https://example.com")
    
    print(f"\n🔍 CMS Detection Results:")
    print(f"  Detected CMS: {result['cms']}")
    print(f"  Confidence: {result['confidence']:.2%}")
    
    if result['cms']:
        print(f"\n⚙️  CMS Features:")
        features = detector.get_cms_features(result['cms'])
        print(f"  Type: {features.get('type')}")
        print(f"  Typical Use: {features.get('typical_use')}")
        print(f"  SEO Friendly: {features.get('seo_friendly')}")
        
        # Get optimized selectors
        selectors = detector.get_optimal_selectors(result['cms'], 'content')
        print(f"\n🎯 Optimized Content Selectors:")
        for selector in selectors[:3]:
            print(f"  - {selector}")


def example_6_full_processing():
    """Example 6: Complete processing pipeline"""
    print("\n" + "="*70)
    print("Example 6: Complete Processing Pipeline")
    print("="*70)
    
    processor = ContentProcessor()
    
    # Process with all features enabled
    result = processor.process(
        BLOG_POST_HTML,
        url="https://blog.example.com/scraper-guide",
        extract_metadata=True,
        extract_structured_data=True,
        extract_media=True,
        detect_cms=True
    )
    
    print(f"\n📊 Processing Summary:")
    summary = result['processing_summary']
    print(f"  Content Length: {summary['total_content_length']} chars")
    print(f"  Word Count: {summary['word_count']} words")
    print(f"  Metadata Fields: {summary['metadata_fields']}")
    print(f"  Structured Data: {summary['has_structured_data']}")
    print(f"  Extraction Method: {result['extraction_method']}")
    
    if 'media' in result:
        print(f"\n📸 Media Summary:")
        counts = result['media']['counts']
        print(f"  Images: {counts['images']}")
        print(f"  Videos: {counts['videos']}")
        print(f"  Embeds: {counts['embeds']}")
    
    # Get concise summary
    content_summary = processor.extract_content_summary(result)
    
    print(f"\n📝 Content Summary:")
    print(f"  Title: {content_summary['title']}")
    print(f"  Word Count: {content_summary['word_count']}")
    print(f"  Has Images: {content_summary['has_images']}")
    print(f"  Schema Types: {content_summary['schema_types']}")


def example_7_extraction_comparison():
    """Example 7: Compare extraction methods"""
    print("\n" + "="*70)
    print("Example 7: Extraction Method Comparison")
    print("="*70)
    
    processor = ContentProcessor()
    comparisons = processor.compare_extractions(
        BLOG_POST_HTML,
        "https://blog.example.com/scraper-guide"
    )
    
    print(f"\n🔬 Extraction Methods Comparison:")
    
    for method, data in comparisons.items():
        print(f"\n  {method.upper()}:")
        print(f"    Content Length: {data['content_length']} chars")
        print(f"    Word Count: {data['word_count']} words")
        print(f"    Preview: {data['preview'][:80]}...")


def example_8_selective_extraction():
    """Example 8: Selective feature extraction"""
    print("\n" + "="*70)
    print("Example 8: Selective Feature Extraction")
    print("="*70)
    
    processor = ContentProcessor()
    
    print("\n  Scenario 1: Content + Metadata only (fast)")
    result1 = processor.process(
        BLOG_POST_HTML,
        url="https://blog.example.com/scraper-guide",
        extract_metadata=True,
        extract_structured_data=False,
        extract_media=False,
        detect_cms=False
    )
    print(f"    Word Count: {result1['text_stats']['word_count']}")
    print(f"    Title: {result1['metadata']['title']}")
    
    print("\n  Scenario 2: Structured data focus")
    result2 = processor.process(
        BLOG_POST_HTML,
        url="https://blog.example.com/scraper-guide",
        extract_structured_data=True,
        extract_media=False
    )
    if 'article_data' in result2:
        print(f"    Article Headline: {result2['article_data']['headline']}")
        print(f"    Article Author: {result2['article_data']['author']}")
    
    print("\n  Scenario 3: Media focus")
    result3 = processor.process(
        BLOG_POST_HTML,
        url="https://blog.example.com/scraper-guide",
        extract_media=True,
        extract_structured_data=False
    )
    print(f"    Images Found: {result3['media']['counts']['images']}")


def main():
    """Run all examples"""
    print("\n" + "🔍" * 35)
    print("CONTENT EXTRACTION ENGINE - USAGE EXAMPLES")
    print("🔍" * 35)
    
    examples = [
        example_1_basic_extraction,
        example_2_metadata_extraction,
        example_3_structured_data,
        example_4_media_extraction,
        example_5_cms_detection,
        example_6_full_processing,
        example_7_extraction_comparison,
        example_8_selective_extraction,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n❌ Example failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("🎉 All examples completed!")
    print("="*70)


if __name__ == "__main__":
    main()

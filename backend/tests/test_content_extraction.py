"""
Comprehensive tests for content extraction engine
Tests main content identification, metadata extraction, structured data, and media extraction
"""
import pytest
from bs4 import BeautifulSoup

from src.scrapers.content_extractor import ContentExtractor
from src.scrapers.metadata_extractor import MetadataExtractor
from src.scrapers.structured_data_extractor import StructuredDataExtractor
from src.scrapers.media_extractor import MediaExtractor
from src.scrapers.cms_detector import CMSDetector
from src.processors.content_processor import ContentProcessor


# Sample HTML for testing
SIMPLE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Test Article</title>
    <meta name="description" content="This is a test article description">
    <meta name="keywords" content="test, article, content">
    <meta name="author" content="John Doe">
</head>
<body>
    <header>
        <nav>
            <a href="/home">Home</a>
            <a href="/about">About</a>
        </nav>
    </header>
    <main>
        <article>
            <h1>Main Article Title</h1>
            <p>This is the first paragraph of the main content.</p>
            <p>This is the second paragraph with more detailed information.</p>
            <p>And this is the third paragraph to ensure we have enough content.</p>
        </article>
    </main>
    <footer>
        <p>Copyright 2024</p>
    </footer>
</body>
</html>
"""

WORDPRESS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="generator" content="WordPress 6.0">
    <title>WordPress Blog Post</title>
</head>
<body class="wordpress">
    <article class="post">
        <h1 class="entry-title">WordPress Article</h1>
        <div class="entry-content">
            <p>This is WordPress content.</p>
        </div>
    </article>
    <link rel="stylesheet" href="/wp-content/themes/default/style.css">
</body>
</html>
"""

STRUCTURED_DATA_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Article with Structured Data</title>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Test Article",
        "author": {
            "@type": "Person",
            "name": "Jane Smith"
        },
        "datePublished": "2024-01-01",
        "image": "https://example.com/image.jpg"
    }
    </script>
</head>
<body>
    <article itemscope itemtype="https://schema.org/BlogPosting">
        <h1 itemprop="headline">Microdata Article</h1>
        <meta itemprop="datePublished" content="2024-01-01">
        <div itemprop="articleBody">
            <p>Article content here.</p>
        </div>
    </article>
</body>
</html>
"""

MEDIA_HTML = """
<!DOCTYPE html>
<html>
<head><title>Media Test</title></head>
<body>
    <img src="/image1.jpg" alt="Test Image" width="800" height="600">
    <figure>
        <img src="/image2.png" alt="Figure Image">
        <figcaption>This is a caption</figcaption>
    </figure>
    <picture>
        <source srcset="/image-large.webp" media="(min-width: 800px)" type="image/webp">
        <source srcset="/image-small.webp" media="(max-width: 799px)" type="image/webp">
        <img src="/image-fallback.jpg" alt="Responsive Image">
    </picture>
    <video controls poster="/poster.jpg">
        <source src="/video.mp4" type="video/mp4">
        <source src="/video.webm" type="video/webm">
        <track src="/captions.vtt" kind="captions" srclang="en" label="English">
    </video>
    <iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ" width="560" height="315"></iframe>
</body>
</html>
"""

OPEN_GRAPH_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Open Graph Test</title>
    <meta property="og:title" content="OG Title">
    <meta property="og:description" content="OG Description">
    <meta property="og:image" content="https://example.com/og-image.jpg">
    <meta property="og:url" content="https://example.com/page">
    <meta property="og:type" content="article">
    <meta property="article:author" content="Author Name">
    <meta property="article:published_time" content="2024-01-01T10:00:00Z">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@example">
</head>
<body>
    <p>Content</p>
</body>
</html>
"""


class TestContentExtractor:
    """Test ContentExtractor class"""
    
    def test_extract_main_content(self):
        """Test main content extraction"""
        extractor = ContentExtractor()
        result = extractor.extract(SIMPLE_HTML, "https://example.com")
        
        assert result['main_content']
        assert 'first paragraph' in result['main_content']
        assert 'second paragraph' in result['main_content']
        assert 'Home' not in result['main_content']  # Navigation removed
        assert 'Copyright' not in result['main_content']  # Footer removed
    
    def test_semantic_content_extraction(self):
        """Test extraction using semantic HTML tags"""
        extractor = ContentExtractor()
        soup = BeautifulSoup(SIMPLE_HTML, 'html.parser')
        
        main_content, html_content = extractor._extract_main_content(soup)
        
        assert main_content
        assert len(main_content) > 50
    
    def test_content_scoring(self):
        """Test content block scoring algorithm"""
        extractor = ContentExtractor()
        soup = BeautifulSoup(SIMPLE_HTML, 'html.parser')
        
        # Remove boilerplate
        extractor._remove_boilerplate_elements(soup)
        
        # Score blocks
        scored_blocks = extractor._score_content_blocks(soup)
        
        assert len(scored_blocks) > 0
        assert all(isinstance(score, float) for _, score in scored_blocks)
    
    def test_metadata_extraction(self):
        """Test basic metadata extraction"""
        extractor = ContentExtractor()
        result = extractor.extract(SIMPLE_HTML, "https://example.com")
        
        metadata = result['metadata']
        
        assert metadata['title'] == 'Test Article'
        assert metadata['description'] == 'This is a test article description'
        assert metadata['keywords'] == 'test, article, content'
        assert metadata['author'] == 'John Doe'
    
    def test_headings_extraction(self):
        """Test headings extraction"""
        extractor = ContentExtractor()
        result = extractor.extract(SIMPLE_HTML, "https://example.com")
        
        headings = result['headings']
        
        assert len(headings) > 0
        assert headings[0]['text'] == 'Main Article Title'
        assert headings[0]['level'] == 1
    
    def test_text_statistics(self):
        """Test text statistics calculation"""
        extractor = ContentExtractor()
        result = extractor.extract(SIMPLE_HTML, "https://example.com")
        
        stats = result['text_stats']
        
        assert stats['character_count'] > 0
        assert stats['word_count'] > 0
        assert stats['paragraph_count'] >= 3


class TestMetadataExtractor:
    """Test MetadataExtractor class"""
    
    def test_basic_metadata(self):
        """Test basic HTML metadata extraction"""
        extractor = MetadataExtractor()
        soup = BeautifulSoup(SIMPLE_HTML, 'html.parser')
        
        metadata = extractor.extract(soup, "https://example.com")
        
        assert metadata['title'] == 'Test Article'
        assert metadata['description'] == 'This is a test article description'
        assert metadata['author'] == 'John Doe'
    
    def test_open_graph_extraction(self):
        """Test Open Graph metadata extraction"""
        extractor = MetadataExtractor()
        soup = BeautifulSoup(OPEN_GRAPH_HTML, 'html.parser')
        
        metadata = extractor.extract(soup, "https://example.com")
        
        assert 'open_graph' in metadata
        og_data = metadata['open_graph']
        
        assert og_data['title'] == 'OG Title'
        assert og_data['description'] == 'OG Description'
        assert og_data['image'] == 'https://example.com/og-image.jpg'
        assert og_data['type'] == 'article'
    
    def test_twitter_card_extraction(self):
        """Test Twitter Card metadata extraction"""
        extractor = MetadataExtractor()
        soup = BeautifulSoup(OPEN_GRAPH_HTML, 'html.parser')
        
        metadata = extractor.extract(soup, "https://example.com")
        
        assert 'twitter_card' in metadata
        twitter_data = metadata['twitter_card']
        
        assert twitter_data['card'] == 'summary_large_image'
        assert twitter_data['site'] == '@example'
    
    def test_article_metadata(self):
        """Test article-specific metadata"""
        extractor = MetadataExtractor()
        soup = BeautifulSoup(OPEN_GRAPH_HTML, 'html.parser')
        
        metadata = extractor.extract(soup, "https://example.com")
        
        assert 'article' in metadata
        article_data = metadata['article']
        
        assert article_data['author'] == 'Author Name'
        assert article_data['published_time'] == '2024-01-01T10:00:00Z'


class TestStructuredDataExtractor:
    """Test StructuredDataExtractor class"""
    
    def test_json_ld_extraction(self):
        """Test JSON-LD extraction"""
        extractor = StructuredDataExtractor()
        soup = BeautifulSoup(STRUCTURED_DATA_HTML, 'html.parser')
        
        data = extractor.extract(soup)
        
        assert 'json_ld' in data
        assert len(data['json_ld']) > 0
        
        article = data['json_ld'][0]
        assert article['@type'] == 'Article'
        assert article['headline'] == 'Test Article'
        assert article['author']['name'] == 'Jane Smith'
    
    def test_microdata_extraction(self):
        """Test Microdata extraction"""
        extractor = StructuredDataExtractor()
        soup = BeautifulSoup(STRUCTURED_DATA_HTML, 'html.parser')
        
        data = extractor.extract(soup)
        
        assert 'microdata' in data
        assert len(data['microdata']) > 0
        
        item = data['microdata'][0]
        assert item['@type'] == 'BlogPosting'
        assert item['headline'] == 'Microdata Article'
    
    def test_schema_type_identification(self):
        """Test schema type identification"""
        extractor = StructuredDataExtractor()
        soup = BeautifulSoup(STRUCTURED_DATA_HTML, 'html.parser')
        
        data = extractor.extract(soup)
        
        assert 'schema_types' in data
        assert 'Article' in data['schema_types']
    
    def test_article_data_normalization(self):
        """Test article data normalization"""
        extractor = StructuredDataExtractor()
        soup = BeautifulSoup(STRUCTURED_DATA_HTML, 'html.parser')
        
        data = extractor.extract(soup)
        article_data = extractor.extract_article_data(data)
        
        assert article_data is not None
        assert article_data['type'] == 'Article'
        assert article_data['headline'] == 'Test Article'
        assert article_data['author']['name'] == 'Jane Smith'


class TestMediaExtractor:
    """Test MediaExtractor class"""
    
    def test_image_extraction(self):
        """Test basic image extraction"""
        extractor = MediaExtractor()
        soup = BeautifulSoup(MEDIA_HTML, 'html.parser')
        
        images = extractor.extract_images(soup, "https://example.com")
        
        assert len(images) >= 2
        
        # Check first image
        img1 = images[0]
        assert 'example.com/image1.jpg' in img1['src']
        assert img1['alt'] == 'Test Image'
        assert img1['width'] == '800'
        assert img1['height'] == '600'
    
    def test_figure_caption_extraction(self):
        """Test figure with caption extraction"""
        extractor = MediaExtractor()
        soup = BeautifulSoup(MEDIA_HTML, 'html.parser')
        
        images = extractor.extract_images(soup, "https://example.com")
        
        # Find image with caption
        captioned_img = next((img for img in images if 'caption' in img), None)
        
        assert captioned_img is not None
        assert captioned_img['caption'] == 'This is a caption'
    
    def test_picture_element_extraction(self):
        """Test picture element extraction"""
        extractor = MediaExtractor()
        soup = BeautifulSoup(MEDIA_HTML, 'html.parser')
        
        images = extractor.extract_images(soup, "https://example.com")
        
        # Find picture element
        picture_img = next((img for img in images if img.get('type') == 'picture'), None)
        
        assert picture_img is not None
        assert 'sources' in picture_img
        assert len(picture_img['sources']) >= 2
    
    def test_video_extraction(self):
        """Test video extraction"""
        extractor = MediaExtractor()
        soup = BeautifulSoup(MEDIA_HTML, 'html.parser')
        
        videos = extractor.extract_videos(soup, "https://example.com")
        
        assert len(videos) > 0
        
        video = videos[0]
        assert 'example.com/poster.jpg' in video['poster']
        assert video['controls'] is True
        assert len(video['sources']) >= 2
        assert len(video['tracks']) > 0
    
    def test_youtube_embed_extraction(self):
        """Test YouTube embed extraction"""
        extractor = MediaExtractor()
        soup = BeautifulSoup(MEDIA_HTML, 'html.parser')
        
        embeds = extractor.extract_embeds(soup, "https://example.com")
        
        assert len(embeds) > 0
        
        youtube_embed = embeds[0]
        assert youtube_embed['embed_type'] == 'video'
        assert youtube_embed['platform'] == 'YouTube'
        assert youtube_embed['video_id'] == 'dQw4w9WgXcQ'


class TestCMSDetector:
    """Test CMSDetector class"""
    
    def test_wordpress_detection(self):
        """Test WordPress detection"""
        detector = CMSDetector()
        soup = BeautifulSoup(WORDPRESS_HTML, 'html.parser')
        
        result = detector.detect(soup, "https://example.com")
        
        assert result['cms'] == 'WordPress'
        assert result['confidence'] > 0.5
    
    def test_cms_selectors(self):
        """Test CMS-specific selectors"""
        detector = CMSDetector()
        
        selectors = detector.get_optimal_selectors('WordPress', 'content')
        
        assert len(selectors) > 0
        assert '.entry-content' in selectors
    
    def test_cms_content_extraction(self):
        """Test content extraction with CMS selectors"""
        detector = CMSDetector()
        soup = BeautifulSoup(WORDPRESS_HTML, 'html.parser')
        
        content = detector.extract_with_cms_selectors(soup, 'WordPress', 'content')
        
        assert content is not None
        assert 'WordPress content' in content


class TestContentProcessor:
    """Test ContentProcessor integration"""
    
    def test_full_processing(self):
        """Test complete content processing"""
        processor = ContentProcessor()
        
        result = processor.process(SIMPLE_HTML, "https://example.com")
        
        assert result['url'] == "https://example.com"
        assert result['main_content']
        assert 'metadata' in result
        assert 'text_stats' in result
        assert 'processing_summary' in result
    
    def test_processing_with_all_features(self):
        """Test processing with all features enabled"""
        processor = ContentProcessor()
        
        result = processor.process(
            STRUCTURED_DATA_HTML,
            "https://example.com",
            extract_metadata=True,
            extract_structured_data=True,
            extract_media=True,
            detect_cms=True
        )
        
        assert 'metadata' in result
        assert 'structured_data' in result
        assert 'media' in result
    
    def test_cms_optimized_extraction(self):
        """Test CMS-optimized extraction"""
        processor = ContentProcessor()
        
        result = processor.process(WORDPRESS_HTML, "https://example.com")
        
        assert 'cms' in result
        assert result['cms']['detected'] == 'WordPress'
        assert result['extraction_method'] in ['cms_optimized', 'algorithm']
    
    def test_content_summary_generation(self):
        """Test content summary generation"""
        processor = ContentProcessor()
        
        result = processor.process(SIMPLE_HTML, "https://example.com")
        summary = processor.extract_content_summary(result)
        
        assert summary['url'] == "https://example.com"
        assert summary['title'] == 'Test Article'
        assert summary['word_count'] > 0
        assert 'content_preview' in summary
    
    def test_extraction_comparison(self):
        """Test extraction method comparison"""
        processor = ContentProcessor()
        
        comparisons = processor.compare_extractions(SIMPLE_HTML, "https://example.com")
        
        assert 'algorithm' in comparisons
        assert comparisons['algorithm']['content_length'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

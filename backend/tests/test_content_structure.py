"""
Tests for Content Structure Analyzer

Comprehensive tests for all structure analysis components.
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from src.analyzers.content_structure_analyzer import (
    Heading,
    Section,
    DocumentOutline,
    HeadingHierarchyDetector,
    SectionIdentifier,
    ContentTypeClassifier,
    KeyPhraseExtractor,
    ContentStructureAnalyzer
)


# ============================================================================
# Heading Tests
# ============================================================================

class TestHeading:
    """Test Heading data class"""
    
    def test_heading_creation(self):
        """Test creating a heading"""
        heading = Heading(level=1, text="Introduction", id="intro", position=0)
        assert heading.level == 1
        assert heading.text == "Introduction"
        assert heading.id == "intro"
        assert heading.position == 0
        assert heading.parent is None
        assert len(heading.children) == 0
    
    def test_heading_hierarchy(self):
        """Test heading parent-child relationships"""
        h1 = Heading(level=1, text="Chapter 1", position=0)
        h2 = Heading(level=2, text="Section 1.1", position=1)
        h2.parent = h1
        h1.children.append(h2)
        
        assert h2.parent == h1
        assert h1.children[0] == h2
    
    def test_heading_to_dict(self):
        """Test converting heading to dictionary"""
        h1 = Heading(level=1, text="Main", position=0)
        h2 = Heading(level=2, text="Sub", position=1)
        h1.children.append(h2)
        
        result = h1.to_dict()
        assert result['level'] == 1
        assert result['text'] == "Main"
        assert len(result['children']) == 1
        assert result['children'][0]['text'] == "Sub"


# ============================================================================
# Heading Hierarchy Detector Tests
# ============================================================================

class TestHeadingHierarchyDetector:
    """Test HeadingHierarchyDetector class"""
    
    def test_detect_from_html_simple(self):
        """Test detecting headings from simple HTML"""
        detector = HeadingHierarchyDetector()
        html = """
        <h1>Main Title</h1>
        <h2>Subtitle</h2>
        <h2>Another Subtitle</h2>
        """
        headings = detector.detect_from_html(html)
        
        assert len(headings) == 3
        assert headings[0].level == 1
        assert headings[0].text == "Main Title"
        assert headings[1].level == 2
        assert headings[2].level == 2
    
    def test_detect_from_html_hierarchy(self):
        """Test building heading hierarchy from HTML"""
        detector = HeadingHierarchyDetector()
        html = """
        <h1>Chapter 1</h1>
        <h2>Section 1.1</h2>
        <h3>Subsection 1.1.1</h3>
        <h2>Section 1.2</h2>
        """
        headings = detector.detect_from_html(html)
        
        assert len(headings) == 4
        # Check hierarchy
        h1 = headings[0]
        assert len(h1.children) == 2
        assert h1.children[0].text == "Section 1.1"
        assert len(h1.children[0].children) == 1
        assert h1.children[0].children[0].text == "Subsection 1.1.1"
    
    def test_detect_from_html_with_ids(self):
        """Test detecting headings with IDs"""
        detector = HeadingHierarchyDetector()
        html = '<h1 id="intro">Introduction</h1><h2 id="background">Background</h2>'
        headings = detector.detect_from_html(html)
        
        assert headings[0].id == "intro"
        assert headings[1].id == "background"
    
    def test_detect_from_html_empty(self):
        """Test with no headings"""
        detector = HeadingHierarchyDetector()
        html = "<p>No headings here</p>"
        headings = detector.detect_from_html(html)
        
        assert len(headings) == 0
    
    def test_detect_from_markdown(self):
        """Test detecting headings from Markdown"""
        detector = HeadingHierarchyDetector()
        markdown = """
# Main Title
## Subtitle 1
### Sub-subtitle
## Subtitle 2
        """
        headings = detector.detect_from_markdown(markdown)
        
        assert len(headings) == 4
        assert headings[0].level == 1
        assert headings[1].level == 2
        assert headings[2].level == 3
        assert headings[3].level == 2
    
    def test_markdown_hierarchy(self):
        """Test Markdown heading hierarchy"""
        detector = HeadingHierarchyDetector()
        markdown = """
# Chapter 1
## Section 1.1
## Section 1.2
# Chapter 2
        """
        headings = detector.detect_from_markdown(markdown)
        
        h1 = headings[0]
        assert len(h1.children) == 2
        assert h1.children[0].text == "Section 1.1"
    
    def test_get_hierarchy_depth(self):
        """Test calculating hierarchy depth"""
        detector = HeadingHierarchyDetector()
        html = """
        <h1>Level 1</h1>
        <h2>Level 2</h2>
        <h3>Level 3</h3>
        <h4>Level 4</h4>
        """
        headings = detector.detect_from_html(html)
        depth = detector.get_hierarchy_depth(headings)
        
        assert depth == 4
    
    def test_get_heading_distribution(self):
        """Test heading distribution"""
        detector = HeadingHierarchyDetector()
        html = """
        <h1>Title</h1>
        <h2>Subtitle 1</h2>
        <h2>Subtitle 2</h2>
        <h3>Sub</h3>
        """
        headings = detector.detect_from_html(html)
        distribution = detector.get_heading_distribution(headings)
        
        assert distribution[1] == 1
        assert distribution[2] == 2
        assert distribution[3] == 1
        assert distribution[4] == 0


# ============================================================================
# Section Identifier Tests
# ============================================================================

class TestSectionIdentifier:
    """Test SectionIdentifier class"""
    
    def test_identify_sections_simple(self):
        """Test identifying simple sections"""
        identifier = SectionIdentifier()
        detector = HeadingHierarchyDetector()
        
        html = """
        <h1>Introduction</h1>
        <p>This is the introduction section.</p>
        <h1>Conclusion</h1>
        <p>This is the conclusion section.</p>
        """
        headings = detector.detect_from_html(html)
        sections = identifier.identify_sections(html, headings)
        
        assert len(sections) == 2
        assert sections[0].type == 'introduction'
        assert sections[1].type == 'conclusion'
    
    def test_identify_sections_with_content(self):
        """Test section content extraction"""
        identifier = SectionIdentifier()
        detector = HeadingHierarchyDetector()
        
        html = """
        <h1>Title</h1>
        <p>First paragraph.</p>
        <p>Second paragraph.</p>
        """
        headings = detector.detect_from_html(html)
        sections = identifier.identify_sections(html, headings)
        
        assert len(sections) == 1
        assert "First paragraph" in sections[0].content
        assert "Second paragraph" in sections[0].content
    
    def test_classify_section_type_introduction(self):
        """Test classifying introduction sections"""
        identifier = SectionIdentifier()
        section_type = identifier._classify_section_type("Introduction")
        assert section_type == 'introduction'
    
    def test_classify_section_type_methodology(self):
        """Test classifying methodology sections"""
        identifier = SectionIdentifier()
        section_type = identifier._classify_section_type("Methodology")
        assert section_type == 'methodology'
    
    def test_classify_section_type_default(self):
        """Test default section classification"""
        identifier = SectionIdentifier()
        section_type = identifier._classify_section_type("Random Section")
        assert section_type == 'body'
    
    def test_section_word_count(self):
        """Test section word counting"""
        identifier = SectionIdentifier()
        detector = HeadingHierarchyDetector()
        
        html = """
        <h1>Title</h1>
        <p>One two three four five.</p>
        """
        headings = detector.detect_from_html(html)
        sections = identifier.identify_sections(html, headings)
        
        assert sections[0].word_count == 5
    
    def test_no_headings(self):
        """Test with content but no headings"""
        identifier = SectionIdentifier()
        html = "<p>Content without headings.</p>"
        sections = identifier.identify_sections(html, [])
        
        assert len(sections) == 1
        assert sections[0].type == 'body'
        assert sections[0].heading is None


# ============================================================================
# Content Type Classifier Tests
# ============================================================================

class TestContentTypeClassifier:
    """Test ContentTypeClassifier class"""
    
    def test_classify_blog_post(self):
        """Test classifying blog posts"""
        classifier = ContentTypeClassifier()
        html = """
        <article>
            <time>2024-01-01</time>
            <p>Posted by John Doe</p>
            <p>This is a blog post content.</p>
        </article>
        """
        text = "Posted by John Doe. This is a blog post content."
        result = classifier.classify(html, text)
        
        assert result['primary_type'] == 'blog_post'
        assert result['confidence'] > 0
    
    def test_classify_technical_docs(self):
        """Test classifying technical documentation"""
        classifier = ContentTypeClassifier()
        html = """
        <code>function example() {}</code>
        <pre>api.call()</pre>
        """
        text = "This function takes parameters and returns a class method."
        result = classifier.classify(html, text)
        
        assert result['primary_type'] == 'technical_docs'
    
    def test_classify_news_article(self):
        """Test classifying news articles"""
        classifier = ContentTypeClassifier()
        html = """
        <article>
            <div class="byline">Reporter Name</div>
            <p>UPDATED: Breaking news reported today.</p>
        </article>
        """
        text = "UPDATED: Breaking news reported today by our journalist."
        result = classifier.classify(html, text)
        
        assert result['primary_type'] == 'news_article'
    
    def test_classify_product_page(self):
        """Test classifying product pages"""
        classifier = ContentTypeClassifier()
        html = """
        <div class="price">$99.99</div>
        <button>Add to cart</button>
        """
        text = "Price: $99.99. Buy now and add to cart."
        result = classifier.classify(html, text)
        
        assert result['primary_type'] == 'product_page'
    
    def test_classify_academic_paper(self):
        """Test classifying academic papers"""
        classifier = ContentTypeClassifier()
        html = """
        <abstract>This paper presents...</abstract>
        <section id="methodology">Methodology</section>
        <section id="references">References</section>
        """
        text = "Abstract: methodology, results, conclusion. Smith et al (2023) [1]"
        result = classifier.classify(html, text)
        
        assert result['primary_type'] == 'academic_paper'
    
    def test_classify_general_content(self):
        """Test classifying general content"""
        classifier = ContentTypeClassifier()
        html = "<p>General content without specific indicators.</p>"
        text = "General content without specific indicators."
        result = classifier.classify(html, text)
        
        assert result['primary_type'] == 'general'
    
    def test_scores_included(self):
        """Test that scores are included in results"""
        classifier = ContentTypeClassifier()
        html = "<p>Content</p>"
        text = "Content"
        result = classifier.classify(html, text)
        
        assert 'scores' in result
        assert isinstance(result['scores'], dict)


# ============================================================================
# Key Phrase Extractor Tests
# ============================================================================

class TestKeyPhraseExtractor:
    """Test KeyPhraseExtractor class"""
    
    def test_extract_single_words(self):
        """Test extracting single words"""
        extractor = KeyPhraseExtractor(max_phrases=5)
        text = "machine learning machine learning artificial intelligence"
        headings = []
        
        phrases = extractor.extract_key_phrases(text, headings)
        
        assert len(phrases) > 0
        # "machine" and "learning" should appear
        words = [p['phrase'] for p in phrases if p['type'] == 'word']
        assert 'machine' in words or 'learning' in words
    
    def test_extract_bigrams(self):
        """Test extracting bigrams"""
        extractor = KeyPhraseExtractor(max_phrases=10)
        text = "machine learning artificial intelligence machine learning"
        headings = []
        
        phrases = extractor.extract_key_phrases(text, headings)
        
        bigrams = [p['phrase'] for p in phrases if p['type'] == 'bigram']
        assert 'machine learning' in bigrams
    
    def test_extract_trigrams(self):
        """Test extracting trigrams"""
        extractor = KeyPhraseExtractor(max_phrases=15)
        text = "natural language processing natural language processing"
        headings = []
        
        phrases = extractor.extract_key_phrases(text, headings)
        
        trigrams = [p['phrase'] for p in phrases if p['type'] == 'trigram']
        assert 'natural language processing' in trigrams
    
    def test_heading_boost(self):
        """Test that heading terms get boosted scores"""
        extractor = KeyPhraseExtractor(max_phrases=10)
        text = "machine learning is important. deep learning too."
        headings = [Heading(level=1, text="Machine Learning", position=0)]
        
        phrases = extractor.extract_key_phrases(text, headings)
        
        # Machine should have higher score due to heading
        machine_phrase = next((p for p in phrases if 'machine' in p['phrase']), None)
        assert machine_phrase is not None
        assert machine_phrase['score'] > 0
    
    def test_stop_words_filtered(self):
        """Test that stop words are filtered"""
        extractor = KeyPhraseExtractor(max_phrases=10)
        text = "the quick brown fox jumps over the lazy dog"
        headings = []
        
        phrases = extractor.extract_key_phrases(text, headings)
        
        # Stop words like "the", "over" should not appear
        words = [p['phrase'] for p in phrases]
        assert 'the' not in words
        assert 'over' not in words
    
    def test_max_phrases_limit(self):
        """Test max phrases limit"""
        extractor = KeyPhraseExtractor(max_phrases=5)
        text = " ".join(["word"] * 100)  # Lots of repetition
        headings = []
        
        phrases = extractor.extract_key_phrases(text, headings)
        
        assert len(phrases) <= 5
    
    def test_phrase_scoring(self):
        """Test that phrases have scores"""
        extractor = KeyPhraseExtractor(max_phrases=5)
        text = "artificial intelligence machine learning deep learning"
        headings = []
        
        phrases = extractor.extract_key_phrases(text, headings)
        
        for phrase in phrases:
            assert 'score' in phrase
            assert phrase['score'] > 0


# ============================================================================
# Content Structure Analyzer Tests
# ============================================================================

class TestContentStructureAnalyzer:
    """Test ContentStructureAnalyzer class"""
    
    def test_analyze_simple_html(self):
        """Test analyzing simple HTML"""
        analyzer = ContentStructureAnalyzer()
        html = """
        <h1>Main Title</h1>
        <p>Introduction paragraph.</p>
        <h2>Section 1</h2>
        <p>Section content.</p>
        """
        
        result = analyzer.analyze(html)
        
        assert result['format'] == 'html'
        assert result['outline'] is not None
        assert result['outline']['total_headings'] == 2
    
    def test_analyze_with_all_features(self):
        """Test analysis with all features enabled"""
        analyzer = ContentStructureAnalyzer(
            extract_key_phrases=True,
            classify_content_type=True
        )
        html = """
        <article>
            <h1>Machine Learning Tutorial</h1>
            <p>Machine learning is a subset of artificial intelligence.</p>
            <h2>Introduction</h2>
            <p>Deep learning uses neural networks.</p>
        </article>
        """
        
        result = analyzer.analyze(html)
        
        assert 'outline' in result
        assert 'content_type' in result
        assert 'key_phrases' in result
        assert len(result['key_phrases']) > 0
    
    def test_analyze_markdown(self):
        """Test analyzing Markdown content"""
        analyzer = ContentStructureAnalyzer()
        markdown = """
# Main Title
Introduction text
## Section 1
Section content
        """
        
        result = analyzer.analyze(markdown, content_format='markdown')
        
        assert result['format'] == 'markdown'
        assert result['outline']['total_headings'] == 2
    
    def test_metadata_extraction(self):
        """Test metadata extraction"""
        analyzer = ContentStructureAnalyzer()
        html = """
        <h1>Title</h1>
        <h2>Section 1</h2>
        <h2>Section 2</h2>
        <p>Content here.</p>
        """
        
        result = analyzer.analyze(html)
        
        assert 'metadata' in result
        assert result['metadata']['total_headings'] == 3
        assert result['metadata']['has_clear_structure'] is True
    
    def test_outline_structure(self):
        """Test outline structure"""
        analyzer = ContentStructureAnalyzer()
        html = """
        <h1>Chapter 1</h1>
        <h2>Section 1.1</h2>
        <h3>Subsection 1.1.1</h3>
        """
        
        result = analyzer.analyze(html)
        outline = result['outline']
        
        assert outline['title'] == "Chapter 1"
        assert outline['hierarchy_depth'] == 3
        assert outline['heading_distribution'][1] == 1
        assert outline['heading_distribution'][2] == 1
        assert outline['heading_distribution'][3] == 1
    
    def test_content_type_classification(self):
        """Test content type is classified"""
        analyzer = ContentStructureAnalyzer(classify_content_type=True)
        html = """
        <article>
            <time>2024-01-01</time>
            <p>Posted by author. This is a blog post.</p>
        </article>
        """
        
        result = analyzer.analyze(html)
        
        assert result['content_type'] is not None
        assert 'primary_type' in result['content_type']
    
    def test_key_phrases_extracted(self):
        """Test key phrases are extracted"""
        analyzer = ContentStructureAnalyzer(extract_key_phrases=True, max_key_phrases=10)
        html = """
        <h1>Machine Learning</h1>
        <p>Machine learning and deep learning are important.</p>
        """
        
        result = analyzer.analyze(html)
        
        assert len(result['key_phrases']) > 0
        phrases = [p['phrase'] for p in result['key_phrases']]
        assert any('learning' in p for p in phrases)
    
    def test_generate_table_of_contents(self):
        """Test generating table of contents"""
        analyzer = ContentStructureAnalyzer()
        html = """
        <h1>Chapter 1</h1>
        <h2>Section 1.1</h2>
        <h2>Section 1.2</h2>
        """
        
        result = analyzer.analyze(html)
        toc = analyzer.generate_table_of_contents(result['outline'])
        
        assert "Table of Contents" in toc
        assert "Chapter 1" in toc
        assert "Section 1.1" in toc
    
    def test_empty_content(self):
        """Test with empty content"""
        analyzer = ContentStructureAnalyzer()
        html = "<p>No headings</p>"
        
        result = analyzer.analyze(html)
        
        assert result['outline']['total_headings'] == 0
        assert result['metadata']['has_clear_structure'] is False
    
    def test_complex_hierarchy(self):
        """Test with complex heading hierarchy"""
        analyzer = ContentStructureAnalyzer()
        html = """
        <h1>Book</h1>
        <h2>Chapter 1</h2>
        <h3>Section 1.1</h3>
        <h4>Subsection 1.1.1</h4>
        <h5>Detail 1.1.1.1</h5>
        <h2>Chapter 2</h2>
        """
        
        result = analyzer.analyze(html)
        
        assert result['outline']['hierarchy_depth'] == 5
        assert result['outline']['total_headings'] == 6
    
    def test_section_count(self):
        """Test section counting"""
        analyzer = ContentStructureAnalyzer()
        html = """
        <h1>Title</h1>
        <p>Content 1</p>
        <h2>Section</h2>
        <p>Content 2</p>
        """
        
        result = analyzer.analyze(html)
        
        assert result['metadata']['total_sections'] > 0


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_full_blog_analysis(self):
        """Test analyzing a complete blog post"""
        analyzer = ContentStructureAnalyzer(
            extract_key_phrases=True,
            classify_content_type=True
        )
        
        html = """
        <article>
            <h1>Understanding Machine Learning</h1>
            <time>2024-01-01</time>
            <p>Posted by Data Scientist</p>
            
            <h2>Introduction</h2>
            <p>Machine learning is revolutionizing artificial intelligence.</p>
            
            <h2>Key Concepts</h2>
            <p>Deep learning and neural networks are fundamental.</p>
            
            <h2>Conclusion</h2>
            <p>Machine learning continues to evolve rapidly.</p>
        </article>
        """
        
        result = analyzer.analyze(html)
        
        # Check all components
        assert result['content_type']['primary_type'] == 'blog_post'
        assert result['outline']['total_headings'] == 4
        assert len(result['key_phrases']) > 0
        assert result['metadata']['has_clear_structure'] is True
    
    def test_technical_documentation_analysis(self):
        """Test analyzing technical documentation"""
        analyzer = ContentStructureAnalyzer()
        
        html = """
        <h1>API Documentation</h1>
        <h2>Methods</h2>
        <code>function getData()</code>
        <p>This method retrieves data from the API.</p>
        <h2>Parameters</h2>
        <p>The function accepts various parameters.</p>
        """
        
        result = analyzer.analyze(html)
        
        assert result['outline']['title'] == "API Documentation"
        assert result['content_type']['primary_type'] == 'technical_docs'
    
    def test_academic_paper_structure(self):
        """Test analyzing academic paper structure"""
        analyzer = ContentStructureAnalyzer()
        
        html = """
        <h1>Research Paper Title</h1>
        <abstract>This study investigates...</abstract>
        <h2>Introduction</h2>
        <h2>Methodology</h2>
        <h2>Results</h2>
        <h2>Discussion</h2>
        <h2>Conclusion</h2>
        <h2>References</h2>
        """
        
        result = analyzer.analyze(html)
        
        # Should detect academic structure
        sections = result['outline']['sections']
        section_types = [s['type'] for s in sections]
        assert 'introduction' in section_types
        assert 'methodology' in section_types
        assert 'conclusion' in section_types

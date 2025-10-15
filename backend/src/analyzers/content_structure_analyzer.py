"""
Content Structure Analyzer

Analyzes document structure, extracts heading hierarchies, identifies sections,
classifies content types, and prepares structured data for AI processing.

Features:
- Heading hierarchy detection (H1-H6)
- Section identification and extraction
- Content type classification
- Key phrase extraction
- Document outline generation
- Structural metadata extraction
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import Counter
from bs4 import BeautifulSoup, Tag, NavigableString

logger = logging.getLogger(__name__)


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class Heading:
    """Represents a heading in the document"""
    level: int  # 1-6 for H1-H6
    text: str
    id: Optional[str] = None
    position: int = 0  # Position in document
    parent: Optional['Heading'] = None
    children: List['Heading'] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding circular references)"""
        return {
            'level': self.level,
            'text': self.text,
            'id': self.id,
            'position': self.position,
            'children': [child.to_dict() for child in self.children]
        }


@dataclass
class Section:
    """Represents a section in the document"""
    heading: Optional[Heading]
    content: str
    word_count: int
    type: str  # 'introduction', 'body', 'conclusion', 'sidebar', etc.
    start_position: int
    end_position: int
    subsections: List['Section'] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'heading': self.heading.to_dict() if self.heading else None,
            'content': self.content[:200] + '...' if len(self.content) > 200 else self.content,
            'word_count': self.word_count,
            'type': self.type,
            'start_position': self.start_position,
            'end_position': self.end_position,
            'subsections': [sub.to_dict() for sub in self.subsections]
        }


@dataclass
class DocumentOutline:
    """Represents the complete document outline"""
    title: Optional[str]
    headings: List[Heading]
    sections: List[Section]
    hierarchy_depth: int
    total_headings: int
    heading_distribution: Dict[int, int]  # {level: count}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'headings': [h.to_dict() for h in self.headings],
            'sections': [s.to_dict() for s in self.sections],
            'hierarchy_depth': self.hierarchy_depth,
            'total_headings': self.total_headings,
            'heading_distribution': self.heading_distribution
        }


# ============================================================================
# Heading Hierarchy Detector
# ============================================================================

class HeadingHierarchyDetector:
    """
    Detects and builds heading hierarchies from HTML or text content.
    
    Features:
    - Extracts H1-H6 tags from HTML
    - Builds parent-child relationships
    - Handles markdown-style headings (# ## ###)
    - Validates hierarchy structure
    """
    
    def __init__(self):
        """Initialize the heading detector"""
        self.markdown_heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    
    def detect_from_html(self, html_content: str) -> List[Heading]:
        """
        Detect headings from HTML content.
        
        Args:
            html_content: HTML string
            
        Returns:
            List of Heading objects with hierarchy
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            headings = []
            position = 0
            
            # Find all heading tags
            for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                level = int(tag.name[1])  # Extract number from h1, h2, etc.
                text = tag.get_text(strip=True)
                heading_id = tag.get('id', None)
                
                if text:  # Only add non-empty headings
                    heading = Heading(
                        level=level,
                        text=text,
                        id=heading_id,
                        position=position
                    )
                    headings.append(heading)
                    position += 1
            
            # Build hierarchy
            self._build_hierarchy(headings)
            
            return headings
            
        except Exception as e:
            logger.error(f"Error detecting headings from HTML: {e}")
            return []
    
    def detect_from_markdown(self, markdown_content: str) -> List[Heading]:
        """
        Detect headings from Markdown content.
        
        Args:
            markdown_content: Markdown string
            
        Returns:
            List of Heading objects with hierarchy
        """
        try:
            headings = []
            position = 0
            
            # Find all markdown headings
            for match in self.markdown_heading_pattern.finditer(markdown_content):
                hashes, text = match.groups()
                level = len(hashes)
                
                heading = Heading(
                    level=level,
                    text=text.strip(),
                    position=position
                )
                headings.append(heading)
                position += 1
            
            # Build hierarchy
            self._build_hierarchy(headings)
            
            return headings
            
        except Exception as e:
            logger.error(f"Error detecting headings from Markdown: {e}")
            return []
    
    def _build_hierarchy(self, headings: List[Heading]) -> None:
        """
        Build parent-child relationships between headings.
        
        Args:
            headings: List of flat headings
        """
        if not headings:
            return
        
        # Stack to track potential parents at each level
        stack = []
        
        for heading in headings:
            # Pop headings from stack that are at same or deeper level
            while stack and stack[-1].level >= heading.level:
                stack.pop()
            
            # If stack not empty, top is parent
            if stack:
                parent = stack[-1]
                heading.parent = parent
                parent.children.append(heading)
            
            # Add current heading to stack
            stack.append(heading)
    
    def get_hierarchy_depth(self, headings: List[Heading]) -> int:
        """
        Calculate maximum depth of heading hierarchy.
        
        Args:
            headings: List of headings
            
        Returns:
            Maximum depth
        """
        if not headings:
            return 0
        
        def get_depth(heading: Heading) -> int:
            if not heading.children:
                return 1
            return 1 + max(get_depth(child) for child in heading.children)
        
        # Get root headings (those without parents)
        root_headings = [h for h in headings if h.parent is None]
        if not root_headings:
            return 0
        
        return max(get_depth(h) for h in root_headings)
    
    def get_heading_distribution(self, headings: List[Heading]) -> Dict[int, int]:
        """
        Get distribution of headings by level.
        
        Args:
            headings: List of headings
            
        Returns:
            Dictionary mapping level to count
        """
        distribution = {i: 0 for i in range(1, 7)}
        for heading in headings:
            distribution[heading.level] += 1
        return distribution


# ============================================================================
# Section Identifier
# ============================================================================

class SectionIdentifier:
    """
    Identifies and extracts sections from document content.
    
    Features:
    - Section boundary detection
    - Content extraction per section
    - Section type classification
    - Nested section handling
    """
    
    # Keywords for section type classification
    SECTION_KEYWORDS = {
        'introduction': ['introduction', 'overview', 'summary', 'abstract', 'preface'],
        'methodology': ['methodology', 'methods', 'approach', 'implementation'],
        'results': ['results', 'findings', 'outcomes', 'analysis'],
        'discussion': ['discussion', 'interpretation', 'implications'],
        'conclusion': ['conclusion', 'summary', 'closing', 'final'],
        'references': ['references', 'bibliography', 'citations', 'sources'],
        'appendix': ['appendix', 'supplementary', 'additional'],
    }
    
    def __init__(self):
        """Initialize the section identifier"""
        pass
    
    def identify_sections(
        self, 
        html_content: str, 
        headings: List[Heading]
    ) -> List[Section]:
        """
        Identify sections based on headings and content.
        
        Args:
            html_content: HTML content
            headings: List of detected headings
            
        Returns:
            List of Section objects
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            sections = []
            
            # Get all heading tags
            heading_tags = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            
            if not heading_tags:
                # No headings, treat entire content as one section
                content = soup.get_text(strip=True)
                section = Section(
                    heading=None,
                    content=content,
                    word_count=len(content.split()),
                    type='body',
                    start_position=0,
                    end_position=len(content)
                )
                return [section]
            
            # Extract content between headings
            for i, heading_tag in enumerate(heading_tags):
                # Find matching Heading object
                heading_text = heading_tag.get_text(strip=True)
                matching_heading = next(
                    (h for h in headings if h.text == heading_text),
                    None
                )
                
                # Get content between this heading and next
                content_elements = []
                current = heading_tag.next_sibling
                next_heading = heading_tags[i + 1] if i + 1 < len(heading_tags) else None
                
                while current and current != next_heading:
                    if isinstance(current, Tag):
                        # Check if we've reached the next heading
                        if current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                            break
                        content_elements.append(current.get_text(strip=True))
                    elif isinstance(current, NavigableString):
                        text = str(current).strip()
                        if text:
                            content_elements.append(text)
                    current = current.next_sibling
                
                content = ' '.join(content_elements)
                word_count = len(content.split())
                
                # Classify section type
                section_type = self._classify_section_type(
                    heading_text if matching_heading else ''
                )
                
                section = Section(
                    heading=matching_heading,
                    content=content,
                    word_count=word_count,
                    type=section_type,
                    start_position=i,
                    end_position=i + 1
                )
                sections.append(section)
            
            # Build section hierarchy
            self._build_section_hierarchy(sections)
            
            return sections
            
        except Exception as e:
            logger.error(f"Error identifying sections: {e}")
            return []
    
    def _classify_section_type(self, heading_text: str) -> str:
        """
        Classify section type based on heading text.
        
        Args:
            heading_text: Text of the heading
            
        Returns:
            Section type string
        """
        heading_lower = heading_text.lower()
        
        for section_type, keywords in self.SECTION_KEYWORDS.items():
            if any(keyword in heading_lower for keyword in keywords):
                return section_type
        
        return 'body'
    
    def _build_section_hierarchy(self, sections: List[Section]) -> None:
        """
        Build parent-child relationships between sections.
        
        Args:
            sections: List of sections
        """
        stack = []
        
        for section in sections:
            if not section.heading:
                continue
            
            # Pop sections with same or deeper level
            while stack and stack[-1].heading and \
                  stack[-1].heading.level >= section.heading.level:
                stack.pop()
            
            # If stack not empty, top is parent
            if stack:
                parent = stack[-1]
                parent.subsections.append(section)
            
            stack.append(section)


# ============================================================================
# Content Type Classifier
# ============================================================================

class ContentTypeClassifier:
    """
    Classifies content types within the document.
    
    Features:
    - Article/blog post detection
    - Technical documentation detection
    - News article detection
    - Product page detection
    - Academic paper detection
    """
    
    CONTENT_TYPE_INDICATORS = {
        'blog_post': {
            'elements': ['article', 'time', 'author'],
            'keywords': ['posted', 'published', 'author', 'comment'],
            'patterns': [r'by\s+\w+', r'\d{1,2}/\d{1,2}/\d{4}']
        },
        'news_article': {
            'elements': ['article', 'time', 'byline'],
            'keywords': ['breaking', 'update', 'reported', 'journalist'],
            'patterns': [r'UPDATED:', r'PUBLISHED:']
        },
        'technical_docs': {
            'elements': ['code', 'pre', 'kbd'],
            'keywords': ['api', 'function', 'class', 'method', 'parameter'],
            'patterns': [r'```', r'`\w+`', r'def\s+\w+\(']
        },
        'academic_paper': {
            'elements': ['abstract', 'references', 'figure'],
            'keywords': ['abstract', 'methodology', 'results', 'conclusion', 'et al'],
            'patterns': [r'\[\d+\]', r'\(\d{4}\)']
        },
        'product_page': {
            'elements': ['price', 'button', 'cart'],
            'keywords': ['buy', 'price', 'cart', 'checkout', 'add to'],
            'patterns': [r'\$\d+', r'€\d+', r'£\d+']
        },
        'landing_page': {
            'elements': ['form', 'button', 'cta'],
            'keywords': ['sign up', 'get started', 'free trial', 'subscribe'],
            'patterns': [r'call to action', r'cta']
        }
    }
    
    def __init__(self):
        """Initialize the content type classifier"""
        pass
    
    def classify(self, html_content: str, text_content: str) -> Dict[str, Any]:
        """
        Classify the content type.
        
        Args:
            html_content: HTML content
            text_content: Plain text content
            
        Returns:
            Dictionary with classification results
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            scores = {}
            
            for content_type, indicators in self.CONTENT_TYPE_INDICATORS.items():
                score = 0
                
                # Check for HTML elements
                for element in indicators.get('elements', []):
                    if soup.find(element):
                        score += 2
                
                # Check for keywords
                text_lower = text_content.lower()
                for keyword in indicators.get('keywords', []):
                    if keyword in text_lower:
                        score += 1
                
                # Check for patterns
                for pattern in indicators.get('patterns', []):
                    if re.search(pattern, text_content, re.IGNORECASE):
                        score += 1.5
                
                scores[content_type] = score
            
            # Get primary and secondary types
            sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            primary_type = sorted_types[0][0] if sorted_types[0][1] > 0 else 'general'
            secondary_types = [t for t, s in sorted_types[1:3] if s > 0]
            
            return {
                'primary_type': primary_type,
                'secondary_types': secondary_types,
                'scores': scores,
                'confidence': min(sorted_types[0][1] / 10, 1.0) if sorted_types else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error classifying content type: {e}")
            return {
                'primary_type': 'general',
                'secondary_types': [],
                'scores': {},
                'confidence': 0.0
            }


# ============================================================================
# Key Phrase Extractor
# ============================================================================

class KeyPhraseExtractor:
    """
    Extracts key phrases and important terms from content.
    
    Features:
    - TF-IDF-like scoring
    - Multi-word phrase extraction
    - Named entity-like detection
    - Technical term identification
    """
    
    # Common stop words to ignore
    STOP_WORDS = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
        'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
        'is', 'are', 'was', 'were', 'been', 'has', 'had', 'can', 'could'
    }
    
    def __init__(self, max_phrases: int = 20):
        """
        Initialize the key phrase extractor.
        
        Args:
            max_phrases: Maximum number of phrases to extract
        """
        self.max_phrases = max_phrases
    
    def extract_key_phrases(self, text: str, headings: List[Heading]) -> List[Dict[str, Any]]:
        """
        Extract key phrases from text.
        
        Args:
            text: Text content
            headings: List of headings (given higher weight)
            
        Returns:
            List of key phrases with scores
        """
        try:
            # Extract candidate phrases
            single_words = self._extract_single_words(text)
            bigrams = self._extract_ngrams(text, 2)
            trigrams = self._extract_ngrams(text, 3)
            
            # Boost phrases from headings
            heading_terms = self._extract_heading_terms(headings)
            
            # Score all phrases
            all_phrases = []
            
            # Single words
            for word, count in single_words.most_common(self.max_phrases):
                score = count
                if word.lower() in heading_terms:
                    score *= 2
                all_phrases.append({
                    'phrase': word,
                    'type': 'word',
                    'frequency': count,
                    'score': score
                })
            
            # Bigrams
            for phrase, count in bigrams.most_common(self.max_phrases):
                score = count * 1.5  # Boost multi-word phrases
                if phrase.lower() in heading_terms:
                    score *= 2
                all_phrases.append({
                    'phrase': phrase,
                    'type': 'bigram',
                    'frequency': count,
                    'score': score
                })
            
            # Trigrams
            for phrase, count in trigrams.most_common(self.max_phrases // 2):
                score = count * 2  # Higher boost for longer phrases
                if phrase.lower() in heading_terms:
                    score *= 2
                all_phrases.append({
                    'phrase': phrase,
                    'type': 'trigram',
                    'frequency': count,
                    'score': score
                })
            
            # Sort by score and return top phrases
            all_phrases.sort(key=lambda x: x['score'], reverse=True)
            return all_phrases[:self.max_phrases]
            
        except Exception as e:
            logger.error(f"Error extracting key phrases: {e}")
            return []
    
    def _extract_single_words(self, text: str) -> Counter:
        """Extract and count single words"""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        words = [w for w in words if w not in self.STOP_WORDS]
        return Counter(words)
    
    def _extract_ngrams(self, text: str, n: int) -> Counter:
        """Extract and count n-grams"""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        words = [w for w in words if w not in self.STOP_WORDS]
        
        ngrams = []
        for i in range(len(words) - n + 1):
            ngram = ' '.join(words[i:i+n])
            ngrams.append(ngram)
        
        return Counter(ngrams)
    
    def _extract_heading_terms(self, headings: List[Heading]) -> set:
        """Extract terms from headings"""
        terms = set()
        for heading in headings:
            words = re.findall(r'\b[a-zA-Z]+\b', heading.text.lower())
            terms.update(words)
            # Also add full heading as phrase
            terms.add(heading.text.lower())
        return terms


# ============================================================================
# Content Structure Analyzer (Main Class)
# ============================================================================

class ContentStructureAnalyzer:
    """
    Main analyzer that orchestrates all structure analysis components.
    
    Combines:
    - Heading hierarchy detection
    - Section identification
    - Content type classification
    - Key phrase extraction
    - Document outline generation
    """
    
    def __init__(
        self,
        extract_key_phrases: bool = True,
        max_key_phrases: int = 20,
        classify_content_type: bool = True
    ):
        """
        Initialize the content structure analyzer.
        
        Args:
            extract_key_phrases: Whether to extract key phrases
            max_key_phrases: Maximum number of key phrases
            classify_content_type: Whether to classify content type
        """
        self.extract_key_phrases_flag = extract_key_phrases
        self.max_key_phrases = max_key_phrases
        self.classify_content_type_flag = classify_content_type
        
        # Initialize components
        self.heading_detector = HeadingHierarchyDetector()
        self.section_identifier = SectionIdentifier()
        self.content_classifier = ContentTypeClassifier()
        self.phrase_extractor = KeyPhraseExtractor(max_key_phrases)
    
    def analyze(
        self, 
        html_content: str, 
        text_content: Optional[str] = None,
        content_format: str = 'html'
    ) -> Dict[str, Any]:
        """
        Perform complete structure analysis.
        
        Args:
            html_content: HTML content (or markdown if format='markdown')
            text_content: Plain text content (optional, extracted if not provided)
            content_format: 'html' or 'markdown'
            
        Returns:
            Complete analysis results
        """
        try:
            results = {
                'format': content_format,
                'outline': None,
                'content_type': None,
                'key_phrases': [],
                'metadata': {}
            }
            
            # Extract text if not provided
            if text_content is None:
                soup = BeautifulSoup(html_content, 'html.parser')
                text_content = soup.get_text(separator=' ', strip=True)
            
            # Detect headings
            if content_format == 'markdown':
                headings = self.heading_detector.detect_from_markdown(html_content)
            else:
                headings = self.heading_detector.detect_from_html(html_content)
            
            # Identify sections
            sections = self.section_identifier.identify_sections(html_content, headings)
            
            # Build document outline
            outline = self._build_outline(headings, sections)
            results['outline'] = outline.to_dict()
            
            # Classify content type
            if self.classify_content_type_flag:
                content_type = self.content_classifier.classify(
                    html_content, 
                    text_content
                )
                results['content_type'] = content_type
            
            # Extract key phrases
            if self.extract_key_phrases_flag:
                key_phrases = self.phrase_extractor.extract_key_phrases(
                    text_content,
                    headings
                )
                results['key_phrases'] = key_phrases
            
            # Add metadata
            results['metadata'] = {
                'total_headings': len(headings),
                'total_sections': len(sections),
                'hierarchy_depth': outline.hierarchy_depth,
                'has_clear_structure': len(headings) > 0,
                'avg_section_length': sum(s.word_count for s in sections) / len(sections) if sections else 0
            }
            
            logger.info(f"Structure analysis complete: {len(headings)} headings, {len(sections)} sections")
            return results
            
        except Exception as e:
            logger.error(f"Error in structure analysis: {e}")
            return self._empty_result()
    
    def _build_outline(
        self, 
        headings: List[Heading], 
        sections: List[Section]
    ) -> DocumentOutline:
        """
        Build complete document outline.
        
        Args:
            headings: List of headings
            sections: List of sections
            
        Returns:
            DocumentOutline object
        """
        # Find title (first H1 or highest level heading)
        title = None
        if headings:
            h1_headings = [h for h in headings if h.level == 1]
            if h1_headings:
                title = h1_headings[0].text
            else:
                title = headings[0].text
        
        # Get hierarchy depth
        hierarchy_depth = self.heading_detector.get_hierarchy_depth(headings)
        
        # Get heading distribution
        heading_distribution = self.heading_detector.get_heading_distribution(headings)
        
        return DocumentOutline(
            title=title,
            headings=headings,
            sections=sections,
            hierarchy_depth=hierarchy_depth,
            total_headings=len(headings),
            heading_distribution=heading_distribution
        )
    
    def generate_table_of_contents(self, outline: Dict[str, Any]) -> str:
        """
        Generate a text-based table of contents.
        
        Args:
            outline: Document outline dictionary
            
        Returns:
            Formatted table of contents string
        """
        try:
            toc_lines = ["Table of Contents", "=" * 50, ""]
            
            def add_heading(heading_dict: Dict, indent_level: int = 0):
                indent = "  " * indent_level
                text = heading_dict['text']
                toc_lines.append(f"{indent}{text}")
                
                for child in heading_dict.get('children', []):
                    add_heading(child, indent_level + 1)
            
            for heading in outline.get('headings', []):
                if heading.get('level') == 1 or not heading.get('parent'):
                    add_heading(heading)
            
            return '\n'.join(toc_lines)
            
        except Exception as e:
            logger.error(f"Error generating TOC: {e}")
            return ""
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure"""
        return {
            'format': 'unknown',
            'outline': None,
            'content_type': None,
            'key_phrases': [],
            'metadata': {}
        }

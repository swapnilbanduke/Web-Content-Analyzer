"""
Advanced Content Extraction Engine
Intelligently identifies main content, removes navigation and ads,
extracts metadata, and handles various HTML structures and CMS patterns.
"""
import logging
from typing import List, Dict, Any, Optional, Set, Tuple
from bs4 import BeautifulSoup, Tag, NavigableString
from urllib.parse import urljoin, urlparse
from collections import defaultdict
import re

from ..models.data_models import ProcessedContent, Metadata, Image, Link, Heading, ContentType

logger = logging.getLogger(__name__)


class ContentExtractor:
    """
    Advanced content extraction with main content identification,
    boilerplate removal, and intelligent content scoring.
    
    Features:
    - Main content identification using semantic HTML and scoring algorithms
    - Navigation and advertisement removal
    - Comprehensive metadata extraction
    - Image and media content handling with metadata
    - Structured data extraction support
    - CMS pattern recognition
    """
    
    # Content indicators (positive signals)
    CONTENT_INDICATORS = {
        'article', 'content', 'main', 'post', 'entry', 'story',
        'body', 'text', 'paragraph', 'section', 'chapter'
    }
    
    # Boilerplate indicators (negative signals)
    BOILERPLATE_INDICATORS = {
        'nav', 'navigation', 'menu', 'sidebar', 'footer', 'header',
        'advertisement', 'ads', 'promo', 'sponsored', 'social',
        'share', 'comment', 'widget', 'related', 'recommended'
    }
    
    # Tags to remove
    REMOVE_TAGS = {
        'script', 'style', 'noscript', 'iframe', 'embed',
        'object', 'applet', 'link'
    }
    
    def __init__(self):
        """Initialize the content extractor"""
        self.min_text_length = 50  # Minimum text length for content blocks
        self.min_word_count = 10   # Minimum word count
    
    def extract(self, html: str, base_url: str) -> ProcessedContent:
        """
        Extract structured content from HTML using advanced algorithms
        
        Args:
            html: Raw HTML content
            base_url: Base URL for resolving relative links
            
        Returns:
            ProcessedContent object with extracted data
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract main content using intelligent algorithms
            main_content, content_html = self._extract_main_content(soup)
            
            # Extract comprehensive metadata
            metadata_dict = self._extract_metadata(soup, base_url)
            
            # Create Metadata object
            metadata = Metadata(
                title=metadata_dict.get('title'),
                description=metadata_dict.get('description'),
                keywords=metadata_dict.get('keywords', []),
                author=metadata_dict.get('author'),
                language=metadata_dict.get('language'),
                og_title=metadata_dict.get('og_title'),
                og_description=metadata_dict.get('og_description'),
                og_image=metadata_dict.get('og_image'),
                twitter_title=metadata_dict.get('twitter_title'),
                twitter_description=metadata_dict.get('twitter_description')
            )
            
            # Add text statistics
            text_stats = self._calculate_text_stats(main_content)
            
            # Extract headings for structure
            headings_data = self._extract_headings(soup)
            headings_list = [
                Heading(
                    level=h['level'],
                    text=h['text'],
                    id=h['id'] if h['id'] else None,
                    position=i
                )
                for i, h in enumerate(headings_data)
            ]
            
            # Extract links with metadata
            links_data = self._extract_links(soup, base_url)
            links = []
            for link_data in links_data:
                try:
                    links.append(Link(
                        href=link_data['url'],
                        text=link_data['text'] if link_data['text'] else None,
                        title=link_data['title'] if link_data['title'] else None,
                        rel=link_data['rel'] if link_data['rel'] else None,
                        is_internal=link_data.get('internal', False),
                        is_external=not link_data.get('internal', False)
                    ))
                except Exception as e:
                    logger.debug(f"Skipping invalid link: {e}")
            
            # Extract images with metadata
            images_data = self._extract_images(soup, base_url)
            images = []
            for img_data in images_data:
                try:
                    images.append(Image(
                        src=img_data['url'],
                        alt=img_data.get('alt') if img_data.get('alt') else None,
                        title=img_data.get('title') if img_data.get('title') else None,
                        width=img_data.get('width'),
                        height=img_data.get('height')
                    ))
                except Exception as e:
                    logger.debug(f"Skipping invalid image: {e}")
            
            return ProcessedContent(
                url=base_url,
                original_content=html,
                processed_text=main_content,
                metadata=metadata,
                headings=headings_list,
                images=images,
                links=links,
                word_count=text_stats.get('word_count', 0),
                sentence_count=text_stats.get('sentence_count', 0),
                paragraph_count=text_stats.get('paragraph_count', 0),
                character_count=len(main_content)
            )
            
        except Exception as e:
            logger.error(f"Content extraction error: {str(e)}", exc_info=True)
            # Return minimal content on error
            return ProcessedContent(
                url=base_url,
                original_content=html,
                processed_text="",
                metadata=Metadata(title="Error extracting content"),
                word_count=0,
                sentence_count=0,
                paragraph_count=0,
                character_count=0
            )
    
    def _extract_main_content(self, soup: BeautifulSoup) -> Tuple[str, str]:
        """
        Extract main content using multiple strategies:
        1. Semantic HTML5 tags (article, main)
        2. Content scoring algorithm
        3. Boilerplate removal
        
        Returns:
            Tuple of (text_content, html_content)
        """
        # Create a working copy
        soup_copy = BeautifulSoup(str(soup), 'html.parser')
        
        # Strategy 1: Try semantic tags first
        main_element = self._find_semantic_main_content(soup_copy)
        
        if main_element:
            logger.info("Found main content via semantic tags")
            return self._extract_text_from_element(main_element), str(main_element)
        
        # Strategy 2: Score-based content identification
        logger.info("Using content scoring algorithm")
        
        # Remove unwanted elements
        self._remove_boilerplate_elements(soup_copy)
        
        # Score all potential content blocks
        content_blocks = self._score_content_blocks(soup_copy)
        
        if not content_blocks:
            # Fallback: get body text
            body = soup_copy.find('body') or soup_copy
            return self._extract_text_from_element(body), str(body)
        
        # Get the highest scoring block
        best_block = max(content_blocks, key=lambda x: x[1])
        element = best_block[0]
        
        text_content = self._extract_text_from_element(element)
        html_content = str(element)
        
        return text_content, html_content
    
    def _find_semantic_main_content(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Find main content using semantic HTML5 tags"""
        # Try <article> tag
        article = soup.find('article')
        if article and self._has_sufficient_text(article):
            return article
        
        # Try <main> tag
        main = soup.find('main')
        if main and self._has_sufficient_text(main):
            return main
        
        # Try role="main"
        role_main = soup.find(attrs={'role': 'main'})
        if role_main and self._has_sufficient_text(role_main):
            return role_main
        
        # Try common content class/id patterns
        for pattern in ['content', 'main-content', 'post-content', 'entry-content', 'article-content']:
            element = soup.find(attrs={'class': re.compile(pattern, re.I)}) or \
                     soup.find(attrs={'id': re.compile(pattern, re.I)})
            if element and self._has_sufficient_text(element):
                return element
        
        return None
    
    def _remove_boilerplate_elements(self, soup: BeautifulSoup) -> None:
        """Remove navigation, ads, and other boilerplate elements"""
        # Remove script, style, etc.
        for tag_name in self.REMOVE_TAGS:
            for element in soup.find_all(tag_name):
                element.decompose()
        
        # Remove semantic boilerplate tags
        for tag_name in ['nav', 'header', 'footer', 'aside']:
            for element in soup.find_all(tag_name):
                element.decompose()
        
        # Remove elements with boilerplate class/id
        for element in soup.find_all(True):
            class_str = ' '.join(element.get('class', [])).lower()
            id_str = element.get('id', '').lower()
            
            combined = f"{class_str} {id_str}"
            
            # Check for boilerplate indicators
            if any(indicator in combined for indicator in self.BOILERPLATE_INDICATORS):
                element.decompose()
                continue
            
            # Remove hidden elements
            style = element.get('style', '')
            if 'display:none' in style.replace(' ', '') or 'visibility:hidden' in style.replace(' ', ''):
                element.decompose()
                continue
            
            # Remove elements with aria-hidden
            if element.get('aria-hidden') == 'true':
                element.decompose()
    
    def _score_content_blocks(self, soup: BeautifulSoup) -> List[Tuple[Tag, float]]:
        """
        Score potential content blocks using multiple signals:
        - Text density
        - Link density
        - Class/ID indicators
        - Paragraph count
        - Text length
        """
        scored_blocks = []
        
        # Find all block-level elements
        for element in soup.find_all(['div', 'section', 'article', 'main']):
            score = 0.0
            
            # Get text content
            text = element.get_text(strip=True)
            
            # Skip if too short
            if len(text) < self.min_text_length:
                continue
            
            # 1. Text length score (more text = better)
            text_length = len(text)
            score += min(text_length / 1000, 10)  # Cap at 10 points
            
            # 2. Paragraph density score
            paragraphs = element.find_all('p')
            para_count = len(paragraphs)
            if para_count > 0:
                score += min(para_count * 2, 20)  # Up to 20 points
            
            # 3. Link density score (lower is better for main content)
            links = element.find_all('a')
            if text_length > 0:
                link_text_length = sum(len(link.get_text(strip=True)) for link in links)
                link_density = link_text_length / text_length
                score -= link_density * 10  # Penalize high link density
            
            # 4. Class/ID indicators
            class_str = ' '.join(element.get('class', [])).lower()
            id_str = element.get('id', '').lower()
            combined = f"{class_str} {id_str}"
            
            # Positive indicators
            for indicator in self.CONTENT_INDICATORS:
                if indicator in combined:
                    score += 15
            
            # Negative indicators
            for indicator in self.BOILERPLATE_INDICATORS:
                if indicator in combined:
                    score -= 10
            
            # 5. Heading presence
            headings = element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if headings:
                score += len(headings) * 3
            
            # 6. Semantic tags bonus
            if element.name in ['article', 'main']:
                score += 25
            
            scored_blocks.append((element, score))
        
        # Sort by score descending
        scored_blocks.sort(key=lambda x: x[1], reverse=True)
        
        logger.debug(f"Scored {len(scored_blocks)} content blocks")
        if scored_blocks:
            logger.debug(f"Top score: {scored_blocks[0][1]:.2f}")
        
        return scored_blocks
    
    def _has_sufficient_text(self, element: Tag) -> bool:
        """Check if element has sufficient text content"""
        text = element.get_text(strip=True)
        word_count = len(text.split())
        return len(text) >= self.min_text_length and word_count >= self.min_word_count
    
    def _extract_text_from_element(self, element: Tag) -> str:
        """Extract clean text from element"""
        # Get text with proper spacing
        text = element.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n\n', text)
        
        return text.strip()
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract comprehensive metadata from HTML"""
        metadata = {"url": url}
        
        # Title - multiple strategies
        title = None
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
        
        # Open Graph title (often better quality)
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            title = og_title.get('content')
        
        metadata['title'] = title or "No title"
        
        # Meta description
        description = soup.find('meta', attrs={'name': 'description'})
        if description and description.get('content'):
            metadata['description'] = description.get('content')
        
        # Open Graph description
        og_description = soup.find('meta', property='og:description')
        if og_description and og_description.get('content'):
            metadata['og_description'] = og_description.get('content')
        
        # Keywords
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        if keywords and keywords.get('content'):
            # Convert comma-separated string to list
            keywords_str = keywords.get('content')
            metadata['keywords'] = [k.strip() for k in keywords_str.split(',') if k.strip()]
        
        # Author
        author = soup.find('meta', attrs={'name': 'author'})
        if author and author.get('content'):
            metadata['author'] = author.get('content')
        
        # Article author
        article_author = soup.find('meta', property='article:author')
        if article_author and article_author.get('content'):
            metadata['article_author'] = article_author.get('content')
        
        # Published date
        published = soup.find('meta', property='article:published_time')
        if published and published.get('content'):
            metadata['published_time'] = published.get('content')
        
        # Modified date
        modified = soup.find('meta', property='article:modified_time')
        if modified and modified.get('content'):
            metadata['modified_time'] = modified.get('content')
        
        # Canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            metadata['canonical_url'] = canonical['href']
        
        # Language
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            metadata['language'] = html_tag.get('lang')
        
        # Open Graph data
        og_data = {}
        for og_meta in soup.find_all('meta', property=re.compile(r'^og:')):
            prop = og_meta.get('property', '').replace('og:', '')
            content = og_meta.get('content')
            if prop and content:
                og_data[prop] = content
        
        if og_data:
            metadata['open_graph'] = og_data
        
        # Twitter Card data
        twitter_data = {}
        for twitter_meta in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
            name = twitter_meta.get('name', '').replace('twitter:', '')
            content = twitter_meta.get('content')
            if name and content:
                twitter_data[name] = content
        
        if twitter_data:
            metadata['twitter_card'] = twitter_data
        
        # Check for forms
        metadata['has_forms'] = len(soup.find_all('form')) > 0
        
        # Check for tables
        metadata['has_tables'] = len(soup.find_all('table')) > 0
        
        return metadata
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract page structure via headings"""
        headings = []
        
        for level in range(1, 7):
            for heading in soup.find_all(f'h{level}'):
                text = heading.get_text(strip=True)
                if text:
                    headings.append({
                        'level': level,
                        'text': text,
                        'id': heading.get('id', '')
                    })
        
        return headings
    
    def _calculate_text_stats(self, text: str) -> Dict[str, int]:
        """Calculate text statistics"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        
        return {
            'character_count': len(text),
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'paragraph_count': len(paragraphs),
            'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
            'avg_sentence_length': len(words) / len([s for s in sentences if s.strip()]) if sentences else 0
        }
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all links with comprehensive metadata"""
        links = []
        seen_urls = set()
        
        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            
            # Skip empty, javascript, and anchor links
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
            
            # Make absolute URL
            absolute_url = urljoin(base_url, href)
            
            # Filter non-HTTP(S) links
            parsed = urlparse(absolute_url)
            if parsed.scheme not in ['http', 'https']:
                continue
            
            # Skip duplicates
            if absolute_url in seen_urls:
                continue
            
            seen_urls.add(absolute_url)
            
            # Extract link metadata
            link_data = {
                'url': absolute_url,
                'text': link.get_text(strip=True),
                'title': link.get('title', ''),
                'rel': ' '.join(link.get('rel', [])),
                'internal': parsed.netloc == urlparse(base_url).netloc,
                'nofollow': 'nofollow' in link.get('rel', [])
            }
            
            links.append(link_data)
        
        return links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract image information with comprehensive metadata"""
        images = []
        seen_urls = set()
        
        for img in soup.find_all('img'):
            src = img.get('src', '').strip()
            
            if not src:
                # Try srcset
                srcset = img.get('srcset', '')
                if srcset:
                    # Take first image from srcset
                    src = srcset.split(',')[0].split()[0]
            
            if not src or src in seen_urls:
                continue
            
            seen_urls.add(src)
            
            # Make absolute URL
            absolute_url = urljoin(base_url, src)
            
            # Extract image metadata
            image_data = {
                'url': absolute_url,
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'width': img.get('width', ''),
                'height': img.get('height', ''),
                'loading': img.get('loading', ''),
                'srcset': img.get('srcset', '')
            }
            
            # Check if it's in a figure with caption
            figure = img.find_parent('figure')
            if figure:
                caption = figure.find('figcaption')
                if caption:
                    image_data['caption'] = caption.get_text(strip=True)
            
            images.append(image_data)
        
        return images

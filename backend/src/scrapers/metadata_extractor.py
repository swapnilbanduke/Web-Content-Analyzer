"""
Metadata Extractor - Extract comprehensive metadata from HTML
Supports Open Graph, Twitter Cards, Schema.org, and standard meta tags
"""
import logging
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """
    Comprehensive metadata extraction engine
    
    Extracts:
    - Standard HTML meta tags (title, description, keywords)
    - Open Graph protocol data
    - Twitter Card metadata
    - Article metadata (author, publish date, modified date)
    - Dublin Core metadata
    - Canonical URLs and alternate links
    - Language and locale information
    """
    
    def extract(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """
        Extract all metadata from HTML
        
        Args:
            soup: BeautifulSoup parsed HTML
            url: Source URL
            
        Returns:
            Dictionary containing all extracted metadata
        """
        metadata = {'source_url': url}
        
        # Basic HTML metadata
        metadata.update(self._extract_basic_metadata(soup))
        
        # Open Graph data
        og_data = self._extract_open_graph(soup)
        if og_data:
            metadata['open_graph'] = og_data
        
        # Twitter Card data
        twitter_data = self._extract_twitter_card(soup)
        if twitter_data:
            metadata['twitter_card'] = twitter_data
        
        # Article metadata
        article_data = self._extract_article_metadata(soup)
        if article_data:
            metadata['article'] = article_data
        
        # Dublin Core metadata
        dc_data = self._extract_dublin_core(soup)
        if dc_data:
            metadata['dublin_core'] = dc_data
        
        # Canonical and alternate links
        metadata.update(self._extract_links_metadata(soup))
        
        # Language and locale
        metadata.update(self._extract_language_metadata(soup))
        
        # Additional metadata
        metadata.update(self._extract_additional_metadata(soup))
        
        return metadata
    
    def _extract_basic_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract standard HTML meta tags"""
        metadata = {}
        
        # Title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()
        
        # Standard meta tags
        meta_tags = {
            'description': 'description',
            'keywords': 'keywords',
            'author': 'author',
            'robots': 'robots',
            'viewport': 'viewport',
            'generator': 'generator',
            'application-name': 'application_name',
            'theme-color': 'theme_color'
        }
        
        for meta_name, key in meta_tags.items():
            meta = soup.find('meta', attrs={'name': meta_name})
            if meta and meta.get('content'):
                metadata[key] = meta.get('content')
        
        return metadata
    
    def _extract_open_graph(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract Open Graph protocol metadata"""
        og_data = {}
        
        for meta in soup.find_all('meta', property=re.compile(r'^og:')):
            prop = meta.get('property', '').replace('og:', '')
            content = meta.get('content')
            
            if prop and content:
                # Handle nested properties (e.g., image:width)
                if ':' in prop:
                    main_prop, sub_prop = prop.split(':', 1)
                    if main_prop not in og_data:
                        og_data[main_prop] = {}
                    if isinstance(og_data[main_prop], dict):
                        og_data[main_prop][sub_prop] = content
                else:
                    og_data[prop] = content
        
        return og_data
    
    def _extract_twitter_card(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract Twitter Card metadata"""
        twitter_data = {}
        
        for meta in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
            name = meta.get('name', '').replace('twitter:', '')
            content = meta.get('content')
            
            if name and content:
                twitter_data[name] = content
        
        return twitter_data
    
    def _extract_article_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract article-specific metadata"""
        article_data = {}
        
        # Article tags (Open Graph article extension)
        article_tags = {
            'article:author': 'author',
            'article:published_time': 'published_time',
            'article:modified_time': 'modified_time',
            'article:section': 'section',
            'article:tag': 'tags'
        }
        
        for prop, key in article_tags.items():
            meta = soup.find('meta', property=prop)
            if meta and meta.get('content'):
                content = meta.get('content')
                
                # Parse dates
                if 'time' in key:
                    try:
                        article_data[key] = content
                        article_data[f"{key}_parsed"] = self._parse_datetime(content)
                    except:
                        article_data[key] = content
                else:
                    article_data[key] = content
        
        # Look for additional author information
        author_meta = soup.find('meta', attrs={'name': 'author'})
        if author_meta and author_meta.get('content'):
            article_data['author_name'] = author_meta.get('content')
        
        # Look for date in various formats
        date_patterns = [
            ('meta', {'name': 'date'}),
            ('meta', {'name': 'pubdate'}),
            ('meta', {'itemprop': 'datePublished'}),
            ('time', {'itemprop': 'datePublished'}),
            ('time', {'class': 'published'}),
        ]
        
        for tag, attrs in date_patterns:
            element = soup.find(tag, attrs=attrs)
            if element:
                date_content = element.get('content') or element.get('datetime') or element.get_text()
                if date_content and 'published_time' not in article_data:
                    article_data['published_time'] = date_content.strip()
                    break
        
        return article_data
    
    def _extract_dublin_core(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract Dublin Core metadata"""
        dc_data = {}
        
        # Dublin Core uses both 'name' and 'property' attributes
        for meta in soup.find_all('meta'):
            name = meta.get('name', '') or meta.get('property', '')
            
            if name.startswith('DC.') or name.startswith('dc.'):
                key = name.split('.', 1)[1].lower()
                content = meta.get('content')
                if content:
                    dc_data[key] = content
        
        return dc_data
    
    def _extract_links_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract link-based metadata (canonical, alternate, etc.)"""
        links_data = {}
        
        # Canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            links_data['canonical_url'] = canonical['href']
        
        # Alternate links (mobile, AMP, etc.)
        alternates = []
        for link in soup.find_all('link', rel='alternate'):
            href = link.get('href')
            if href:
                alternate = {'href': href}
                
                if link.get('media'):
                    alternate['media'] = link.get('media')
                if link.get('type'):
                    alternate['type'] = link.get('type')
                if link.get('hreflang'):
                    alternate['hreflang'] = link.get('hreflang')
                
                alternates.append(alternate)
        
        if alternates:
            links_data['alternate_links'] = alternates
        
        # AMP version
        amp_link = soup.find('link', rel='amphtml')
        if amp_link and amp_link.get('href'):
            links_data['amp_url'] = amp_link['href']
        
        # RSS/Atom feeds
        feed_link = soup.find('link', type='application/rss+xml')
        if feed_link and feed_link.get('href'):
            links_data['rss_url'] = feed_link['href']
        
        atom_link = soup.find('link', type='application/atom+xml')
        if atom_link and atom_link.get('href'):
            links_data['atom_url'] = atom_link['href']
        
        return links_data
    
    def _extract_language_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract language and locale information"""
        lang_data = {}
        
        # HTML lang attribute
        html_tag = soup.find('html')
        if html_tag:
            if html_tag.get('lang'):
                lang_data['language'] = html_tag.get('lang')
            if html_tag.get('xml:lang'):
                lang_data['xml_language'] = html_tag.get('xml:lang')
        
        # Content-Language meta tag
        content_lang = soup.find('meta', attrs={'http-equiv': re.compile('content-language', re.I)})
        if content_lang and content_lang.get('content'):
            lang_data['content_language'] = content_lang.get('content')
        
        # Open Graph locale
        og_locale = soup.find('meta', property='og:locale')
        if og_locale and og_locale.get('content'):
            lang_data['og_locale'] = og_locale.get('content')
        
        return lang_data
    
    def _extract_additional_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract additional useful metadata"""
        additional = {}
        
        # Favicon
        favicon = soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')
        if favicon and favicon.get('href'):
            additional['favicon'] = favicon['href']
        
        # Apple touch icon
        apple_icon = soup.find('link', rel='apple-touch-icon')
        if apple_icon and apple_icon.get('href'):
            additional['apple_touch_icon'] = apple_icon['href']
        
        # Manifest (PWA)
        manifest = soup.find('link', rel='manifest')
        if manifest and manifest.get('href'):
            additional['manifest_url'] = manifest['href']
        
        # Check for common page types
        additional['has_forms'] = len(soup.find_all('form')) > 0
        additional['has_tables'] = len(soup.find_all('table')) > 0
        additional['has_video'] = len(soup.find_all('video')) > 0
        additional['has_audio'] = len(soup.find_all('audio')) > 0
        
        # Count media elements
        additional['image_count'] = len(soup.find_all('img'))
        additional['link_count'] = len(soup.find_all('a', href=True))
        
        return additional
    
    def _parse_datetime(self, date_string: str) -> Optional[str]:
        """Parse datetime string to ISO format"""
        try:
            # Common datetime formats
            formats = [
                '%Y-%m-%dT%H:%M:%S%z',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%d %b %Y',
                '%B %d, %Y'
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_string.strip(), fmt)
                    return dt.isoformat()
                except ValueError:
                    continue
            
            return None
        except:
            return None

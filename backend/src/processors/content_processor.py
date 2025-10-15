"""
Enhanced Content Processor - Orchestrates all content extraction components
Integrates content extraction, metadata, structured data, media, and CMS detection
"""
import logging
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

from ..scrapers.content_extractor import ContentExtractor
from ..scrapers.metadata_extractor import MetadataExtractor
from ..scrapers.structured_data_extractor import StructuredDataExtractor
from ..scrapers.media_extractor import MediaExtractor
from ..scrapers.cms_detector import CMSDetector
from ..models.data_models import ScrapedContent

logger = logging.getLogger(__name__)


class ContentProcessor:
    """
    Enhanced content processor with comprehensive extraction capabilities
    
    Orchestrates:
    - Main content extraction with scoring algorithms
    - Metadata extraction (Open Graph, Twitter Cards, etc.)
    - Structured data extraction (JSON-LD, Microdata, RDFa)
    - Media extraction (images, videos, audio)
    - CMS detection and optimized extraction
    - Text processing and statistics
    """
    
    def __init__(self):
        """Initialize all extraction components"""
        self.content_extractor = ContentExtractor()
        self.metadata_extractor = MetadataExtractor()
        self.structured_data_extractor = StructuredDataExtractor()
        self.media_extractor = MediaExtractor()
        self.cms_detector = CMSDetector()
        
        logger.info("ContentProcessor initialized with all extractors")
    
    def process(
        self, 
        html: str, 
        url: str,
        extract_metadata: bool = True,
        extract_structured_data: bool = True,
        extract_media: bool = True,
        detect_cms: bool = True
    ) -> Dict[str, Any]:
        """
        Process HTML and extract all content
        
        Args:
            html: Raw HTML content
            url: Source URL
            extract_metadata: Whether to extract metadata
            extract_structured_data: Whether to extract structured data
            extract_media: Whether to extract media
            detect_cms: Whether to detect CMS
            
        Returns:
            Comprehensive extraction results dictionary
        """
        try:
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # CMS Detection (helps optimize other extractions)
            cms_info = None
            if detect_cms:
                cms_info = self.cms_detector.detect(soup, url)
                logger.info(f"CMS Detection: {cms_info.get('cms', 'None')} "
                          f"(confidence: {cms_info.get('confidence', 0):.2f})")
            
            # Main content extraction (always performed)
            content_result = self.content_extractor.extract(html, url)
            
            # If CMS detected, try to enhance extraction
            if cms_info and cms_info.get('cms'):
                enhanced_content = self.cms_detector.extract_with_cms_selectors(
                    soup, cms_info['cms'], 'content'
                )
                if enhanced_content and len(enhanced_content) > len(content_result['main_content']):
                    logger.info(f"Using CMS-optimized content extraction")
                    content_result['main_content'] = enhanced_content
                    content_result['extraction_method'] = 'cms_optimized'
                else:
                    content_result['extraction_method'] = 'algorithm'
            else:
                content_result['extraction_method'] = 'algorithm'
            
            # Build comprehensive result
            result = {
                'url': url,
                'main_content': content_result['main_content'],
                'text_stats': content_result.get('text_stats', {}),
                'extraction_method': content_result['extraction_method']
            }
            
            # Enhanced metadata extraction
            if extract_metadata:
                comprehensive_metadata = self.metadata_extractor.extract(soup, url)
                
                # Merge with basic metadata from content extractor
                result['metadata'] = {
                    **content_result.get('metadata', {}),
                    **comprehensive_metadata
                }
                
                # Add headings
                result['metadata']['headings'] = content_result.get('headings', [])
                
                logger.info(f"Extracted {len(result['metadata'])} metadata fields")
            else:
                result['metadata'] = content_result.get('metadata', {})
            
            # Structured data extraction
            if extract_structured_data:
                structured_data = self.structured_data_extractor.extract(soup)
                
                if structured_data:
                    result['structured_data'] = structured_data
                    
                    # Try to extract specific schema types
                    article_data = self.structured_data_extractor.extract_article_data(structured_data)
                    if article_data:
                        result['article_data'] = article_data
                    
                    product_data = self.structured_data_extractor.extract_product_data(structured_data)
                    if product_data:
                        result['product_data'] = product_data
                    
                    event_data = self.structured_data_extractor.extract_event_data(structured_data)
                    if event_data:
                        result['event_data'] = event_data
                    
                    logger.info(f"Extracted structured data with "
                              f"{len(structured_data.get('json_ld', []))} JSON-LD items")
            
            # Media extraction
            if extract_media:
                media_data = self.media_extractor.extract(soup, url)
                
                result['media'] = {
                    'images': media_data.get('images', []),
                    'videos': media_data.get('videos', []),
                    'audio': media_data.get('audio', []),
                    'embeds': media_data.get('embeds', []),
                    'counts': {
                        'images': len(media_data.get('images', [])),
                        'videos': len(media_data.get('videos', [])),
                        'audio': len(media_data.get('audio', [])),
                        'embeds': len(media_data.get('embeds', []))
                    }
                }
                
                logger.info(f"Extracted {result['media']['counts']['images']} images, "
                          f"{result['media']['counts']['videos']} videos")
            else:
                # Use basic link/image extraction from content extractor
                result['links'] = content_result.get('links', [])
                result['images'] = content_result.get('images', [])
            
            # CMS information
            if cms_info:
                result['cms'] = {
                    'detected': cms_info.get('cms'),
                    'confidence': cms_info.get('confidence', 0),
                    'features': self.cms_detector.get_cms_features(cms_info.get('cms'))
                }
            
            # Processing summary
            result['processing_summary'] = {
                'total_content_length': len(result['main_content']),
                'word_count': result['text_stats'].get('word_count', 0),
                'metadata_fields': len(result.get('metadata', {})),
                'has_structured_data': 'structured_data' in result,
                'cms_detected': cms_info.get('cms') if cms_info else None
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Content processing error: {str(e)}", exc_info=True)
            
            # Return minimal result on error
            return {
                'url': url,
                'main_content': '',
                'metadata': {'error': str(e)},
                'processing_summary': {
                    'error': True,
                    'error_message': str(e)
                }
            }
    
    def process_to_scraped_content(self, html: str, url: str) -> ScrapedContent:
        """
        Process HTML and return ScrapedContent model
        
        Args:
            html: Raw HTML content
            url: Source URL
            
        Returns:
            ScrapedContent object
        """
        # Process with all features
        result = self.process(html, url)
        
        # Extract links from media data or use basic links
        links = []
        if 'media' in result:
            # Create link objects from images
            for img in result.get('media', {}).get('images', []):
                links.append({
                    'url': img.get('url', ''),
                    'text': img.get('alt', ''),
                    'type': 'image'
                })
        else:
            links = result.get('links', [])
        
        # Extract images
        images = []
        if 'media' in result:
            images = result.get('media', {}).get('images', [])
        else:
            images = result.get('images', [])
        
        # Create ScrapedContent object
        return ScrapedContent(
            url=url,
            main_content=result.get('main_content', ''),
            metadata=result.get('metadata', {}),
            links=links[:100],  # Limit to first 100 links
            images=images[:50]  # Limit to first 50 images
        )
    
    def extract_content_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a concise summary of extraction results
        
        Args:
            result: Full processing result
            
        Returns:
            Concise summary dictionary
        """
        summary = {
            'url': result.get('url'),
            'title': result.get('metadata', {}).get('title', 'No title'),
            'description': result.get('metadata', {}).get('description', ''),
            'word_count': result.get('text_stats', {}).get('word_count', 0),
            'content_preview': result.get('main_content', '')[:200] + '...',
            'has_images': len(result.get('media', {}).get('images', [])) > 0,
            'has_videos': len(result.get('media', {}).get('videos', [])) > 0,
            'cms': result.get('cms', {}).get('detected'),
            'schema_types': result.get('structured_data', {}).get('schema_types', [])
        }
        
        return summary
    
    def compare_extractions(
        self, 
        html: str, 
        url: str
    ) -> Dict[str, Any]:
        """
        Compare different extraction methods for debugging/optimization
        
        Returns:
            Dictionary with results from different extraction strategies
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        comparisons = {}
        
        # Standard algorithm-based extraction
        standard_result = self.content_extractor.extract(html, url)
        comparisons['algorithm'] = {
            'content_length': len(standard_result['main_content']),
            'word_count': standard_result.get('text_stats', {}).get('word_count', 0),
            'preview': standard_result['main_content'][:100]
        }
        
        # CMS-optimized extraction
        cms_info = self.cms_detector.detect(soup, url)
        if cms_info and cms_info.get('cms'):
            cms_content = self.cms_detector.extract_with_cms_selectors(
                soup, cms_info['cms'], 'content'
            )
            if cms_content:
                comparisons['cms_optimized'] = {
                    'cms': cms_info['cms'],
                    'content_length': len(cms_content),
                    'word_count': len(cms_content.split()),
                    'preview': cms_content[:100]
                }
        
        # Semantic HTML extraction
        main_tag = soup.find('main') or soup.find('article')
        if main_tag:
            semantic_content = main_tag.get_text(separator=' ', strip=True)
            comparisons['semantic'] = {
                'content_length': len(semantic_content),
                'word_count': len(semantic_content.split()),
                'preview': semantic_content[:100]
            }
        
        return comparisons

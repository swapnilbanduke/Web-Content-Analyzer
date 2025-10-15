"""
CMS Detector - Identify and handle various Content Management Systems
Detects CMS patterns and provides optimized content selectors
"""
import logging
from typing import Dict, Optional, List, Any
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class CMSDetector:
    """
    Detect Content Management Systems and provide optimized extraction strategies
    
    Supports:
    - WordPress
    - Drupal
    - Joomla
    - Medium
    - Shopify
    - Wix
    - Squarespace
    - Ghost
    - Blogger
    - Custom CMS detection
    """
    
    # CMS detection patterns
    CMS_PATTERNS = {
        'WordPress': {
            'meta': [
                {'name': 'generator', 'content': re.compile(r'WordPress', re.I)},
            ],
            'classes': ['wp-content', 'wp-includes', 'wordpress'],
            'paths': ['/wp-content/', '/wp-includes/', '/wp-json/'],
            'selectors': {
                'content': [
                    'article.post',
                    '.entry-content',
                    '.post-content',
                    'main article',
                    '.content-area'
                ],
                'title': [
                    'h1.entry-title',
                    '.post-title',
                    'article h1'
                ],
                'author': [
                    '.author',
                    '.post-author',
                    'span.author'
                ],
                'date': [
                    'time.entry-date',
                    '.post-date',
                    '.published'
                ]
            }
        },
        'Drupal': {
            'meta': [
                {'name': 'generator', 'content': re.compile(r'Drupal', re.I)},
            ],
            'classes': ['drupal', 'region-content'],
            'paths': ['/sites/all/', '/sites/default/'],
            'attributes': ['data-drupal-selector'],
            'selectors': {
                'content': [
                    '.field--name-body',
                    '.node__content',
                    'article .content',
                    '.region-content'
                ],
                'title': [
                    'h1.page-title',
                    '.node-title'
                ]
            }
        },
        'Joomla': {
            'meta': [
                {'name': 'generator', 'content': re.compile(r'Joomla', re.I)},
            ],
            'classes': ['joomla', 'item-page'],
            'paths': ['/components/', '/modules/'],
            'selectors': {
                'content': [
                    '.item-page',
                    'div.article-content',
                    '.content-body'
                ]
            }
        },
        'Medium': {
            'meta': [
                {'property': 'al:android:app_name', 'content': 'Medium'},
                {'property': 'og:site_name', 'content': 'Medium'}
            ],
            'classes': ['medium', 'postArticle'],
            'domains': ['medium.com'],
            'selectors': {
                'content': [
                    'article section',
                    '.postArticle-content',
                    '[data-selectable-paragraph]'
                ],
                'title': [
                    'h1[data-testid="storyTitle"]',
                    '.graf--title'
                ],
                'author': [
                    'a[rel="author"]',
                    '[data-testid="authorName"]'
                ]
            }
        },
        'Shopify': {
            'meta': [
                {'name': 'shopify-digital-wallet'},
            ],
            'paths': ['/cdn.shopify.com/', 'myshopify.com'],
            'classes': ['shopify', 'product-single'],
            'selectors': {
                'content': [
                    '.product-single',
                    '.product-description',
                    '.rte'
                ],
                'title': [
                    'h1.product-single__title',
                    '.product-title'
                ],
                'price': [
                    '.product-single__price',
                    '.price'
                ]
            }
        },
        'Wix': {
            'meta': [
                {'name': 'generator', 'content': re.compile(r'Wix\.com', re.I)},
            ],
            'classes': ['wix', 'wix-ads'],
            'paths': ['static.wixstatic.com'],
            'selectors': {
                'content': [
                    '[data-mesh-id]',
                    '.comp-'
                ]
            }
        },
        'Squarespace': {
            'meta': [],
            'paths': ['static.squarespace.com', 'squarespace.com'],
            'classes': ['sqs', 'squarespace'],
            'selectors': {
                'content': [
                    '.sqs-block-content',
                    'article.entry',
                    '.Main-content'
                ],
                'title': [
                    'h1.entry-title'
                ]
            }
        },
        'Ghost': {
            'meta': [
                {'name': 'generator', 'content': re.compile(r'Ghost', re.I)},
            ],
            'classes': ['ghost', 'post-full'],
            'selectors': {
                'content': [
                    '.post-full-content',
                    '.post-content',
                    'article.post'
                ],
                'title': [
                    'h1.post-full-title',
                    '.post-title'
                ]
            }
        },
        'Blogger': {
            'meta': [
                {'name': 'generator', 'content': re.compile(r'Blogger', re.I)},
            ],
            'classes': ['blogger', 'post-body'],
            'domains': ['blogspot.com', 'blogger.com'],
            'selectors': {
                'content': [
                    '.post-body',
                    'article .post-content'
                ],
                'title': [
                    'h1.entry-title',
                    '.post-title'
                ]
            }
        },
        'Webflow': {
            'meta': [
                {'name': 'generator', 'content': re.compile(r'Webflow', re.I)},
            ],
            'paths': ['webflow.com'],
            'classes': ['w-'],
            'selectors': {
                'content': [
                    '.w-richtext',
                    '[data-w-id]'
                ]
            }
        }
    }
    
    def detect(self, soup: BeautifulSoup, url: str = '') -> Dict[str, Any]:
        """
        Detect CMS from HTML and URL
        
        Args:
            soup: BeautifulSoup parsed HTML
            url: Page URL (optional, helps with detection)
            
        Returns:
            Dictionary containing:
                - cms: Detected CMS name or None
                - confidence: Detection confidence (0-1)
                - selectors: Optimized CSS selectors for content
                - features: Detected CMS features
        """
        detection_scores = {}
        
        # Check each CMS
        for cms_name, patterns in self.CMS_PATTERNS.items():
            score = self._calculate_cms_score(soup, url, patterns)
            if score > 0:
                detection_scores[cms_name] = score
        
        # Get the CMS with highest score
        if detection_scores:
            detected_cms = max(detection_scores, key=detection_scores.get)
            confidence = min(detection_scores[detected_cms] / 100, 1.0)
            
            # Only return if confidence is reasonable
            if confidence >= 0.3:
                return {
                    'cms': detected_cms,
                    'confidence': confidence,
                    'selectors': self.CMS_PATTERNS[detected_cms].get('selectors', {}),
                    'all_scores': detection_scores
                }
        
        return {
            'cms': None,
            'confidence': 0.0,
            'selectors': {},
            'all_scores': detection_scores
        }
    
    def _calculate_cms_score(self, soup: BeautifulSoup, url: str, patterns: Dict) -> int:
        """Calculate detection score for a CMS"""
        score = 0
        
        # Check meta tags (30 points each)
        if 'meta' in patterns:
            for meta_pattern in patterns['meta']:
                meta_tag = soup.find('meta', attrs=meta_pattern)
                if meta_tag:
                    score += 30
        
        # Check for specific classes in HTML (10 points each, max 30)
        if 'classes' in patterns:
            class_matches = 0
            html_text = str(soup)
            
            for class_pattern in patterns['classes']:
                if class_pattern in html_text:
                    class_matches += 1
                    if class_matches <= 3:  # Max 3 matches counted
                        score += 10
        
        # Check for specific paths in links/scripts (15 points each, max 30)
        if 'paths' in patterns:
            path_matches = 0
            
            for link in soup.find_all(['link', 'script', 'a']):
                href = link.get('href', '') or link.get('src', '')
                
                for path_pattern in patterns['paths']:
                    if path_pattern in href:
                        path_matches += 1
                        if path_matches <= 2:  # Max 2 matches counted
                            score += 15
                        break
        
        # Check URL domain (20 points)
        if 'domains' in patterns and url:
            for domain in patterns['domains']:
                if domain in url:
                    score += 20
                    break
        
        # Check for specific attributes (10 points each)
        if 'attributes' in patterns:
            for attr in patterns['attributes']:
                if soup.find(attrs={attr: True}):
                    score += 10
        
        return score
    
    def get_optimal_selectors(self, cms: Optional[str], content_type: str = 'content') -> List[str]:
        """
        Get optimal CSS selectors for a detected CMS
        
        Args:
            cms: Detected CMS name
            content_type: Type of content ('content', 'title', 'author', 'date', etc.)
            
        Returns:
            List of CSS selectors to try
        """
        if not cms or cms not in self.CMS_PATTERNS:
            return []
        
        selectors = self.CMS_PATTERNS[cms].get('selectors', {})
        return selectors.get(content_type, [])
    
    def extract_with_cms_selectors(
        self, 
        soup: BeautifulSoup, 
        cms: str, 
        content_type: str = 'content'
    ) -> Optional[str]:
        """
        Extract content using CMS-specific selectors
        
        Args:
            soup: BeautifulSoup parsed HTML
            cms: CMS name
            content_type: Type of content to extract
            
        Returns:
            Extracted content or None
        """
        selectors = self.get_optimal_selectors(cms, content_type)
        
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    # Get text content
                    text = element.get_text(separator=' ', strip=True)
                    
                    # Clean up whitespace
                    text = re.sub(r'\s+', ' ', text)
                    
                    if text and len(text) > 10:  # Ensure meaningful content
                        logger.info(f"Extracted {content_type} using selector: {selector}")
                        return text
            
            except Exception as e:
                logger.debug(f"Selector '{selector}' failed: {e}")
                continue
        
        return None
    
    def get_cms_features(self, cms: Optional[str]) -> Dict[str, Any]:
        """
        Get known features and characteristics of a CMS
        
        Returns information about:
        - Typical content structure
        - Common plugins/extensions
        - SEO capabilities
        - Performance characteristics
        """
        features = {
            'WordPress': {
                'type': 'Blog/CMS',
                'content_structure': 'Post-based with categories and tags',
                'common_plugins': ['Yoast SEO', 'WooCommerce', 'Elementor'],
                'seo_friendly': True,
                'typical_use': 'Blogs, business websites, e-commerce'
            },
            'Drupal': {
                'type': 'Enterprise CMS',
                'content_structure': 'Node-based with flexible content types',
                'seo_friendly': True,
                'typical_use': 'Large enterprise websites, government sites'
            },
            'Joomla': {
                'type': 'CMS',
                'content_structure': 'Article-based',
                'seo_friendly': True,
                'typical_use': 'Community websites, corporate sites'
            },
            'Medium': {
                'type': 'Publishing platform',
                'content_structure': 'Story-based',
                'seo_friendly': True,
                'typical_use': 'Blogging, thought leadership'
            },
            'Shopify': {
                'type': 'E-commerce',
                'content_structure': 'Product-based',
                'seo_friendly': True,
                'typical_use': 'Online stores'
            },
            'Ghost': {
                'type': 'Publishing platform',
                'content_structure': 'Post-based, minimalist',
                'seo_friendly': True,
                'typical_use': 'Professional blogging'
            }
        }
        
        return features.get(cms, {'type': 'Unknown'})

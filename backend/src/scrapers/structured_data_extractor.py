"""
Structured Data Extractor - Extract JSON-LD, Microdata, and RDFa
Supports Schema.org structured data extraction
"""
import logging
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import json
import re

logger = logging.getLogger(__name__)


class StructuredDataExtractor:
    """
    Extract structured data from HTML pages
    
    Supports:
    - JSON-LD (Schema.org)
    - Microdata (Schema.org)
    - RDFa
    - Common schema types (Article, Product, Event, etc.)
    """
    
    def extract(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract all structured data from HTML
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            Dictionary containing:
                - json_ld: List of JSON-LD objects
                - microdata: Extracted microdata items
                - rdfa: RDFa properties
                - schema_types: Detected schema.org types
        """
        result = {}
        
        # Extract JSON-LD
        json_ld_data = self._extract_json_ld(soup)
        if json_ld_data:
            result['json_ld'] = json_ld_data
            result['schema_types'] = self._identify_schema_types(json_ld_data)
        
        # Extract Microdata
        microdata = self._extract_microdata(soup)
        if microdata:
            result['microdata'] = microdata
        
        # Extract RDFa
        rdfa = self._extract_rdfa(soup)
        if rdfa:
            result['rdfa'] = rdfa
        
        return result
    
    def _extract_json_ld(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract JSON-LD structured data"""
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        json_ld_data = []
        
        for script in json_ld_scripts:
            try:
                content = script.string
                if content:
                    # Parse JSON
                    data = json.loads(content)
                    
                    # Handle both single objects and arrays
                    if isinstance(data, list):
                        json_ld_data.extend(data)
                    else:
                        json_ld_data.append(data)
                        
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON-LD: {e}")
            except Exception as e:
                logger.error(f"Error extracting JSON-LD: {e}")
        
        return json_ld_data
    
    def _extract_microdata(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract Microdata structured data"""
        items = []
        
        # Find all itemscope elements (top-level)
        for element in soup.find_all(attrs={'itemscope': True}):
            # Skip nested items (they'll be processed as part of parent)
            if element.find_parent(attrs={'itemscope': True}):
                continue
            
            item = self._parse_microdata_item(element)
            if item:
                items.append(item)
        
        return items
    
    def _parse_microdata_item(self, element) -> Dict[str, Any]:
        """Parse a microdata item"""
        item = {}
        
        # Get item type
        item_type = element.get('itemtype', '')
        if item_type:
            item['@type'] = item_type.split('/')[-1]  # Get the last part (e.g., "Article")
        
        # Get item ID
        item_id = element.get('itemid')
        if item_id:
            item['@id'] = item_id
        
        # Extract properties
        properties = {}
        
        for prop_elem in element.find_all(attrs={'itemprop': True}):
            prop_name = prop_elem.get('itemprop')
            
            # Skip if this property belongs to a nested item
            parent_scope = prop_elem.find_parent(attrs={'itemscope': True})
            if parent_scope and parent_scope != element:
                continue
            
            # Get property value
            if prop_elem.has_attr('itemscope'):
                # Nested item
                prop_value = self._parse_microdata_item(prop_elem)
            elif prop_elem.has_attr('content'):
                prop_value = prop_elem.get('content')
            elif prop_elem.has_attr('datetime'):
                prop_value = prop_elem.get('datetime')
            elif prop_elem.has_attr('href'):
                prop_value = prop_elem.get('href')
            elif prop_elem.has_attr('src'):
                prop_value = prop_elem.get('src')
            else:
                prop_value = prop_elem.get_text(strip=True)
            
            # Handle multiple values for same property
            if prop_name in properties:
                if not isinstance(properties[prop_name], list):
                    properties[prop_name] = [properties[prop_name]]
                properties[prop_name].append(prop_value)
            else:
                properties[prop_name] = prop_value
        
        item.update(properties)
        return item
    
    def _extract_rdfa(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract RDFa structured data"""
        items = []
        
        # Find elements with typeof attribute (RDFa)
        for element in soup.find_all(attrs={'typeof': True}):
            item = {'@type': element.get('typeof')}
            
            # Extract properties
            properties = {}
            for prop_elem in element.find_all(attrs={'property': True}):
                prop_name = prop_elem.get('property')
                
                # Get value
                if prop_elem.has_attr('content'):
                    prop_value = prop_elem.get('content')
                elif prop_elem.has_attr('href'):
                    prop_value = prop_elem.get('href')
                else:
                    prop_value = prop_elem.get_text(strip=True)
                
                properties[prop_name] = prop_value
            
            if properties:
                item.update(properties)
                items.append(item)
        
        return items
    
    def _identify_schema_types(self, json_ld_data: List[Dict[str, Any]]) -> List[str]:
        """Identify Schema.org types from JSON-LD data"""
        schema_types = set()
        
        def extract_types(data):
            if isinstance(data, dict):
                if '@type' in data:
                    type_value = data['@type']
                    if isinstance(type_value, list):
                        schema_types.update(type_value)
                    else:
                        schema_types.add(type_value)
                
                # Recursively check nested objects
                for value in data.values():
                    extract_types(value)
            elif isinstance(data, list):
                for item in data:
                    extract_types(item)
        
        for item in json_ld_data:
            extract_types(item)
        
        return sorted(list(schema_types))
    
    def extract_article_data(self, structured_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract Article-specific data from structured data
        
        Looks for:
        - Article, NewsArticle, BlogPosting schema types
        - Returns normalized article data
        """
        article_types = {'Article', 'NewsArticle', 'BlogPosting', 'ScholarlyArticle', 'TechArticle'}
        
        # Check JSON-LD first
        if 'json_ld' in structured_data:
            for item in structured_data['json_ld']:
                item_type = item.get('@type', '')
                
                # Handle both single type and list of types
                types = [item_type] if isinstance(item_type, str) else item_type
                
                if any(t in article_types for t in types):
                    return self._normalize_article_data(item)
        
        # Check microdata
        if 'microdata' in structured_data:
            for item in structured_data['microdata']:
                if item.get('@type') in article_types:
                    return self._normalize_article_data(item)
        
        return None
    
    def extract_product_data(self, structured_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract Product-specific data from structured data"""
        # Check JSON-LD
        if 'json_ld' in structured_data:
            for item in structured_data['json_ld']:
                if item.get('@type') == 'Product':
                    return self._normalize_product_data(item)
        
        # Check microdata
        if 'microdata' in structured_data:
            for item in structured_data['microdata']:
                if item.get('@type') == 'Product':
                    return self._normalize_product_data(item)
        
        return None
    
    def extract_event_data(self, structured_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract Event-specific data from structured data"""
        event_types = {'Event', 'BusinessEvent', 'EducationEvent', 'SocialEvent'}
        
        # Check JSON-LD
        if 'json_ld' in structured_data:
            for item in structured_data['json_ld']:
                if item.get('@type') in event_types:
                    return self._normalize_event_data(item)
        
        # Check microdata
        if 'microdata' in structured_data:
            for item in structured_data['microdata']:
                if item.get('@type') in event_types:
                    return self._normalize_event_data(item)
        
        return None
    
    def _normalize_article_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize article data to common format"""
        normalized = {
            'type': data.get('@type', 'Article'),
            'headline': data.get('headline', ''),
            'description': data.get('description', ''),
            'author': self._extract_author(data.get('author')),
            'datePublished': data.get('datePublished', ''),
            'dateModified': data.get('dateModified', ''),
            'image': data.get('image', ''),
            'publisher': data.get('publisher', {}),
            'url': data.get('url', ''),
            'keywords': data.get('keywords', [])
        }
        
        # Handle articleBody
        if 'articleBody' in data:
            normalized['articleBody'] = data['articleBody']
        
        return normalized
    
    def _normalize_product_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize product data to common format"""
        normalized = {
            'type': 'Product',
            'name': data.get('name', ''),
            'description': data.get('description', ''),
            'image': data.get('image', ''),
            'brand': data.get('brand', {}),
            'offers': data.get('offers', {}),
            'aggregateRating': data.get('aggregateRating', {}),
            'review': data.get('review', [])
        }
        
        return normalized
    
    def _normalize_event_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize event data to common format"""
        normalized = {
            'type': data.get('@type', 'Event'),
            'name': data.get('name', ''),
            'description': data.get('description', ''),
            'startDate': data.get('startDate', ''),
            'endDate': data.get('endDate', ''),
            'location': data.get('location', {}),
            'organizer': data.get('organizer', {}),
            'performer': data.get('performer', []),
            'offers': data.get('offers', {})
        }
        
        return normalized
    
    def _extract_author(self, author_data: Any) -> Any:
        """Extract author information from various formats"""
        if isinstance(author_data, str):
            return {'name': author_data}
        elif isinstance(author_data, dict):
            return {
                'name': author_data.get('name', ''),
                'url': author_data.get('url', ''),
                'type': author_data.get('@type', '')
            }
        elif isinstance(author_data, list):
            return [self._extract_author(a) for a in author_data]
        
        return {}

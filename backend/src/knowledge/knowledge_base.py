"""
Knowledge Base

Central knowledge management system with indexing, categorization, and retrieval.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..storage.content_store import ContentStore
from ..storage.database import get_db

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """
    Intelligent knowledge base for managing scraped content.
    
    Features:
    - Content indexing and organization
    - Category management
    - Advanced search (keyword + filters)
    - Related content discovery
    - Statistics and insights
    """
    
    def __init__(self):
        """Initialize knowledge base"""
        self.store = ContentStore()
        self.db = get_db()
    
    # ==================== Indexing & Organization ====================
    
    def index_content(
        self,
        content_id: int,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Index content for better organization.
        
        Args:
            content_id: Content ID to index
            categories: List of categories
            tags: List of tags
            
        Returns:
            Success status
        """
        # TODO: Implement category/tag tables if needed
        logger.info(f"Indexed content {content_id}")
        return True
    
    # ==================== Search & Retrieval ====================
    
    def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base with filters.
        
        Args:
            query: Search query
            filters: Optional filters (domain, date_range, etc.)
            limit: Maximum results
            
        Returns:
            List of matching content with metadata
        """
        if not query.strip():
            # Return recent content if no query
            return self.get_recent_content(limit)
        
        # Full-text search
        results = self.store.search_content(query, limit)
        
        # Apply additional filters
        if filters:
            results = self._apply_filters(results, filters)
        
        # Enrich with analysis data
        enriched_results = []
        for result in results:
            # Get latest analysis for each type
            analyses = self.store.get_analyses_for_content(result['id'])
            result['analyses'] = {
                a['analysis_type']: a for a in analyses
            }
            enriched_results.append(result)
        
        return enriched_results
    
    def _apply_filters(
        self,
        results: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply additional filters to search results"""
        filtered = results
        
        # Filter by domain
        if 'domain' in filters and filters['domain']:
            filtered = [
                r for r in filtered 
                if r.get('domain') == filters['domain']
            ]
        
        # Filter by date range
        if 'date_from' in filters and filters['date_from']:
            filtered = [
                r for r in filtered 
                if r.get('scraped_at', '') >= filters['date_from']
            ]
        
        if 'date_to' in filters and filters['date_to']:
            filtered = [
                r for r in filtered 
                if r.get('scraped_at', '') <= filters['date_to']
            ]
        
        # Filter by minimum word count
        if 'min_words' in filters and filters['min_words']:
            filtered = [
                r for r in filtered 
                if r.get('word_count', 0) >= filters['min_words']
            ]
        
        return filtered
    
    def get_recent_content(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get most recently scraped content"""
        return self.store.list_content(limit, offset)
    
    def get_content_by_domain(
        self,
        domain: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all content from a specific domain"""
        query = """
            SELECT c.*, w.domain 
            FROM scraped_content c
            JOIN websites w ON c.website_id = w.id
            WHERE w.domain = ?
            ORDER BY c.scraped_at DESC
            LIMIT ?
        """
        return self.db.execute_query(query, (domain, limit))
    
    def find_related_content(
        self,
        content_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find content related to given content.
        
        Uses keywords and domain to find similar content.
        
        Args:
            content_id: Reference content ID
            limit: Maximum results
            
        Returns:
            List of related content
        """
        # Get original content
        content = self.store.get_content(content_id)
        if not content:
            return []
        
        # Get keywords from analysis
        analyses = self.store.get_analyses_for_content(content_id)
        keywords = []
        for analysis in analyses:
            if analysis.get('keywords'):
                keywords.extend(analysis['keywords'])
        
        if not keywords:
            # Fallback: same domain
            return self.get_content_by_domain(
                content.get('domain', ''),
                limit
            )
        
        # Search by keywords
        search_query = ' '.join(keywords[:5])  # Top 5 keywords
        results = self.store.search_content(search_query, limit + 1)
        
        # Exclude the original content
        related = [r for r in results if r['id'] != content_id]
        return related[:limit]
    
    # ==================== Statistics & Insights ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        stats = self.db.get_stats()
        
        # Add more insights
        query = """
            SELECT w.domain, COUNT(*) as count
            FROM scraped_content c
            JOIN websites w ON c.website_id = w.id
            GROUP BY w.domain
            ORDER BY count DESC
            LIMIT 10
        """
        top_domains = self.db.execute_query(query)
        stats['top_domains'] = top_domains
        
        # Analysis type distribution
        query = """
            SELECT analysis_type, COUNT(*) as count
            FROM analysis_results
            GROUP BY analysis_type
            ORDER BY count DESC
        """
        analysis_dist = self.db.execute_query(query)
        stats['analysis_distribution'] = analysis_dist
        
        # Recent activity
        query = """
            SELECT DATE(scraped_at) as date, COUNT(*) as count
            FROM scraped_content
            WHERE scraped_at >= date('now', '-30 days')
            GROUP BY DATE(scraped_at)
            ORDER BY date DESC
        """
        recent_activity = self.db.execute_query(query)
        stats['recent_activity'] = recent_activity
        
        return stats
    
    def get_all_domains(self) -> List[str]:
        """Get list of all domains in knowledge base"""
        query = "SELECT DISTINCT domain FROM websites ORDER BY domain"
        results = self.db.execute_query(query)
        return [r['domain'] for r in results]
    
    # ==================== Content Management ====================
    
    def get_content_details(self, content_id: int) -> Optional[Dict[str, Any]]:
        """
        Get complete details for a content item including all analyses.
        
        Args:
            content_id: Content ID
            
        Returns:
            Complete content details with analyses
        """
        content = self.store.get_content(content_id)
        if not content:
            return None
        
        # Get all analyses
        analyses = self.store.get_analyses_for_content(content_id)
        content['analyses'] = {
            a['analysis_type']: a for a in analyses
        }
        
        # Get website info
        website = self.store.get_website_by_id(content['website_id'])
        content['website'] = website
        
        return content
    
    def delete_content(self, content_id: int) -> bool:
        """Delete content from knowledge base"""
        return self.store.delete_content(content_id)
    
    def clear_old_content(self, days: int = 90) -> int:
        """
        Delete content older than specified days.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of items deleted
        """
        query = f"""
            DELETE FROM scraped_content 
            WHERE scraped_at < datetime('now', '-{days} days')
        """
        result = self.db.execute_query(query)
        logger.info(f"Deleted {result['rowcount']} old content items")
        return result['rowcount']

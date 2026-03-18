"""
Content Store

CRUD operations for storing and retrieving scraped content and analysis results.
"""

import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from urllib.parse import urlparse
import logging

from .database import DatabaseManager, get_db

logger = logging.getLogger(__name__)


class ContentStore:
    """Handles storage and retrieval of scraped content"""
    
    def __init__(self, db: Optional[DatabaseManager] = None):
        """
        Initialize content store.
        
        Args:
            db: Database manager instance (uses global if None)
        """
        self.db = db or get_db()
    
    # ==================== Website Operations ====================
    
    def save_website(
        self,
        url: str,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> int:
        """
        Save or update website information.
        
        Args:
            url: Website URL
            title: Page title
            description: Page description
            
        Returns:
            Website ID
        """
        domain = urlparse(url).netloc
        
        # Check if website exists
        existing = self.db.execute_query(
            "SELECT id, scrape_count FROM websites WHERE url = ?",
            (url,),
            fetch_one=True
        )
        
        if existing:
            # Update existing
            self.db.execute_query('''
                UPDATE websites 
                SET last_scraped = CURRENT_TIMESTAMP,
                    scrape_count = ?,
                    title = COALESCE(?, title),
                    description = COALESCE(?, description)
                WHERE id = ?
            ''', (existing['scrape_count'] + 1, title, description, existing['id']))
            return existing['id']
        else:
            # Insert new
            result = self.db.execute_query('''
                INSERT INTO websites (url, domain, title, description)
                VALUES (?, ?, ?, ?)
            ''', (url, domain, title, description))
            return result['lastrowid']
    
    def get_website(self, url: str) -> Optional[Dict[str, Any]]:
        """Get website by URL"""
        return self.db.execute_query(
            "SELECT * FROM websites WHERE url = ?",
            (url,),
            fetch_one=True
        )
    
    def get_website_by_id(self, website_id: int) -> Optional[Dict[str, Any]]:
        """Get website by ID"""
        return self.db.execute_query(
            "SELECT * FROM websites WHERE id = ?",
            (website_id,),
            fetch_one=True
        )
    
    def list_websites(
        self,
        limit: int = 100,
        offset: int = 0,
        domain: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all websites.
        
        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            domain: Filter by domain (optional)
            
        Returns:
            List of website records
        """
        if domain:
            query = """
                SELECT * FROM websites 
                WHERE domain = ?
                ORDER BY last_scraped DESC
                LIMIT ? OFFSET ?
            """
            params = (domain, limit, offset)
        else:
            query = """
                SELECT * FROM websites 
                ORDER BY last_scraped DESC
                LIMIT ? OFFSET ?
            """
            params = (limit, offset)
        
        return self.db.execute_query(query, params)
    
    # ==================== Content Operations ====================
    
    def save_content(
        self,
        url: str,
        title: Optional[str],
        content: str,
        main_content: Optional[str] = None,
        word_count: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
        headings: Optional[List[Dict[str, Any]]] = None,
        images: Optional[List[Dict[str, Any]]] = None,
        links: Optional[List[str]] = None
    ) -> int:
        """
        Save scraped content.
        
        Args:
            url: Content URL
            title: Page title
            content: Full content text
            main_content: Main content only
            word_count: Number of words
            metadata: Page metadata
            headings: List of headings
            images: List of images
            links: List of links
            
        Returns:
            Content ID
        """
        # Ensure website exists
        website_id = self.save_website(url, title)
        
        # Insert content
        result = self.db.execute_query('''
            INSERT INTO scraped_content (
                website_id, url, title, content, main_content, 
                word_count, metadata, headings, images, links
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            website_id, url, title, content, main_content,
            word_count,
            json.dumps(metadata) if metadata else None,
            json.dumps(headings) if headings else None,
            json.dumps(images) if images else None,
            json.dumps(links) if links else None
        ))
        
        content_id = result['lastrowid']
        
        # Add to full-text search
        keywords = json.dumps(metadata.get('keywords', [])) if metadata else None
        self.db.execute_query('''
            INSERT INTO content_fts (content_id, title, content, keywords)
            VALUES (?, ?, ?, ?)
        ''', (content_id, title or '', content, keywords or ''))
        
        logger.info(f"Saved content {content_id} for URL: {url}")
        return content_id
    
    def get_content(self, content_id: int) -> Optional[Dict[str, Any]]:
        """Get content by ID"""
        content = self.db.execute_query(
            "SELECT * FROM scraped_content WHERE id = ?",
            (content_id,),
            fetch_one=True
        )
        
        if content:
            # Parse JSON fields
            if content.get('metadata'):
                content['metadata'] = json.loads(content['metadata'])
            if content.get('headings'):
                content['headings'] = json.loads(content['headings'])
            if content.get('images'):
                content['images'] = json.loads(content['images'])
            if content.get('links'):
                content['links'] = json.loads(content['links'])
        
        return content
    
    def get_content_by_url(self, url: str, latest: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get content by URL.
        
        Args:
            url: Content URL
            latest: If True, return most recent; else return all
            
        Returns:
            Content record(s)
        """
        if latest:
            content = self.db.execute_query("""
                SELECT * FROM scraped_content 
                WHERE url = ?
                ORDER BY scraped_at DESC
                LIMIT 1
            """, (url,), fetch_one=True)
            
            if content and content.get('metadata'):
                content['metadata'] = json.loads(content['metadata'])
                if content.get('headings'):
                    content['headings'] = json.loads(content['headings'])
            
            return content
        else:
            contents = self.db.execute_query("""
                SELECT * FROM scraped_content 
                WHERE url = ?
                ORDER BY scraped_at DESC
            """, (url,))
            
            for content in contents:
                if content.get('metadata'):
                    content['metadata'] = json.loads(content['metadata'])
            
            return contents
    
    def list_content(
        self,
        limit: int = 50,
        offset: int = 0,
        website_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List all content.
        
        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            website_id: Filter by website ID (optional)
            
        Returns:
            List of content records
        """
        if website_id:
            query = """
                SELECT c.*, w.domain 
                FROM scraped_content c
                JOIN websites w ON c.website_id = w.id
                WHERE c.website_id = ?
                ORDER BY c.scraped_at DESC
                LIMIT ? OFFSET ?
            """
            params = (website_id, limit, offset)
        else:
            query = """
                SELECT c.*, w.domain 
                FROM scraped_content c
                JOIN websites w ON c.website_id = w.id
                ORDER BY c.scraped_at DESC
                LIMIT ? OFFSET ?
            """
            params = (limit, offset)
        
        return self.db.execute_query(query, params)
    
    def search_content(
        self,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Full-text search across content.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching content records
        """
        results = self.db.execute_query("""
            SELECT c.*, w.domain, rank
            FROM content_fts fts
            JOIN scraped_content c ON fts.content_id = c.id
            JOIN websites w ON c.website_id = w.id
            WHERE content_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))
        
        return results
    
    # ==================== Analysis Operations ====================
    
    def save_analysis(
        self,
        content_id: int,
        analysis_type: str,
        results: Dict[str, Any],
        scores: Optional[Dict[str, float]] = None,
        summary: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        llm_model: Optional[str] = None,
        processing_time_ms: float = 0.0
    ) -> int:
        """
        Save analysis results.
        
        Args:
            content_id: Content ID
            analysis_type: Type of analysis (seo, sentiment, readability, etc.)
            results: Complete analysis results
            scores: Analysis scores
            summary: Summary text
            keywords: Extracted keywords
            llm_model: LLM model used
            processing_time_ms: Processing time in milliseconds
            
        Returns:
            Analysis ID
        """
        result = self.db.execute_query('''
            INSERT INTO analysis_results (
                content_id, analysis_type, results, scores, 
                summary, keywords, llm_model, processing_time_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            content_id, analysis_type,
            json.dumps(results),
            json.dumps(scores) if scores else None,
            summary,
            json.dumps(keywords) if keywords else None,
            llm_model,
            processing_time_ms
        ))
        
        logger.info(f"Saved {analysis_type} analysis {result['lastrowid']} for content {content_id}")
        return result['lastrowid']
    
    def get_analysis(self, analysis_id: int) -> Optional[Dict[str, Any]]:
        """Get analysis by ID"""
        analysis = self.db.execute_query(
            "SELECT * FROM analysis_results WHERE id = ?",
            (analysis_id,),
            fetch_one=True
        )
        
        if analysis:
            analysis['results'] = json.loads(analysis['results'])
            if analysis.get('scores'):
                analysis['scores'] = json.loads(analysis['scores'])
            if analysis.get('keywords'):
                analysis['keywords'] = json.loads(analysis['keywords'])
        
        return analysis
    
    def get_analyses_for_content(
        self,
        content_id: int,
        analysis_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all analyses for a content item.
        
        Args:
            content_id: Content ID
            analysis_type: Filter by analysis type (optional)
            
        Returns:
            List of analysis records
        """
        if analysis_type:
            query = """
                SELECT * FROM analysis_results 
                WHERE content_id = ? AND analysis_type = ?
                ORDER BY analyzed_at DESC
            """
            params = (content_id, analysis_type)
        else:
            query = """
                SELECT * FROM analysis_results 
                WHERE content_id = ?
                ORDER BY analyzed_at DESC
            """
            params = (content_id,)
        
        analyses = self.db.execute_query(query, params)
        
        for analysis in analyses:
            analysis['results'] = json.loads(analysis['results'])
            if analysis.get('scores'):
                analysis['scores'] = json.loads(analysis['scores'])
            if analysis.get('keywords'):
                analysis['keywords'] = json.loads(analysis['keywords'])
        
        return analyses
    
    def delete_content(self, content_id: int) -> bool:
        """Delete content and all associated analyses"""
        result = self.db.execute_query(
            "DELETE FROM scraped_content WHERE id = ?",
            (content_id,)
        )
        return result['rowcount'] > 0
    
    def delete_website(self, website_id: int) -> bool:
        """Delete website and all associated content"""
        result = self.db.execute_query(
            "DELETE FROM websites WHERE id = ?",
            (website_id,)
        )
        return result['rowcount'] > 0

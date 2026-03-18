"""
Database Manager

SQLite database for storing scraped content and analysis results.
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database connections and operations"""
    
    def __init__(self, db_path: str = "data/knowledge_base.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()
    
    def _initialize_database(self):
        """Create tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Websites table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS websites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    domain TEXT NOT NULL,
                    title TEXT,
                    description TEXT,
                    first_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    scrape_count INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Scraped content table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scraped_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    website_id INTEGER NOT NULL,
                    url TEXT NOT NULL,
                    title TEXT,
                    content TEXT,
                    main_content TEXT,
                    word_count INTEGER,
                    metadata JSON,
                    headings JSON,
                    images JSON,
                    links JSON,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (website_id) REFERENCES websites(id) ON DELETE CASCADE
                )
            ''')
            
            # Analysis results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id INTEGER NOT NULL,
                    analysis_type TEXT NOT NULL,
                    results JSON NOT NULL,
                    scores JSON,
                    summary TEXT,
                    keywords JSON,
                    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    llm_model TEXT,
                    processing_time_ms REAL,
                    FOREIGN KEY (content_id) REFERENCES scraped_content(id) ON DELETE CASCADE
                )
            ''')
            
            # Content embeddings table (for semantic search)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content_embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id INTEGER NOT NULL,
                    chunk_text TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    embedding BLOB,
                    embedding_model TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (content_id) REFERENCES scraped_content(id) ON DELETE CASCADE
                )
            ''')
            
            # Create indexes for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_websites_domain ON websites(domain)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_websites_url ON websites(url)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_content_website ON scraped_content(website_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_analysis_content ON analysis_results(content_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_analysis_type ON analysis_results(analysis_type)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_embeddings_content ON content_embeddings(content_id)
            ''')
            
            # Full-text search virtual table
            cursor.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS content_fts USING fts5(
                    content_id UNINDEXED,
                    title,
                    content,
                    keywords
                )
            ''')
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def execute_query(
        self,
        query: str,
        params: tuple = (),
        fetch_one: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a database query.
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch_one: If True, return single result; else return all
            
        Returns:
            Query results as dict(s) or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                if fetch_one:
                    row = cursor.fetchone()
                    return dict(row) if row else None
                else:
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
            else:
                conn.commit()
                return {'lastrowid': cursor.lastrowid, 'rowcount': cursor.rowcount}
    
    def get_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            cursor.execute("SELECT COUNT(*) FROM websites")
            stats['total_websites'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM scraped_content")
            stats['total_content'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM analysis_results")
            stats['total_analyses'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM content_embeddings")
            stats['total_embeddings'] = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM websites 
                WHERE last_scraped >= datetime('now', '-7 days')
            """)
            stats['recent_scrapes'] = cursor.fetchone()[0]
            
            return stats


# Global database instance
_db_instance: Optional[DatabaseManager] = None


def get_db() -> DatabaseManager:
    """Get or create global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance

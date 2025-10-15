"""
Content Cleaner - Cleans and normalizes text content
"""
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class ContentCleaner:
    """
    Cleans and normalizes text content
    """
    
    def clean(self, text: str, aggressive: bool = False) -> str:
        """
        Clean and normalize text content
        
        Args:
            text: Input text to clean
            aggressive: If True, performs more aggressive cleaning
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        try:
            # Remove extra whitespace
            cleaned = self._normalize_whitespace(text)
            
            # Remove special characters (optional)
            if aggressive:
                cleaned = self._remove_special_chars(cleaned)
            
            # Fix common encoding issues
            cleaned = self._fix_encoding(cleaned)
            
            # Remove URLs (optional)
            if aggressive:
                cleaned = self._remove_urls(cleaned)
            
            # Remove email addresses (optional)
            if aggressive:
                cleaned = self._remove_emails(cleaned)
            
            return cleaned.strip()
            
        except Exception as e:
            logger.error(f"Content cleaning error: {str(e)}")
            return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text"""
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with double newline
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove trailing whitespace from lines
        lines = [line.rstrip() for line in text.split('\n')]
        
        return '\n'.join(lines)
    
    def _remove_special_chars(self, text: str) -> str:
        """Remove special characters (keeping basic punctuation)"""
        # Keep letters, numbers, and basic punctuation
        return re.sub(r'[^a-zA-Z0-9\s.,!?\-\'\"()]', '', text)
    
    def _fix_encoding(self, text: str) -> str:
        """Fix common encoding issues"""
        # Replace common HTML entities
        replacements = {
            '&nbsp;': ' ',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&mdash;': '—',
            '&ndash;': '–',
            '&rsquo;': ''',
            '&lsquo;': ''',
            '&rdquo;': '"',
            '&ldquo;': '"'
        }
        
        for entity, char in replacements.items():
            text = text.replace(entity, char)
        
        return text
    
    def _remove_urls(self, text: str) -> str:
        """Remove URLs from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.sub(url_pattern, '', text)
    
    def _remove_emails(self, text: str) -> str:
        """Remove email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.sub(email_pattern, '', text)

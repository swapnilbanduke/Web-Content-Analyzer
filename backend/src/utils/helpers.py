"""
Helper Functions - Utility helper functions
"""
import logging
from typing import Any, Dict
import json
from datetime import datetime

logger = logging.getLogger(__name__)


def format_timestamp(dt: datetime = None) -> str:
    """
    Format datetime as ISO string
    
    Args:
        dt: Datetime object (defaults to now)
        
    Returns:
        ISO formatted timestamp
    """
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()


def safe_json_dumps(data: Any, indent: int = 2) -> str:
    """
    Safely convert data to JSON string
    
    Args:
        data: Data to convert
        indent: JSON indentation
        
    Returns:
        JSON string or error message
    """
    try:
        return json.dumps(data, indent=indent, default=str)
    except Exception as e:
        logger.error(f"JSON serialization error: {str(e)}")
        return "{}"


def truncate_text(text: str, max_length: int = 1000) -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Merge two dictionaries
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    result.update(dict2)
    return result


def get_file_size_mb(content: str) -> float:
    """
    Get size of content in MB
    
    Args:
        content: Content string
        
    Returns:
        Size in MB
    """
    size_bytes = len(content.encode('utf-8'))
    return round(size_bytes / (1024 * 1024), 2)

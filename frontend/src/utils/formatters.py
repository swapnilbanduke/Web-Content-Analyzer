"""
Formatters - Data formatting utilities for display
"""
from typing import Any, Dict
import json
from datetime import datetime


def format_number(num: int) -> str:
    """
    Format number with thousands separator
    
    Args:
        num: Number to format
        
    Returns:
        Formatted number string
    """
    return f"{num:,}"


def format_filesize(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def format_timestamp(timestamp: str) -> str:
    """
    Format ISO timestamp to readable format
    
    Args:
        timestamp: ISO format timestamp
        
    Returns:
        Formatted timestamp
    """
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration
    """
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.2f}h"


def format_json(data: Any, indent: int = 2) -> str:
    """
    Format data as pretty JSON
    
    Args:
        data: Data to format
        indent: JSON indentation
        
    Returns:
        Formatted JSON string
    """
    try:
        return json.dumps(data, indent=indent, default=str)
    except:
        return str(data)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_list(items: list, separator: str = ", ", max_items: int = 5) -> str:
    """
    Format list as comma-separated string
    
    Args:
        items: List of items
        separator: Separator between items
        max_items: Maximum items to show
        
    Returns:
        Formatted string
    """
    if not items:
        return "None"
    
    if len(items) <= max_items:
        return separator.join(str(item) for item in items)
    
    shown_items = separator.join(str(item) for item in items[:max_items])
    remaining = len(items) - max_items
    return f"{shown_items} (+{remaining} more)"

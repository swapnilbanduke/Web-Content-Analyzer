"""
Validators - Frontend input validation
"""
import re
from urllib.parse import urlparse


def validate_url(url: str) -> tuple[bool, str]:
    """
    Validate URL format
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL cannot be empty"
    
    # Remove whitespace
    url = url.strip()
    
    # Check minimum length
    if len(url) < 10:
        return False, "URL is too short"
    
    # Parse URL
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if not parsed.scheme:
            return False, "URL must include http:// or https://"
        
        if parsed.scheme not in ['http', 'https']:
            return False, "Only HTTP and HTTPS URLs are supported"
        
        # Check netloc (domain)
        if not parsed.netloc:
            return False, "URL must include a domain name"
        
        # Check for localhost (optional - can be disabled)
        if 'localhost' in parsed.netloc or '127.0.0.1' in parsed.netloc:
            return False, "Localhost URLs are not allowed"
        
        return True, ""
        
    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"


def validate_url_list(urls: list) -> tuple[bool, str, list]:
    """
    Validate list of URLs
    
    Args:
        urls: List of URLs to validate
        
    Returns:
        Tuple of (is_valid, error_message, valid_urls)
    """
    if not urls:
        return False, "URL list cannot be empty", []
    
    if len(urls) > 10:
        return False, "Maximum 10 URLs allowed", []
    
    valid_urls = []
    invalid_urls = []
    
    for url in urls:
        is_valid, error = validate_url(url)
        if is_valid:
            valid_urls.append(url)
        else:
            invalid_urls.append(f"{url}: {error}")
    
    if invalid_urls:
        error_msg = "Invalid URLs:\n" + "\n".join(invalid_urls)
        return False, error_msg, valid_urls
    
    return True, "", valid_urls


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file operations
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    max_length = 200
    if len(filename) > max_length:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        name = name[:max_length - len(ext) - 1]
        filename = f"{name}.{ext}" if ext else name
    
    return filename

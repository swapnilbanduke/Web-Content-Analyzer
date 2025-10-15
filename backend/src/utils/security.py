"""
Comprehensive Security Module
Implements SSRF prevention, URL validation, content sanitization,
file type validation, and malicious content detection.
"""
import html
import re
from urllib.parse import urlparse, parse_qs
from typing import List, Optional, Set, Dict, Any, Tuple
import logging
import ipaddress
import mimetypes
from io import BytesIO

logger = logging.getLogger(__name__)


# ============================================================================
# SSRF Prevention and URL Validation
# ============================================================================

class URLValidator:
    """
    Comprehensive URL validation to prevent SSRF and other attacks
    
    Features:
    - Private IP range blocking (RFC 1918)
    - Localhost/loopback blocking
    - Protocol whitelist/blacklist
    - Domain whitelist/blacklist
    - Suspicious pattern detection
    """
    
    # Private IP ranges (RFC 1918)
    PRIVATE_IP_RANGES = [
        ipaddress.ip_network('10.0.0.0/8'),        # Class A private
        ipaddress.ip_network('172.16.0.0/12'),     # Class B private
        ipaddress.ip_network('192.168.0.0/16'),    # Class C private
        ipaddress.ip_network('127.0.0.0/8'),       # Loopback
        ipaddress.ip_network('169.254.0.0/16'),    # Link-local
        ipaddress.ip_network('::1/128'),           # IPv6 loopback
        ipaddress.ip_network('fc00::/7'),          # IPv6 private
        ipaddress.ip_network('fe80::/10'),         # IPv6 link-local
    ]
    
    # Dangerous protocols
    DANGEROUS_PROTOCOLS = {
        'javascript', 'data', 'file', 'vbscript', 'about',
        'jar', 'ftp', 'sftp', 'ssh', 'telnet', 'ldap'
    }
    
    # Allowed protocols
    ALLOWED_PROTOCOLS = {'http', 'https'}
    
    # Suspicious patterns in URLs
    SUSPICIOUS_PATTERNS = [
        r'@',              # Credentials in URL
        r'\.\./',          # Directory traversal
        r'%00',            # Null byte
        r'%0[ad]',         # CRLF injection
        r'<script',        # XSS attempt
        r'javascript:',    # Protocol bypass
    ]
    
    def __init__(
        self,
        allowed_protocols: Optional[Set[str]] = None,
        blocked_domains: Optional[Set[str]] = None,
        allowed_domains: Optional[Set[str]] = None,
        block_private_ips: bool = True
    ):
        """
        Initialize URL validator
        
        Args:
            allowed_protocols: Set of allowed protocols (default: http, https)
            blocked_domains: Set of blocked domains
            allowed_domains: Set of allowed domains (None = allow all)
            block_private_ips: Block private IP ranges
        """
        self.allowed_protocols = allowed_protocols or self.ALLOWED_PROTOCOLS
        self.blocked_domains = blocked_domains or set()
        self.allowed_domains = allowed_domains
        self.block_private_ips = block_private_ips
    
    def validate_url(self, url: str, raise_exception: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive URL validation
        
        Args:
            url: URL to validate
            raise_exception: Raise exception on validation failure
            
        Returns:
            Tuple of (is_valid, error_message)
            
        Raises:
            ValueError: If raise_exception=True and validation fails
        """
        try:
            # Basic validation
            if not url or not isinstance(url, str):
                return self._handle_error("URL must be a non-empty string", raise_exception)
            
            url = url.strip()
            
            if len(url) > 2048:  # Max URL length
                return self._handle_error("URL exceeds maximum length (2048)", raise_exception)
            
            # Parse URL
            try:
                parsed = urlparse(url)
            except Exception as e:
                return self._handle_error(f"Invalid URL format: {e}", raise_exception)
            
            # Check protocol
            protocol = parsed.scheme.lower()
            if protocol not in self.allowed_protocols:
                if protocol in self.DANGEROUS_PROTOCOLS:
                    return self._handle_error(f"Dangerous protocol: {protocol}", raise_exception)
                return self._handle_error(f"Protocol not allowed: {protocol}", raise_exception)
            
            # Check for suspicious patterns
            url_lower = url.lower()
            for pattern in self.SUSPICIOUS_PATTERNS:
                if re.search(pattern, url_lower, re.IGNORECASE):
                    return self._handle_error(f"Suspicious pattern detected: {pattern}", raise_exception)
            
            # Check hostname
            hostname = parsed.hostname
            if not hostname:
                return self._handle_error("Missing hostname", raise_exception)
            
            # Check domain whitelist/blacklist
            if self.allowed_domains and hostname not in self.allowed_domains:
                return self._handle_error(f"Domain not in whitelist: {hostname}", raise_exception)
            
            if hostname in self.blocked_domains:
                return self._handle_error(f"Domain is blocked: {hostname}", raise_exception)
            
            # Check for private IPs
            if self.block_private_ips:
                is_private, error = self._check_private_ip(hostname)
                if is_private:
                    return self._handle_error(error or "Private IP address detected", raise_exception)
            
            # Check for localhost variations
            if self._is_localhost(hostname):
                return self._handle_error("Localhost access is blocked", raise_exception)
            
            return True, None
            
        except Exception as e:
            logger.exception("URL validation error")
            return self._handle_error(f"Validation error: {e}", raise_exception)
    
    def _check_private_ip(self, hostname: str) -> Tuple[bool, Optional[str]]:
        """Check if hostname resolves to private IP"""
        try:
            # Try to parse as IP address
            ip = ipaddress.ip_address(hostname)
            
            # Check against private ranges
            for network in self.PRIVATE_IP_RANGES:
                if ip in network:
                    return True, f"Private IP range detected: {network}"
            
            return False, None
            
        except ValueError:
            # Not an IP address, hostname will be resolved later
            # In production, you might want to resolve and check
            return False, None
    
    def _is_localhost(self, hostname: str) -> bool:
        """Check if hostname is localhost"""
        localhost_names = {
            'localhost', '127.0.0.1', '::1',
            '0.0.0.0', 'localhost.localdomain'
        }
        return hostname.lower() in localhost_names
    
    def _handle_error(self, message: str, raise_exception: bool) -> Tuple[bool, str]:
        """Handle validation error"""
        logger.warning(f"URL validation failed: {message}")
        if raise_exception:
            raise ValueError(f"URL validation failed: {message}")
        return False, message


# ============================================================================
# Content Size Validation
# ============================================================================

class ContentSizeValidator:
    """
    Content size validation and limits
    
    Features:
    - Maximum content size limits
    - Progressive size checking
    - Memory-safe content handling
    """
    
    # Default limits (in bytes)
    DEFAULT_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
    DEFAULT_WARNING_SIZE = 5 * 1024 * 1024  # 5 MB
    
    def __init__(
        self,
        max_size: int = DEFAULT_MAX_SIZE,
        warning_size: int = DEFAULT_WARNING_SIZE
    ):
        """
        Initialize content size validator
        
        Args:
            max_size: Maximum allowed content size in bytes
            warning_size: Warning threshold in bytes
        """
        self.max_size = max_size
        self.warning_size = warning_size
    
    def validate_size(
        self,
        content_length: Optional[int],
        raise_exception: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate content size
        
        Args:
            content_length: Content length in bytes
            raise_exception: Raise exception on validation failure
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if content_length is None:
            logger.warning("Content length is unknown, cannot validate size")
            return True, None
        
        if content_length > self.max_size:
            message = f"Content size ({content_length} bytes) exceeds maximum ({self.max_size} bytes)"
            logger.error(message)
            if raise_exception:
                raise ValueError(message)
            return False, message
        
        if content_length > self.warning_size:
            logger.warning(f"Content size ({content_length} bytes) exceeds warning threshold ({self.warning_size} bytes)")
        
        return True, None
    
    def validate_content(
        self,
        content: str,
        raise_exception: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate actual content size
        
        Args:
            content: Content to validate
            raise_exception: Raise exception on validation failure
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        content_length = len(content.encode('utf-8'))
        return self.validate_size(content_length, raise_exception)


# ============================================================================
# File Type Validation
# ============================================================================

class FileTypeValidator:
    """
    File type and MIME type validation
    
    Features:
    - MIME type validation
    - Extension whitelist
    - Content type checking
    - Magic number verification (basic)
    """
    
    # Allowed MIME types for web content
    ALLOWED_MIME_TYPES = {
        'text/html',
        'text/plain',
        'text/xml',
        'application/xhtml+xml',
        'application/xml',
        'text/html; charset=utf-8',
        'text/html; charset=UTF-8',
    }
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'.html', '.htm', '.xml', '.xhtml', '.txt'}
    
    # Magic numbers (file signatures) for common formats
    MAGIC_NUMBERS = {
        b'<!DOCTYPE': 'html',
        b'<html': 'html',
        b'<?xml': 'xml',
        b'<\x00?xml': 'xml',  # UTF-16
    }
    
    def __init__(
        self,
        allowed_mime_types: Optional[Set[str]] = None,
        allowed_extensions: Optional[Set[str]] = None
    ):
        """
        Initialize file type validator
        
        Args:
            allowed_mime_types: Set of allowed MIME types
            allowed_extensions: Set of allowed file extensions
        """
        self.allowed_mime_types = allowed_mime_types or self.ALLOWED_MIME_TYPES
        self.allowed_extensions = allowed_extensions or self.ALLOWED_EXTENSIONS
    
    def validate_mime_type(
        self,
        mime_type: str,
        raise_exception: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate MIME type
        
        Args:
            mime_type: MIME type to validate
            raise_exception: Raise exception on validation failure
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not mime_type:
            return True, None  # Allow if not specified
        
        # Normalize MIME type (remove parameters)
        base_mime = mime_type.split(';')[0].strip().lower()
        
        # Check if base MIME type is allowed
        is_allowed = any(
            base_mime == allowed.split(';')[0].strip().lower()
            for allowed in self.allowed_mime_types
        )
        
        if not is_allowed:
            message = f"MIME type not allowed: {mime_type}"
            logger.warning(message)
            if raise_exception:
                raise ValueError(message)
            return False, message
        
        return True, None
    
    def validate_extension(
        self,
        url: str,
        raise_exception: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate file extension from URL
        
        Args:
            url: URL to check
            raise_exception: Raise exception on validation failure
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # Check if path has an extension
        if '.' not in path.split('/')[-1]:
            return True, None  # No extension, allow
        
        # Get extension
        extension = '.' + path.split('.')[-1]
        
        if extension not in self.allowed_extensions:
            message = f"File extension not allowed: {extension}"
            logger.warning(message)
            if raise_exception:
                raise ValueError(message)
            return False, message
        
        return True, None
    
    def detect_content_type(self, content: bytes) -> Optional[str]:
        """
        Detect content type from magic numbers
        
        Args:
            content: First bytes of content
            
        Returns:
            Detected content type or None
        """
        for magic, ctype in self.MAGIC_NUMBERS.items():
            if content.startswith(magic):
                return ctype
        
        return None


# ============================================================================
# XSS Prevention and Content Sanitization
# ============================================================================

class ContentSanitizer:
    """
    XSS prevention and content sanitization
    
    Features:
    - HTML entity encoding
    - Dangerous tag removal
    - Script/iframe filtering
    - Event handler removal
    - Safe content rendering
    """
    
    # Dangerous HTML tags
    DANGEROUS_TAGS = {
        'script', 'iframe', 'embed', 'object', 'applet',
        'frame', 'frameset', 'meta', 'link', 'style',
        'base', 'form', 'input', 'button', 'textarea'
    }
    
    # Dangerous attributes
    DANGEROUS_ATTRIBUTES = {
        'onclick', 'onerror', 'onload', 'onmouseover', 'onmouseout',
        'onfocus', 'onblur', 'onchange', 'onsubmit', 'onkeypress',
        'onkeydown', 'onkeyup', 'onabort', 'ondblclick', 'ondrag'
    }
    
    # Dangerous protocols in attributes
    DANGEROUS_PROTOCOLS = {
        'javascript:', 'data:', 'vbscript:', 'file:', 'about:'
    }
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize content sanitizer
        
        Args:
            strict_mode: Enable strict sanitization
        """
        self.strict_mode = strict_mode
    
    def sanitize_html(self, content: str) -> str:
        """
        Sanitize HTML content to prevent XSS
        
        Args:
            content: HTML content to sanitize
            
        Returns:
            Sanitized content
        """
        if self.strict_mode:
            # Strict mode: escape all HTML
            return html.escape(content)
        else:
            # Less strict: remove dangerous elements
            sanitized = content
            
            # Remove dangerous tags
            for tag in self.DANGEROUS_TAGS:
                pattern = rf'<{tag}[^>]*>.*?</{tag}>|<{tag}[^>]*/>'
                sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
            
            # Remove event handlers
            for attr in self.DANGEROUS_ATTRIBUTES:
                pattern = rf'\s{attr}\s*=\s*["\'][^"\']*["\']'
                sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
            
            # Remove dangerous protocols
            for protocol in self.DANGEROUS_PROTOCOLS:
                pattern = rf'(href|src)\s*=\s*["\']?\s*{re.escape(protocol)}'
                sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
            
            return sanitized
    
    def sanitize_text(self, text: str) -> str:
        """
        Sanitize plain text (escape HTML entities)
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        return html.escape(text)
    
    def strip_dangerous_content(self, content: str) -> str:
        """
        Strip all dangerous content aggressively
        
        Args:
            content: Content to sanitize
            
        Returns:
            Sanitized content
        """
        # Remove all script tags and content
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove all style tags and content
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove all iframes
        content = re.sub(r'<iframe[^>]*>.*?</iframe>', '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove all event handlers
        content = re.sub(r'\son\w+\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
        
        # Remove javascript: and data: URLs
        content = re.sub(r'(href|src)\s*=\s*["\']?\s*(javascript|data):', '', content, flags=re.IGNORECASE)
        
        return content


# ============================================================================
# Malicious Content Detection
# ============================================================================

class MaliciousContentDetector:
    """
    Detect malicious patterns in content
    
    Features:
    - SQL injection pattern detection
    - XSS pattern detection
    - Path traversal detection
    - Command injection detection
    """
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(UNION\s+SELECT)",
        r"(--|\#|\/\*|\*\/)",
        r"(\bOR\b\s+\d+\s*=\s*\d+)",
        r"('\s+OR\s+')",
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
        r"<iframe[^>]*>",
        r"eval\s*\(",
        r"alert\s*\(",
    ]
    
    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e%2f",
        r"%2e%2e/",
        r"..%2f",
        r"%2e%2e%5c",
    ]
    
    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r";\s*(ls|cat|wget|curl|nc|bash|sh|cmd|powershell)",
        r"\|\s*(ls|cat|wget|curl|nc|bash|sh|cmd|powershell)",
        r"`.*`",
        r"\$\(.*\)",
    ]
    
    def __init__(self):
        """Initialize malicious content detector"""
        self.compiled_patterns = {
            'sql': [re.compile(p, re.IGNORECASE) for p in self.SQL_INJECTION_PATTERNS],
            'xss': [re.compile(p, re.IGNORECASE) for p in self.XSS_PATTERNS],
            'path': [re.compile(p, re.IGNORECASE) for p in self.PATH_TRAVERSAL_PATTERNS],
            'command': [re.compile(p, re.IGNORECASE) for p in self.COMMAND_INJECTION_PATTERNS],
        }
    
    def detect_malicious_patterns(
        self,
        content: str,
        check_types: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """
        Detect malicious patterns in content
        
        Args:
            content: Content to check
            check_types: Types of checks to perform (sql, xss, path, command)
            
        Returns:
            Dictionary of detected patterns by type
        """
        if check_types is None:
            check_types = ['sql', 'xss', 'path', 'command']
        
        detected = {}
        
        for check_type in check_types:
            if check_type not in self.compiled_patterns:
                continue
            
            matches = []
            for pattern in self.compiled_patterns[check_type]:
                found = pattern.findall(content)
                if found:
                    matches.extend(found)
            
            if matches:
                detected[check_type] = matches
                logger.warning(f"Malicious {check_type} patterns detected: {matches}")
        
        return detected
    
    def is_malicious(
        self,
        content: str,
        check_types: Optional[List[str]] = None
    ) -> bool:
        """
        Check if content contains malicious patterns
        
        Args:
            content: Content to check
            check_types: Types of checks to perform
            
        Returns:
            True if malicious patterns detected
        """
        detected = self.detect_malicious_patterns(content, check_types)
        return len(detected) > 0


# ============================================================================
# Legacy Functions (for backward compatibility)
# ============================================================================

def sanitize_url(url: str) -> str:
    """
    Remove dangerous characters and protocols from URL (Legacy)
    
    Note: Use URLValidator for comprehensive validation
    
    Args:
        url: URL to sanitize
        
    Returns:
        Sanitized URL or empty string if invalid
    """
    validator = URLValidator()
    is_valid, error = validator.validate_url(url, raise_exception=False)
    if not is_valid:
        logger.warning(f"URL sanitization failed: {error}")
        return ""
    return url


def sanitize_html(content: str) -> str:
    """
    Escape HTML special characters (Legacy)
    
    Note: Use ContentSanitizer for comprehensive sanitization
    
    Args:
        content: HTML content to sanitize
        
    Returns:
        Sanitized content
    """
    sanitizer = ContentSanitizer(strict_mode=True)
    return sanitizer.sanitize_html(content)


def is_safe_url(url: str) -> bool:
    """
    Check if URL is safe to fetch (Legacy)
    
    Note: Use URLValidator for comprehensive validation
    
    Args:
        url: URL to check
        
    Returns:
        True if URL is safe
    """
    validator = URLValidator()
    is_valid, _ = validator.validate_url(url, raise_exception=False)
    return is_valid


def validate_content_length(content: str, max_length: int = 1000000) -> bool:
    """
    Validate content length to prevent memory issues (Legacy)
    
    Note: Use ContentSizeValidator for better control
    
    Args:
        content: Content to validate
        max_length: Maximum allowed length
        
    Returns:
        True if content length is acceptable
    """
    validator = ContentSizeValidator(max_size=max_length)
    is_valid, _ = validator.validate_content(content, raise_exception=False)
    return is_valid


def remove_sensitive_data(text: str) -> str:
    """
    Remove potential sensitive data from text
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    
    # Remove phone numbers (simple pattern)
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    
    # Remove credit card numbers (simple pattern)
    text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]', text)
    
    return text


class ContentFilter:
    """
    Filter and validate scraped content (Legacy)
    
    Note: Use ContentSizeValidator and FileTypeValidator for better control
    """
    
    def __init__(self, max_size: int = 10 * 1024 * 1024):  # 10MB default
        self.max_size = max_size
        self.size_validator = ContentSizeValidator(max_size=max_size)
        self.file_validator = FileTypeValidator()
    
    def validate_content_type(self, content_type: str) -> bool:
        """Validate if content type is allowed"""
        is_valid, _ = self.file_validator.validate_mime_type(
            content_type, 
            raise_exception=False
        )
        return is_valid
    
    def validate_size(self, content_length: int) -> bool:
        """Validate if content size is within limits"""
        is_valid, _ = self.size_validator.validate_size(
            content_length, 
            raise_exception=False
        )
        return is_valid


# ============================================================================
# Utility Functions
# ============================================================================

def create_secure_validator(
    max_size: int = 10 * 1024 * 1024,
    allowed_domains: Optional[Set[str]] = None,
    blocked_domains: Optional[Set[str]] = None,
    block_private_ips: bool = True,
    strict_sanitization: bool = True
) -> Dict[str, Any]:
    """
    Create a set of security validators with common configuration
    
    Args:
        max_size: Maximum content size in bytes
        allowed_domains: Set of allowed domains (None = allow all)
        blocked_domains: Set of blocked domains
        block_private_ips: Block private IP ranges
        strict_sanitization: Enable strict HTML sanitization
        
    Returns:
        Dictionary of configured validators
    """
    return {
        'url_validator': URLValidator(
            allowed_domains=allowed_domains,
            blocked_domains=blocked_domains,
            block_private_ips=block_private_ips
        ),
        'size_validator': ContentSizeValidator(max_size=max_size),
        'file_validator': FileTypeValidator(),
        'sanitizer': ContentSanitizer(strict_mode=strict_sanitization),
        'malicious_detector': MaliciousContentDetector()
    }


def validate_request(
    url: str,
    content_length: Optional[int] = None,
    content_type: Optional[str] = None,
    validators: Optional[Dict[str, Any]] = None
) -> Tuple[bool, Optional[str]]:
    """
    Comprehensive request validation
    
    Args:
        url: URL to validate
        content_length: Expected content length
        content_type: Expected content type
        validators: Pre-configured validators (or create new ones)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if validators is None:
        validators = create_secure_validator()
    
    # Validate URL
    is_valid, error = validators['url_validator'].validate_url(url, raise_exception=False)
    if not is_valid:
        return False, f"URL validation failed: {error}"
    
    # Validate content size
    if content_length:
        is_valid, error = validators['size_validator'].validate_size(
            content_length, 
            raise_exception=False
        )
        if not is_valid:
            return False, f"Size validation failed: {error}"
    
    # Validate content type
    if content_type:
        is_valid, error = validators['file_validator'].validate_mime_type(
            content_type, 
            raise_exception=False
        )
        if not is_valid:
            return False, f"Content type validation failed: {error}"
    
    return True, None


def sanitize_and_validate_content(
    content: str,
    check_malicious: bool = True,
    sanitize: bool = True,
    validators: Optional[Dict[str, Any]] = None
) -> Tuple[str, Dict[str, Any]]:
    """
    Sanitize and validate content
    
    Args:
        content: Content to process
        check_malicious: Check for malicious patterns
        sanitize: Sanitize the content
        validators: Pre-configured validators
        
    Returns:
        Tuple of (sanitized_content, validation_results)
    """
    if validators is None:
        validators = create_secure_validator()
    
    results = {
        'malicious_patterns': {},
        'sanitized': False,
        'safe': True
    }
    
    # Check for malicious patterns
    if check_malicious:
        detector = validators['malicious_detector']
        patterns = detector.detect_malicious_patterns(content)
        results['malicious_patterns'] = patterns
        if patterns:
            results['safe'] = False
            logger.warning(f"Malicious patterns detected: {patterns}")
    
    # Sanitize content
    if sanitize:
        sanitizer = validators['sanitizer']
        content = sanitizer.strip_dangerous_content(content)
        results['sanitized'] = True
    
    return content, results


__all__ = [
    'URLValidator',
    'ContentSizeValidator',
    'FileTypeValidator',
    'ContentSanitizer',
    'MaliciousContentDetector',
    'ContentFilter',
    'sanitize_url',
    'sanitize_html',
    'is_safe_url',
    'validate_content_length',
    'remove_sensitive_data',
    'create_secure_validator',
    'validate_request',
    'sanitize_and_validate_content',
]

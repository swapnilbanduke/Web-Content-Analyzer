"""
Validators - URL validation and SSRF prevention
"""
import re
from urllib.parse import urlparse
import ipaddress
import logging

logger = logging.getLogger(__name__)


class URLValidator:
    """
    URL validation and security checks
    """
    
    # Blocked IP ranges for SSRF prevention
    BLOCKED_IP_RANGES = [
        ipaddress.ip_network('127.0.0.0/8'),      # Loopback
        ipaddress.ip_network('10.0.0.0/8'),       # Private
        ipaddress.ip_network('172.16.0.0/12'),    # Private
        ipaddress.ip_network('192.168.0.0/16'),   # Private
        ipaddress.ip_network('169.254.0.0/16'),   # Link-local
        ipaddress.ip_network('::1/128'),          # IPv6 loopback
        ipaddress.ip_network('fc00::/7'),         # IPv6 private
    ]
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Validate URL format and safety
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid and safe
        """
        try:
            # Parse URL
            parsed = urlparse(str(url))
            
            # Check scheme
            if parsed.scheme not in ['http', 'https']:
                logger.warning(f"Invalid URL scheme: {parsed.scheme}")
                return False
            
            # Check if hostname exists
            if not parsed.netloc:
                logger.warning("URL missing hostname")
                return False
            
            # Check for IP address and validate if present
            hostname = parsed.hostname
            if hostname:
                if URLValidator._is_ip_address(hostname):
                    if not URLValidator._is_ip_allowed(hostname):
                        logger.warning(f"Blocked IP address: {hostname}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"URL validation error: {str(e)}")
            return False
    
    @staticmethod
    def _is_ip_address(hostname: str) -> bool:
        """Check if hostname is an IP address"""
        try:
            ipaddress.ip_address(hostname)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def _is_ip_allowed(ip_str: str) -> bool:
        """
        Check if IP address is allowed (not in blocked ranges)
        """
        try:
            ip = ipaddress.ip_address(ip_str)
            
            # Check against blocked ranges
            for blocked_range in URLValidator.BLOCKED_IP_RANGES:
                if ip in blocked_range:
                    return False
            
            return True
            
        except ValueError:
            return False
    
    @staticmethod
    def sanitize_url(url: str) -> str:
        """
        Sanitize URL by removing potentially dangerous elements
        """
        # Remove any whitespace
        url = url.strip()
        
        # Remove javascript: and data: schemes
        if url.lower().startswith(('javascript:', 'data:', 'file:')):
            raise ValueError(f"Dangerous URL scheme detected")
        
        return url

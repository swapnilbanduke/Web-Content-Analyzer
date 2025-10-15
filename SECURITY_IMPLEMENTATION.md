# Security Implementation Guide

## Overview

This document describes the comprehensive security implementation for the Web Content Analyzer. The security module provides multiple layers of protection against common web security threats including SSRF, XSS, SQL injection, path traversal, and other attacks.

## Table of Contents

1. [Threat Model](#threat-model)
2. [Security Components](#security-components)
3. [Features](#features)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Best Practices](#best-practices)
7. [Testing](#testing)
8. [Incident Response](#incident-response)

## Threat Model

### Attack Vectors

The Web Content Analyzer is vulnerable to several attack vectors:

1. **Server-Side Request Forgery (SSRF)**
   - Attacker provides malicious URLs targeting internal infrastructure
   - Accessing cloud metadata endpoints (169.254.169.254)
   - Port scanning internal networks
   - Accessing internal services (localhost, private IPs)

2. **Cross-Site Scripting (XSS)**
   - Malicious scripts in scraped content
   - JavaScript injection through content rendering
   - Event handler injection

3. **Content Injection**
   - SQL injection patterns in content
   - Command injection attempts
   - Path traversal sequences

4. **Denial of Service (DoS)**
   - Extremely large content payloads
   - Memory exhaustion attacks
   - Infinite redirects

5. **Malicious File Types**
   - Executable files disguised as HTML
   - Binary payloads
   - Script files

### Assets Protected

- **Infrastructure**: Backend servers, internal networks, cloud resources
- **Data**: User data, scraped content, system configurations
- **Availability**: System uptime, resource availability
- **Integrity**: Content accuracy, system state

### Security Objectives

1. **Prevent SSRF**: Block access to internal resources and private networks
2. **Prevent XSS**: Sanitize all scraped content before processing or display
3. **Prevent Injection**: Detect and block malicious patterns
4. **Resource Protection**: Limit content size and processing time
5. **Content Validation**: Ensure only safe file types are processed

## Security Components

### 1. URLValidator

**Purpose**: Comprehensive URL validation to prevent SSRF attacks

**Features**:
- Protocol whitelist (HTTP/HTTPS only)
- Private IP range blocking (RFC 1918)
- Localhost blocking
- Link-local address blocking
- Domain whitelist/blacklist
- Suspicious pattern detection
- URL length limits

**Protected IP Ranges**:
```
10.0.0.0/8         # Class A private
172.16.0.0/12      # Class B private
192.168.0.0/16     # Class C private
127.0.0.0/8        # Loopback
169.254.0.0/16     # Link-local (AWS metadata)
::1/128            # IPv6 loopback
fc00::/7           # IPv6 private
fe80::/10          # IPv6 link-local
```

**Blocked Protocols**:
- `javascript:` - XSS vector
- `data:` - Data URI injection
- `file:` - Local file access
- `vbscript:` - Script injection
- `ftp:`, `sftp:`, `ssh:`, `telnet:` - Non-HTTP protocols

**Suspicious Patterns**:
- `@` in URL (credentials)
- `../` (directory traversal)
- `%00` (null byte)
- `%0a`, `%0d` (CRLF injection)
- `<script` (XSS attempt)

### 2. ContentSizeValidator

**Purpose**: Prevent memory exhaustion and DoS attacks

**Features**:
- Maximum content size limits (default: 10MB)
- Warning thresholds (default: 5MB)
- Content size pre-validation
- Actual content validation
- Unicode-aware size calculation

**Limits**:
```python
DEFAULT_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
DEFAULT_WARNING_SIZE = 5 * 1024 * 1024  # 5 MB
```

### 3. FileTypeValidator

**Purpose**: Ensure only safe content types are processed

**Features**:
- MIME type whitelist
- File extension validation
- Magic number detection
- Content-Type header validation

**Allowed MIME Types**:
```
text/html
text/plain
text/xml
application/xhtml+xml
application/xml
```

**Allowed Extensions**:
```
.html, .htm, .xml, .xhtml, .txt
```

**Magic Numbers**:
```python
b'<!DOCTYPE' -> HTML
b'<html'     -> HTML
b'<?xml'     -> XML
```

### 4. ContentSanitizer

**Purpose**: Remove malicious content and prevent XSS

**Features**:
- Strict mode (escape all HTML)
- Selective mode (remove dangerous elements)
- Script/iframe removal
- Event handler removal
- Dangerous protocol removal
- HTML entity encoding

**Dangerous Tags**:
```
script, iframe, embed, object, applet,
frame, frameset, meta, link, style,
base, form, input, button, textarea
```

**Dangerous Attributes**:
```
onclick, onerror, onload, onmouseover,
onfocus, onblur, onchange, onsubmit,
onkeypress, onkeydown, onkeyup, etc.
```

### 5. MaliciousContentDetector

**Purpose**: Detect malicious patterns in content

**Features**:
- SQL injection detection
- XSS pattern detection
- Path traversal detection
- Command injection detection
- Multi-pattern analysis
- Confidence scoring

**Detection Categories**:

**SQL Injection**:
```regex
SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC
UNION\s+SELECT
--|#|\/\*|\*\/
\bOR\b\s+\d+\s*=\s*\d+
```

**XSS Patterns**:
```regex
<script[^>]*>
javascript:
onerror\s*=
onload\s*=
eval\s*\(
alert\s*\(
```

**Path Traversal**:
```regex
\.\./
\.\.\\
%2e%2e%2f
%2e%2e/
..%2f
```

**Command Injection**:
```regex
;\s*(ls|cat|wget|curl|nc|bash|sh|cmd|powershell)
\|\s*(ls|cat|wget|curl|nc|bash|sh|cmd|powershell)
`.*`
\$\(.*\)
```

## Configuration

### Basic Configuration

```python
from backend.src.utils.security import create_secure_validator

# Create validators with default settings
validators = create_secure_validator()

# Custom configuration
validators = create_secure_validator(
    max_size=5 * 1024 * 1024,  # 5 MB limit
    allowed_domains={"example.com", "trusted.org"},  # Domain whitelist
    blocked_domains={"malicious.com"},  # Domain blacklist
    block_private_ips=True,  # Block private IPs
    strict_sanitization=True  # Use strict HTML sanitization
)
```

### Advanced Configuration

```python
from backend.src.utils.security import (
    URLValidator,
    ContentSizeValidator,
    FileTypeValidator,
    ContentSanitizer,
    MaliciousContentDetector
)

# Custom URL validator
url_validator = URLValidator(
    allowed_protocols={'http', 'https'},
    blocked_domains={'spam.com', 'phishing.com'},
    allowed_domains={'example.com', 'safe.org'},  # None = allow all
    block_private_ips=True
)

# Custom size validator
size_validator = ContentSizeValidator(
    max_size=20 * 1024 * 1024,  # 20 MB
    warning_size=10 * 1024 * 1024  # 10 MB
)

# Custom file type validator
file_validator = FileTypeValidator(
    allowed_mime_types={'text/html', 'application/json'},
    allowed_extensions={'.html', '.json'}
)

# Custom sanitizer
sanitizer = ContentSanitizer(
    strict_mode=False  # Allow some HTML
)

# Malicious content detector
detector = MaliciousContentDetector()
```

## Usage Examples

### Example 1: Validate URL Before Scraping

```python
from backend.src.utils.security import URLValidator

validator = URLValidator()

# Validate URL
url = "http://example.com/page.html"
is_valid, error = validator.validate_url(url, raise_exception=False)

if is_valid:
    # Safe to scrape
    print(f"URL is safe: {url}")
else:
    # Block request
    print(f"URL validation failed: {error}")
```

### Example 2: Validate Complete Request

```python
from backend.src.utils.security import validate_request

# Validate URL, size, and content type
is_valid, error = validate_request(
    url="http://example.com/page.html",
    content_length=5000,
    content_type="text/html"
)

if is_valid:
    # Proceed with request
    response = await scraper.fetch(url)
else:
    # Block request
    logger.error(f"Request validation failed: {error}")
```

### Example 3: Sanitize and Validate Content

```python
from backend.src.utils.security import sanitize_and_validate_content

html_content = """
<div>
    <h1>Article Title</h1>
    <p>This is the content.</p>
    <script>alert('xss')</script>
</div>
"""

# Sanitize and check for malicious patterns
sanitized, results = sanitize_and_validate_content(
    html_content,
    check_malicious=True,
    sanitize=True
)

if results['safe']:
    print("Content is safe")
else:
    print(f"Malicious patterns detected: {results['malicious_patterns']}")

# Use sanitized content
print(f"Sanitized content: {sanitized}")
```

### Example 4: Complete Security Pipeline

```python
from backend.src.utils.security import create_secure_validator, validate_request

# Create validators
validators = create_secure_validator(
    max_size=10 * 1024 * 1024,
    block_private_ips=True,
    strict_sanitization=True
)

async def secure_scrape(url: str):
    # Step 1: Validate URL
    is_valid, error = validators['url_validator'].validate_url(
        url, 
        raise_exception=False
    )
    if not is_valid:
        raise ValueError(f"Invalid URL: {error}")
    
    # Step 2: Fetch content
    response = await scraper.fetch(url)
    
    # Step 3: Validate content size
    content_length = len(response.content)
    is_valid, error = validators['size_validator'].validate_size(
        content_length,
        raise_exception=False
    )
    if not is_valid:
        raise ValueError(f"Content too large: {error}")
    
    # Step 4: Validate content type
    is_valid, error = validators['file_validator'].validate_mime_type(
        response.content_type,
        raise_exception=False
    )
    if not is_valid:
        raise ValueError(f"Invalid content type: {error}")
    
    # Step 5: Sanitize and check content
    sanitized, results = sanitize_and_validate_content(
        response.content,
        check_malicious=True,
        sanitize=True,
        validators=validators
    )
    
    if not results['safe']:
        logger.warning(f"Malicious patterns detected: {results['malicious_patterns']}")
    
    return sanitized
```

### Example 5: Domain Whitelist Configuration

```python
from backend.src.utils.security import URLValidator

# Only allow specific domains
validator = URLValidator(
    allowed_domains={
        'example.com',
        'trusted.org',
        'safe.net'
    }
)

# Test URLs
urls = [
    'http://example.com',      # ✅ Allowed
    'http://trusted.org',      # ✅ Allowed
    'http://untrusted.com',    # ❌ Not in whitelist
]

for url in urls:
    is_valid, error = validator.validate_url(url, raise_exception=False)
    print(f"{url}: {'✅ Valid' if is_valid else f'❌ {error}'}")
```

### Example 6: Detect Malicious Patterns

```python
from backend.src.utils.security import MaliciousContentDetector

detector = MaliciousContentDetector()

# Check content for malicious patterns
content = "SELECT * FROM users WHERE id=1 OR 1=1"

# Detect SQL injection
patterns = detector.detect_malicious_patterns(content, check_types=['sql'])
if 'sql' in patterns:
    print(f"SQL injection detected: {patterns['sql']}")

# Check if content is malicious
if detector.is_malicious(content):
    print("Content contains malicious patterns!")
```

## Best Practices

### 1. Defense in Depth

Implement multiple security layers:

```python
# Layer 1: URL validation
validate_url(url)

# Layer 2: Request validation
validate_request(url, content_length, content_type)

# Layer 3: Content size check
validate_size(content_length)

# Layer 4: Content sanitization
sanitized = sanitize_content(content)

# Layer 5: Malicious pattern detection
detect_malicious_patterns(sanitized)
```

### 2. Fail Securely

Always fail closed (deny by default):

```python
is_valid, error = validator.validate_url(url, raise_exception=False)

if not is_valid:
    # Block by default
    logger.error(f"Security validation failed: {error}")
    return None

# Only proceed if explicitly valid
return process_content(url)
```

### 3. Log Security Events

Log all security-related events:

```python
# Validation failures
logger.warning(f"URL validation failed: {error}")

# Malicious patterns
logger.error(f"Malicious content detected: {patterns}")

# Blocked requests
logger.info(f"Request blocked: {url}")
```

### 4. Use Strict Mode in Production

Enable strict sanitization for production:

```python
if settings.ENVIRONMENT == 'production':
    validators = create_secure_validator(strict_sanitization=True)
else:
    validators = create_secure_validator(strict_sanitization=False)
```

### 5. Regularly Update Security Rules

Keep security rules up-to-date:

```python
# Periodically update blocked domains
BLOCKED_DOMAINS = load_blocked_domains_from_threat_intel()

validator = URLValidator(blocked_domains=BLOCKED_DOMAINS)
```

### 6. Rate Limiting

Combine with rate limiting:

```python
from backend.src.utils.rate_limiter import RateLimiter

rate_limiter = RateLimiter(max_requests=100, window_seconds=60)

async def secure_scrape(url: str):
    # Check rate limit
    if not rate_limiter.allow_request(url):
        raise RateLimitError("Too many requests")
    
    # Validate security
    is_valid, error = validate_request(url)
    if not is_valid:
        raise SecurityError(error)
    
    # Proceed
    return await scrape(url)
```

### 7. Content Type Verification

Always verify content matches expected type:

```python
# Validate MIME type
is_valid = file_validator.validate_mime_type(response.content_type)

# Verify with magic numbers
detected_type = file_validator.detect_content_type(response.content[:100])

if detected_type and detected_type != expected_type:
    raise SecurityError("Content type mismatch")
```

### 8. Sanitize User Input

Sanitize all user-provided URLs and parameters:

```python
from backend.src.utils.security import sanitize_url

# User provides URL
user_url = request.query_params.get('url')

# Sanitize before validation
clean_url = sanitize_url(user_url)

if not clean_url:
    raise ValueError("Invalid URL provided")
```

## Testing

### Running Security Tests

```bash
# Run all security tests
pytest backend/tests/test_security.py -v

# Run specific test categories
pytest backend/tests/test_security.py -k "TestURLValidator" -v
pytest backend/tests/test_security.py -k "TestContentSanitizer" -v

# Run with coverage
pytest backend/tests/test_security.py --cov=backend.src.utils.security
```

### Test Categories

The test suite includes:

1. **URL Validation Tests** (25+ tests)
   - Valid/invalid protocols
   - Private IP blocking
   - Localhost blocking
   - Domain whitelist/blacklist
   - Suspicious patterns
   - URL length limits

2. **Content Size Tests** (8+ tests)
   - Size limits
   - Warning thresholds
   - Unicode handling
   - Edge cases

3. **File Type Tests** (12+ tests)
   - MIME type validation
   - Extension validation
   - Magic number detection
   - Custom configurations

4. **XSS Prevention Tests** (10+ tests)
   - Script tag removal
   - Event handler removal
   - Protocol filtering
   - HTML sanitization

5. **Malicious Content Tests** (15+ tests)
   - SQL injection detection
   - XSS pattern detection
   - Path traversal detection
   - Command injection detection

6. **Integration Tests** (6+ tests)
   - Complete request validation
   - Content processing pipeline
   - Whitelist configurations

### Manual Testing

```python
# Test SSRF prevention
test_urls = [
    "http://localhost",           # Should block
    "http://127.0.0.1",          # Should block
    "http://10.0.0.1",           # Should block
    "http://192.168.1.1",        # Should block
    "http://169.254.169.254",    # Should block (AWS metadata)
    "http://example.com",         # Should allow
]

validator = URLValidator()
for url in test_urls:
    is_valid, error = validator.validate_url(url, raise_exception=False)
    print(f"{url}: {'✅ Valid' if is_valid else f'❌ {error}'}")
```

## Incident Response

### Security Incident Handling

1. **Detection**
   - Monitor security logs
   - Alert on validation failures
   - Track malicious patterns

2. **Analysis**
   - Review security logs
   - Identify attack pattern
   - Assess impact

3. **Containment**
   - Block malicious IPs/domains
   - Update security rules
   - Isolate affected systems

4. **Recovery**
   - Restore from backups
   - Verify system integrity
   - Update documentation

5. **Post-Incident**
   - Review security measures
   - Update threat model
   - Improve detection

### Monitoring

```python
# Log security events
logger.warning(f"Security validation failed: {error}")
logger.error(f"Malicious pattern detected: {patterns}")

# Metrics
security_metrics.increment('url_validation_failures')
security_metrics.increment('malicious_content_detected')
security_metrics.increment('requests_blocked')
```

### Alerting

```python
# Alert on suspicious activity
if detector.is_malicious(content):
    send_alert(
        severity='HIGH',
        message=f'Malicious content detected',
        details=patterns
    )

# Alert on SSRF attempts
if 'localhost' in url or is_private_ip(url):
    send_alert(
        severity='CRITICAL',
        message=f'SSRF attempt detected: {url}'
    )
```

## Security Updates

### Updating Security Rules

1. **Add Blocked Domain**:
```python
validator.blocked_domains.add('new-malicious.com')
```

2. **Update Detection Patterns**:
```python
detector.SQL_INJECTION_PATTERNS.append(r'new_pattern')
detector.compiled_patterns = compile_patterns()
```

3. **Adjust Size Limits**:
```python
size_validator.max_size = 20 * 1024 * 1024  # Increase to 20 MB
```

### Threat Intelligence Integration

```python
# Load threat intelligence feeds
def update_blocked_domains():
    """Update blocked domains from threat intel"""
    blocked = load_from_threat_feed('https://threat-intel.example.com/domains')
    validator.blocked_domains.update(blocked)

# Schedule regular updates
scheduler.add_job(update_blocked_domains, 'interval', hours=1)
```

## Performance Considerations

### Optimization Tips

1. **Cache Validation Results**:
```python
from functools import lru_cache

@lru_cache(maxsize=10000)
def is_safe_url_cached(url: str) -> bool:
    return is_safe_url(url)
```

2. **Batch Validation**:
```python
def validate_urls_batch(urls: List[str]) -> Dict[str, bool]:
    """Validate multiple URLs efficiently"""
    results = {}
    validator = URLValidator()
    for url in urls:
        results[url], _ = validator.validate_url(url, raise_exception=False)
    return results
```

3. **Lazy Loading**:
```python
# Only validate when needed
validators = None

def get_validators():
    global validators
    if validators is None:
        validators = create_secure_validator()
    return validators
```

## Compliance

This security implementation helps meet requirements for:

- **OWASP Top 10**
  - A1: Injection (SQL, Command)
  - A3: Sensitive Data Exposure
  - A7: Cross-Site Scripting (XSS)
  - A10: Server-Side Request Forgery (SSRF)

- **CWE (Common Weakness Enumeration)**
  - CWE-79: Cross-site Scripting (XSS)
  - CWE-89: SQL Injection
  - CWE-918: Server-Side Request Forgery (SSRF)
  - CWE-22: Path Traversal
  - CWE-78: OS Command Injection

## Additional Resources

- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [CWE-918: SSRF](https://cwe.mitre.org/data/definitions/918.html)
- [RFC 1918: Address Allocation for Private Internets](https://tools.ietf.org/html/rfc1918)

## License

This security implementation is part of the Web Content Analyzer project.

## Support

For security-related questions or concerns, contact the development team.

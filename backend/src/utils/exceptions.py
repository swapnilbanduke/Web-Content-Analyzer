"""
Custom Exceptions - Application-specific exceptions
"""


class WebContentAnalyzerException(Exception):
    """Base exception for web content analyzer"""
    pass


class ValidationError(WebContentAnalyzerException):
    """Raised when validation fails"""
    pass


class ScrapingError(WebContentAnalyzerException):
    """Raised when web scraping fails"""
    pass


class ProcessingError(WebContentAnalyzerException):
    """Raised when content processing fails"""
    pass


class LLMError(WebContentAnalyzerException):
    """Raised when LLM analysis fails"""
    pass


class ReportGenerationError(WebContentAnalyzerException):
    """Raised when report generation fails"""
    pass

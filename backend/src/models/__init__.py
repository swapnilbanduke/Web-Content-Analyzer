"""
Data Models - Initialization
"""
from .data_models import (
    # Enums
    ContentType,
    AnalysisStatus,
    ErrorSeverity,
    SectionType,
    
    # Request Models
    URLAnalysisRequest,
    BatchAnalysisRequest,
    
    # Content Models
    ScrapedContent,
    ProcessedContent,
    Metadata,
    Image,
    Link,
    Heading,
    Section,
    
    # Analysis Models
    StructureAnalysis,
    TextAnalysis,
    QualityMetrics,
    AnalysisReport,
    
    # Error Models
    AnalysisError,
    ValidationError,
    
    # Response Models
    AnalysisResponse,
    BatchAnalysisResponse,
)

__all__ = [
    # Enums
    "ContentType",
    "AnalysisStatus",
    "ErrorSeverity",
    "SectionType",
    
    # Request Models
    "URLAnalysisRequest",
    "BatchAnalysisRequest",
    
    # Content Models
    "ScrapedContent",
    "ProcessedContent",
    "Metadata",
    "Image",
    "Link",
    "Heading",
    "Section",
    
    # Analysis Models
    "StructureAnalysis",
    "TextAnalysis",
    "QualityMetrics",
    "AnalysisReport",
    
    # Error Models
    "AnalysisError",
    "ValidationError",
    
    # Response Models
    "AnalysisResponse",
    "BatchAnalysisResponse",
]

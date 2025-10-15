"""
API Routes - API endpoints for the web content analyzer
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from ..models.data_models import AnalysisRequest, AnalysisResponse, HealthResponse, BatchRequest
from ..services.analysis_service import AnalysisService
from ..utils.validators import URLValidator
from ..utils.exceptions import ValidationError, ScrapingError, ProcessingError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint
    """
    return HealthResponse(
        status="healthy",
        message="Web Content Analyzer API is running"
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_url(
    request: AnalysisRequest,
    analysis_service: AnalysisService = Depends()
) -> AnalysisResponse:
    """
    Analyze a single URL and generate comprehensive report
    
    Args:
        request: Analysis request containing URL and options
        
    Returns:
        AnalysisResponse with analysis results
        
    Raises:
        HTTPException: If validation or processing fails
    """
    try:
        # Validate URL
        if not URLValidator.is_valid_url(request.url):
            raise ValidationError(f"Invalid URL: {request.url}")
        
        # Perform analysis
        logger.info(f"Starting analysis for URL: {request.url}")
        result = await analysis_service.analyze_url(
            url=request.url,
            include_llm_analysis=request.include_llm_analysis,
            options=request.options
        )
        
        logger.info(f"Analysis completed for URL: {request.url}")
        return result
        
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ScrapingError as e:
        logger.error(f"Scraping error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except ProcessingError as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/batch")
async def batch_analyze(
    request: BatchRequest,
    analysis_service: AnalysisService = Depends()
) -> Dict[str, Any]:
    """
    Analyze multiple URLs in batch
    
    Args:
        request: Batch request containing list of URLs
        
    Returns:
        Dictionary with batch analysis results
    """
    try:
        # Validate all URLs
        invalid_urls = [
            url for url in request.urls 
            if not URLValidator.is_valid_url(url)
        ]
        
        if invalid_urls:
            raise ValidationError(f"Invalid URLs: {', '.join(invalid_urls)}")
        
        # Process batch
        logger.info(f"Starting batch analysis for {len(request.urls)} URLs")
        results = await analysis_service.batch_analyze(
            urls=request.urls,
            options=request.options
        )
        
        return {
            "total": len(request.urls),
            "results": results
        }
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Batch processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

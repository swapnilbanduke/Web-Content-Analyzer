"""
API Client - Backend API communication
"""
import httpx
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class APIClient:
    """
    Client for communicating with backend API
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.api_prefix = "/api/v1"
        self.timeout = 60.0
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check API health
        
        Returns:
            Health status
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}{self.api_prefix}/health")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def analyze_url(
        self,
        url: str,
        include_llm_analysis: bool = True,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a URL
        
        Args:
            url: URL to analyze
            include_llm_analysis: Include LLM analysis
            options: Additional options
            
        Returns:
            Analysis results
            
        Raises:
            Exception: If request fails
        """
        try:
            payload = {
                "url": url,
                "include_llm_analysis": include_llm_analysis,
                "options": options or {}
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}{self.api_prefix}/analyze",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get('detail', str(e))
            except:
                error_detail = str(e)
            
            logger.error(f"Analysis request failed: {error_detail}")
            raise Exception(f"API Error: {error_detail}")
            
        except httpx.TimeoutException:
            logger.error("Analysis request timed out")
            raise Exception("Request timed out. The website may be slow to respond.")
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise Exception(f"Failed to analyze URL: {str(e)}")
    
    async def batch_analyze(
        self,
        urls: list,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze multiple URLs
        
        Args:
            urls: List of URLs
            options: Analysis options
            
        Returns:
            Batch analysis results
        """
        try:
            payload = {
                "urls": urls,
                "options": options or {}
            }
            
            async with httpx.AsyncClient(timeout=self.timeout * 2) as client:
                response = await client.post(
                    f"{self.base_url}{self.api_prefix}/batch",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Batch analysis failed: {str(e)}")
            raise Exception(f"Batch analysis failed: {str(e)}")

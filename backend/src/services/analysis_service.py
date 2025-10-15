"""
Analysis Service - Orchestrates the analysis workflow
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..scrapers.web_scraper import WebScraper
from ..scrapers.content_extractor import ContentExtractor
from ..processors.text_processor import TextProcessor
from ..processors.content_cleaner import ContentCleaner
from ..services.llm_service import LLMService
from ..services.report_service import ReportService
from ..models.data_models import AnalysisResponse, ScrapedContent
from ..utils.exceptions import ScrapingError, ProcessingError

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    Main service for coordinating web content analysis
    """
    
    def __init__(self):
        self.web_scraper = WebScraper()
        self.content_extractor = ContentExtractor()
        self.text_processor = TextProcessor()
        self.content_cleaner = ContentCleaner()
        self.llm_service = LLMService()
        self.report_service = ReportService()
    
    async def analyze_url(
        self,
        url: str,
        include_llm_analysis: bool = True,
        options: Optional[Dict[str, Any]] = None
    ) -> AnalysisResponse:
        """
        Perform comprehensive analysis of a URL
        
        Args:
            url: URL to analyze
            include_llm_analysis: Whether to include LLM-based analysis
            options: Additional analysis options
            
        Returns:
            AnalysisResponse with complete analysis
        """
        try:
            start_time = datetime.now()
            
            # Step 1: Scrape the website
            logger.info(f"Scraping URL: {url}")
            raw_html = await self.web_scraper.scrape(url)
            
            # Step 2: Extract content
            logger.info("Extracting content from HTML")
            scraped_content = self.content_extractor.extract(raw_html, url)
            
            # Step 3: Clean and process text
            logger.info("Processing and cleaning content")
            cleaned_text = self.content_cleaner.clean(scraped_content.main_content)
            processed_data = self.text_processor.process(cleaned_text)
            
            # Step 4: LLM Analysis (if requested)
            llm_analysis = None
            if include_llm_analysis:
                logger.info("Performing LLM analysis")
                llm_analysis = await self.llm_service.analyze(
                    content=cleaned_text,
                    metadata=scraped_content.metadata,
                    options=options
                )
            
            # Step 5: Generate report
            logger.info("Generating comprehensive report")
            report = self.report_service.generate_report(
                url=url,
                scraped_content=scraped_content,
                processed_data=processed_data,
                llm_analysis=llm_analysis
            )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AnalysisResponse(
                url=url,
                status="success",
                timestamp=datetime.now().isoformat(),
                processing_time=processing_time,
                metadata=scraped_content.metadata,
                content_summary={
                    "word_count": processed_data.get("word_count", 0),
                    "sentence_count": processed_data.get("sentence_count", 0),
                    "paragraph_count": processed_data.get("paragraph_count", 0),
                    "reading_time": processed_data.get("reading_time", 0)
                },
                analysis=llm_analysis,
                report=report
            )
            
        except Exception as e:
            logger.error(f"Analysis failed for {url}: {str(e)}")
            raise ProcessingError(f"Failed to analyze URL: {str(e)}")
    
    async def batch_analyze(
        self,
        urls: List[str],
        options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple URLs in batch
        
        Args:
            urls: List of URLs to analyze
            options: Analysis options
            
        Returns:
            List of analysis results
        """
        results = []
        
        for url in urls:
            try:
                result = await self.analyze_url(
                    url=url,
                    include_llm_analysis=options.get("include_llm", True),
                    options=options
                )
                results.append({
                    "url": url,
                    "status": "success",
                    "result": result.dict()
                })
            except Exception as e:
                logger.error(f"Batch analysis failed for {url}: {str(e)}")
                results.append({
                    "url": url,
                    "status": "failed",
                    "error": str(e)
                })
        
        return results

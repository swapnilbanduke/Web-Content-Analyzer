"""
Report Service - Generate comprehensive analysis reports
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ReportService:
    """
    Service for generating analysis reports
    """
    
    def generate_report(
        self,
        url: str,
        scraped_content: Any,
        processed_data: Dict[str, Any],
        llm_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive analysis report
        
        Args:
            url: Analyzed URL
            scraped_content: Scraped content object
            processed_data: Processed text data
            llm_analysis: LLM analysis results
            
        Returns:
            Complete analysis report
        """
        report = {
            "report_id": self._generate_report_id(),
            "generated_at": datetime.now().isoformat(),
            "url": url,
            "metadata": scraped_content.metadata,
            "content_analysis": {
                "word_count": processed_data.get("word_count", 0),
                "sentence_count": processed_data.get("sentence_count", 0),
                "paragraph_count": processed_data.get("paragraph_count", 0),
                "reading_time": processed_data.get("reading_time", 0),
                "readability_score": processed_data.get("readability_score", 0),
                "keywords": processed_data.get("keywords", []),
                "language": processed_data.get("language", "unknown")
            },
            "structure_analysis": {
                "headings": scraped_content.metadata.get("headings", []),
                "links_count": len(scraped_content.links),
                "images_count": len(scraped_content.images),
                "has_forms": scraped_content.metadata.get("has_forms", False)
            }
        }
        
        # Add LLM analysis if available
        if llm_analysis:
            report["ai_analysis"] = {
                "summary": llm_analysis.get("summary", ""),
                "key_points": llm_analysis.get("key_points", []),
                "sentiment": llm_analysis.get("sentiment", "unknown"),
                "topics": llm_analysis.get("topics", []),
                "entities": llm_analysis.get("entities", []),
                "content_type": llm_analysis.get("content_type", "unknown")
            }
        
        # Add recommendations
        report["recommendations"] = self._generate_recommendations(
            processed_data,
            llm_analysis
        )
        
        return report
    
    def _generate_report_id(self) -> str:
        """Generate unique report ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"RPT-{timestamp}"
    
    def _generate_recommendations(
        self,
        processed_data: Dict[str, Any],
        llm_analysis: Optional[Dict[str, Any]]
    ) -> list:
        """
        Generate recommendations based on analysis
        """
        recommendations = []
        
        # Content length recommendations
        word_count = processed_data.get("word_count", 0)
        if word_count < 300:
            recommendations.append({
                "type": "content_length",
                "severity": "warning",
                "message": "Content is quite short. Consider adding more detail."
            })
        
        # Readability recommendations
        readability = processed_data.get("readability_score", 0)
        if readability < 50:
            recommendations.append({
                "type": "readability",
                "severity": "info",
                "message": "Content may be difficult to read. Consider simplifying."
            })
        
        return recommendations

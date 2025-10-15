"""
AI Analysis Service - Main Orchestrator

Unified service that coordinates all AI analyzers:
- Content Summarization
- Sentiment Analysis  
- Topic Extraction
- SEO Analysis
- Readability Scoring
- Competitive Analysis

Provides comprehensive content intelligence in a single call.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import asyncio

from .llm_service import LLMService, create_llm_service
from .content_summarizer import ContentSummarizer, SummarizationResult
from .sentiment_analyzer import SentimentAnalyzer, SentimentAnalysisResult
from .topic_extractor import TopicExtractor, TopicExtractionResult
from .seo_analyzer import SEOAnalyzer, SEOAnalysisResult
from .readability_scorer import ReadabilityScorer, ReadabilityAnalysisResult
from .competitive_analyzer import CompetitiveAnalyzer, CompetitiveAnalysisResult


@dataclass
class AIAnalysisConfig:
    """Configuration for AI analysis"""
    # Which analyzers to run
    summarize: bool = True
    analyze_sentiment: bool = True
    extract_topics: bool = True
    analyze_seo: bool = True
    score_readability: bool = True
    analyze_competitive: bool = False  # Optional, requires competitor data
    
    # LLM settings
    llm_provider: str = "openai"  # or "anthropic"
    llm_model: str = "gpt-4-turbo"
    max_concurrent: int = 3  # Max parallel analyzer calls
    
    # Cost control
    max_cost_usd: float = 1.0  # Max cost per analysis


@dataclass
class ComprehensiveAnalysisResult:
    """Complete AI analysis results from all analyzers"""
    # Individual analyzer results
    summary: Optional[SummarizationResult] = None
    sentiment: Optional[SentimentAnalysisResult] = None
    topics: Optional[TopicExtractionResult] = None
    seo: Optional[SEOAnalysisResult] = None
    readability: Optional[ReadabilityAnalysisResult] = None
    competitive: Optional[CompetitiveAnalysisResult] = None
    
    # Metadata
    total_processing_time_ms: float = 0.0
    total_llm_cost: float = 0.0
    analyzers_run: List[str] = field(default_factory=list)
    errors: Dict[str, str] = field(default_factory=dict)  # analyzer -> error message
    
    # High-level insights (generated from all results)
    executive_summary: str = ""
    key_insights: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    overall_quality_score: float = 0.0  # 0-100


class AIAnalysisService:
    """
    Comprehensive AI-powered content analysis service.
    
    Orchestrates multiple specialized analyzers to provide complete
    content intelligence including summarization, sentiment, topics,
    SEO, readability, and competitive insights.
    
    Features:
    - Parallel analyzer execution for performance
    - Cost tracking and limits
    - Graceful error handling (partial results on failures)
    - Unified comprehensive report
    """
    
    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        config: Optional[AIAnalysisConfig] = None
    ):
        """
        Initialize AI Analysis Service.
        
        Args:
            llm_service: Optional LLM service (will create if not provided)
            config: Analysis configuration
        """
        self.config = config or AIAnalysisConfig()
        self.llm = llm_service or create_llm_service(
            provider=self.config.llm_provider,
            model=self.config.llm_model
        )
        
        # Initialize analyzers
        self.summarizer = ContentSummarizer(self.llm)
        self.sentiment_analyzer = SentimentAnalyzer(self.llm)
        self.topic_extractor = TopicExtractor(self.llm)
        self.seo_analyzer = SEOAnalyzer(self.llm)
        self.readability_scorer = ReadabilityScorer(self.llm)
        self.competitive_analyzer = CompetitiveAnalyzer(self.llm)
    
    async def analyze(
        self,
        content: str,
        title: Optional[str] = None,
        meta_description: Optional[str] = None,
        url: Optional[str] = None,
        headings: Optional[List[str]] = None,
        competitor_context: Optional[str] = None,
        industry: Optional[str] = None,
        target_audience: Optional[str] = None,
        config: Optional[AIAnalysisConfig] = None
    ) -> ComprehensiveAnalysisResult:
        """
        Perform comprehensive AI analysis on content.
        
        Args:
            content: Main content text to analyze
            title: Page/article title
            meta_description: Meta description
            url: Page URL
            headings: List of headings
            competitor_context: Information about competitor content
            industry: Industry/domain
            target_audience: Target audience description
            config: Override default configuration
            
        Returns:
            ComprehensiveAnalysisResult with all analysis results
        """
        start_time = datetime.now()
        config = config or self.config
        
        # Track which analyzers to run
        analyzers_to_run = []
        if config.summarize:
            analyzers_to_run.append('summary')
        if config.analyze_sentiment:
            analyzers_to_run.append('sentiment')
        if config.extract_topics:
            analyzers_to_run.append('topics')
        if config.analyze_seo:
            analyzers_to_run.append('seo')
        if config.score_readability:
            analyzers_to_run.append('readability')
        if config.analyze_competitive and competitor_context:
            analyzers_to_run.append('competitive')
        
        # Run analyzers in parallel (with concurrency limit)
        results = {}
        errors = {}
        
        # Create tasks
        tasks = {}
        if 'summary' in analyzers_to_run:
            tasks['summary'] = self.summarizer.summarize(content, title)
        if 'sentiment' in analyzers_to_run:
            tasks['sentiment'] = self.sentiment_analyzer.analyze(content, title)
        if 'topics' in analyzers_to_run:
            tasks['topics'] = self.topic_extractor.extract(content, title)
        if 'seo' in analyzers_to_run:
            tasks['seo'] = self.seo_analyzer.analyze(
                content, title, meta_description, url, headings
            )
        if 'readability' in analyzers_to_run:
            tasks['readability'] = self.readability_scorer.analyze(content, title)
        if 'competitive' in analyzers_to_run:
            tasks['competitive'] = self.competitive_analyzer.analyze(
                content, title, competitor_context, industry, target_audience
            )
        
        # Execute with concurrency control
        semaphore = asyncio.Semaphore(config.max_concurrent)
        
        async def run_with_semaphore(name: str, task):
            """Run task with semaphore and error handling"""
            async with semaphore:
                try:
                    return name, await task, None
                except Exception as e:
                    return name, None, str(e)
        
        # Run all tasks
        task_results = await asyncio.gather(*[
            run_with_semaphore(name, task)
            for name, task in tasks.items()
        ])
        
        # Collect results
        for name, result, error in task_results:
            if error:
                errors[name] = error
            else:
                results[name] = result
        
        # Check cost limit
        total_cost = self.llm.get_total_cost()
        if total_cost > config.max_cost_usd:
            # Add warning but continue
            errors['cost_warning'] = f"Cost ${total_cost:.4f} exceeded limit ${config.max_cost_usd:.2f}"
        
        # Generate high-level insights
        executive_summary = await self._generate_executive_summary(results)
        key_insights = await self._extract_key_insights(results)
        action_items = await self._generate_action_items(results)
        quality_score = self._calculate_overall_quality(results)
        
        # Calculate total processing time
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        
        return ComprehensiveAnalysisResult(
            summary=results.get('summary'),
            sentiment=results.get('sentiment'),
            topics=results.get('topics'),
            seo=results.get('seo'),
            readability=results.get('readability'),
            competitive=results.get('competitive'),
            total_processing_time_ms=total_time,
            total_llm_cost=total_cost,
            analyzers_run=list(results.keys()),
            errors=errors,
            executive_summary=executive_summary,
            key_insights=key_insights,
            action_items=action_items,
            overall_quality_score=quality_score
        )
    
    async def quick_analysis(
        self,
        content: str,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Quick analysis with just the essentials (fast, low cost).
        
        Returns: Dict with summary, sentiment score, topics, and grade level
        """
        # Run minimal analyzers in parallel
        summary_task = self.summarizer.generate_tldr(content)
        sentiment_task = self.sentiment_analyzer.quick_sentiment_score(content)
        topics_task = self.topic_extractor.extract_quick_keywords(content)
        grade_task = self.readability_scorer.quick_grade_level(content)
        
        summary, sentiment, topics, grade = await asyncio.gather(
            summary_task, sentiment_task, topics_task, grade_task
        )
        
        return {
            'summary': summary,
            'sentiment_score': sentiment,
            'keywords': topics,
            'grade_level': grade,
            'cost': self.llm.get_total_cost()
        }
    
    async def _generate_executive_summary(
        self,
        results: Dict[str, Any]
    ) -> str:
        """Generate executive summary from all results"""
        
        # Build summary from available results
        summary_parts = []
        
        # Content summary
        if 'summary' in results and results['summary'].main_takeaway:
            summary_parts.append(f"Content: {results['summary'].main_takeaway}")
        
        # Sentiment
        if 'sentiment' in results:
            sent = results['sentiment']
            summary_parts.append(
                f"Sentiment: {sent.sentiment.polarity.value} "
                f"(score: {sent.sentiment.score:.2f}), "
                f"tone is {sent.tone.primary_tone.value}"
            )
        
        # Key topics
        if 'topics' in results and results['topics'].main_topics:
            top_topics = [t.name for t in results['topics'].main_topics[:3]]
            summary_parts.append(f"Topics: {', '.join(top_topics)}")
        
        # SEO
        if 'seo' in results:
            seo_score = results['seo'].score.overall_score
            summary_parts.append(f"SEO Score: {seo_score:.0f}/100")
        
        # Readability
        if 'readability' in results:
            read = results['readability']
            summary_parts.append(
                f"Readability: {read.readability_metrics.reading_level.value} "
                f"(grade {read.readability_metrics.average_grade_level:.1f})"
            )
        
        # Competitive
        if 'competitive' in results:
            comp_score = results['competitive'].overall_competitive_score
            summary_parts.append(f"Competitive Position: {comp_score:.0f}/100")
        
        return " | ".join(summary_parts) if summary_parts else "Analysis complete"
    
    async def _extract_key_insights(
        self,
        results: Dict[str, Any]
    ) -> List[str]:
        """Extract key insights from all analyzers"""
        
        insights = []
        
        # Summary insights
        if 'summary' in results and results['summary'].key_points:
            top_point = results['summary'].key_points[0]
            insights.append(f"Key Point: {top_point.point}")
        
        # Sentiment insights
        if 'sentiment' in results:
            sent = results['sentiment']
            if sent.sentiment.score > 0.5:
                insights.append("Content has strong positive sentiment")
            elif sent.sentiment.score < -0.5:
                insights.append("Content has strong negative sentiment")
            
            if sent.emotions:
                dominant = sent.emotions[0]
                insights.append(f"Dominant emotion: {dominant.emotion.value}")
        
        # Topic insights
        if 'topics' in results and results['topics'].main_topics:
            topic_count = len(results['topics'].main_topics)
            insights.append(f"Covers {topic_count} main topics with depth")
        
        # SEO insights
        if 'seo' in results:
            seo = results['seo']
            if seo.score.overall_score < 60:
                insights.append("SEO needs improvement - low overall score")
            if seo.issues:
                critical = [i for i in seo.issues if i.priority.value == 'critical']
                if critical:
                    insights.append(f"{len(critical)} critical SEO issues found")
        
        # Readability insights
        if 'readability' in results:
            read = results['readability']
            if read.readability_metrics.average_grade_level > 12:
                insights.append("Content complexity may limit audience reach")
            if read.accessibility.level.value == 'fail':
                insights.append("Accessibility improvements needed")
        
        # Competitive insights
        if 'competitive' in results:
            comp = results['competitive']
            if comp.content_gaps:
                high_priority = [g for g in comp.content_gaps if g.priority.value == 'high']
                if high_priority:
                    insights.append(f"{len(high_priority)} high-priority content gaps identified")
        
        return insights[:10]
    
    async def _generate_action_items(
        self,
        results: Dict[str, Any]
    ) -> List[str]:
        """Generate prioritized action items"""
        
        actions = []
        
        # SEO actions (high priority)
        if 'seo' in results and results['seo'].recommendations:
            actions.extend(results['seo'].recommendations[:2])
        
        # Readability actions
        if 'readability' in results and results['readability'].improvements:
            top_improvement = results['readability'].improvements[0]
            actions.append(f"Readability: {top_improvement.suggestion}")
        
        # Competitive actions
        if 'competitive' in results and results['competitive'].recommendations:
            actions.extend(results['competitive'].recommendations[:2])
        
        # Sentiment actions
        if 'sentiment' in results and results['sentiment'].recommendations:
            actions.extend(results['sentiment'].recommendations[:1])
        
        return actions[:8]
    
    def _calculate_overall_quality(
        self,
        results: Dict[str, Any]
    ) -> float:
        """Calculate overall content quality score (0-100)"""
        
        scores = []
        weights = []
        
        # SEO score (20% weight)
        if 'seo' in results:
            scores.append(results['seo'].score.overall_score)
            weights.append(0.20)
        
        # Readability score (25% weight)
        if 'readability' in results:
            scores.append(results['readability'].overall_score)
            weights.append(0.25)
        
        # Sentiment balance (15% weight - prefer neutral to slightly positive)
        if 'sentiment' in results:
            sent_score = results['sentiment'].sentiment.score
            # Map -1 to +1 scale to 0-100, with 0.3 being optimal (100)
            if -0.1 <= sent_score <= 0.5:
                sentiment_quality = 100
            else:
                sentiment_quality = max(0, 100 - abs(sent_score - 0.2) * 50)
            scores.append(sentiment_quality)
            weights.append(0.15)
        
        # Topic depth (15% weight)
        if 'topics' in results:
            topic_count = len(results['topics'].main_topics)
            # 5-10 topics is optimal
            if 5 <= topic_count <= 10:
                topic_score = 100
            elif topic_count < 5:
                topic_score = topic_count / 5 * 100
            else:
                topic_score = max(70, 100 - (topic_count - 10) * 5)
            scores.append(topic_score)
            weights.append(0.15)
        
        # Competitive score (25% weight)
        if 'competitive' in results:
            scores.append(results['competitive'].overall_competitive_score)
            weights.append(0.25)
        
        # Calculate weighted average
        if not scores:
            return 0.0
        
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        overall = sum(s * w for s, w in zip(scores, normalized_weights))
        return min(100.0, max(0.0, overall))
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get LLM usage statistics"""
        return {
            'total_requests': self.llm.usage_stats.total_requests,
            'total_tokens': self.llm.usage_stats.total_tokens,
            'total_cost': self.llm.usage_stats.total_cost,
            'total_time_seconds': self.llm.usage_stats.total_time,
            'error_count': self.llm.usage_stats.error_count,
            'average_tokens_per_request': (
                self.llm.usage_stats.total_tokens / self.llm.usage_stats.total_requests
                if self.llm.usage_stats.total_requests > 0 else 0
            )
        }


async def create_ai_analysis_service(
    provider: str = "openai",
    model: str = "gpt-4-turbo",
    api_key: Optional[str] = None
) -> AIAnalysisService:
    """
    Create AI Analysis Service with LLM configuration.
    
    Args:
        provider: LLM provider ('openai' or 'anthropic')
        model: Model name
        api_key: Optional API key (uses env var if not provided)
        
    Returns:
        Configured AIAnalysisService
    """
    llm_service = create_llm_service(provider, model, api_key)
    return AIAnalysisService(llm_service)

"""
AI Analysis Package

Comprehensive AI-powered content analysis services including:
- Content summarization
- Sentiment and emotion analysis
- Topic extraction and NER
- SEO optimization analysis
- Readability and accessibility scoring
- Competitive positioning analysis

All powered by LLM APIs (OpenAI, Anthropic) with cost tracking,
rate limiting, and comprehensive error handling.
"""

from .llm_service import (
    LLMService,
    LLMProvider,
    LLMModel,
    LLMConfig,
    create_llm_service,
)

from .content_summarizer import (
    ContentSummarizer,
    SummaryLength,
    SummarizationResult,
    Summary,
    KeyPoint,
)

from .sentiment_analyzer import (
    SentimentAnalyzer,
    SentimentPolarity,
    ToneType,
    EmotionType,
    SentimentAnalysisResult,
    SentimentScore,
    ToneAnalysis,
    EmotionScore,
)

from .topic_extractor import (
    TopicExtractor,
    EntityType,
    TopicExtractionResult,
    Topic,
    NamedEntity,
    KeyPhrase,
    Theme,
)

from .seo_analyzer import (
    SEOAnalyzer,
    SEOPriority,
    SEOAnalysisResult,
    SEOScore,
    KeywordAnalysis,
    MetaTagsAnalysis,
    ContentStructureScore,
    SEOIssue,
)

from .readability_scorer import (
    ReadabilityScorer,
    ReadingLevel,
    AccessibilityLevel,
    ReadabilityAnalysisResult,
    ReadabilityMetrics,
    TextComplexity,
    VocabularyAnalysis,
    AccessibilityScore,
    ImprovementSuggestion,
)

from .competitive_analyzer import (
    CompetitiveAnalyzer,
    CompetitiveStrength,
    ContentGapPriority,
    CompetitiveAnalysisResult,
    ContentGap,
    UniqueValueProposition,
    CompetitiveAdvantage,
    MarketPosition,
    ContentDepthComparison,
    StyleDifferentiation,
)

from .ai_analysis_service import (
    AIAnalysisService,
    AIAnalysisConfig,
    ComprehensiveAnalysisResult,
    create_ai_analysis_service,
)

# Alias for backward compatibility
AnalysisConfig = AIAnalysisConfig

__all__ = [
    # Main service
    'AIAnalysisService',
    'AIAnalysisConfig',
    'AnalysisConfig',  # Alias
    'ComprehensiveAnalysisResult',
    'create_ai_analysis_service',
    
    # LLM Service
    'LLMService',
    'LLMProvider',
    'LLMModel',
    'LLMConfig',
    'create_llm_service',
    
    # Content Summarizer
    'ContentSummarizer',
    'SummaryLength',
    'SummarizationResult',
    'Summary',
    'KeyPoint',
    
    # Sentiment Analyzer
    'SentimentAnalyzer',
    'SentimentPolarity',
    'ToneType',
    'EmotionType',
    'SentimentAnalysisResult',
    'SentimentScore',
    'ToneAnalysis',
    'EmotionScore',
    
    # Topic Extractor
    'TopicExtractor',
    'EntityType',
    'TopicExtractionResult',
    'Topic',
    'NamedEntity',
    'KeyPhrase',
    'Theme',
    
    # SEO Analyzer
    'SEOAnalyzer',
    'SEOPriority',
    'SEOAnalysisResult',
    'SEOScore',
    'KeywordAnalysis',
    'MetaTagsAnalysis',
    'ContentStructureScore',
    'SEOIssue',
    
    # Readability Scorer
    'ReadabilityScorer',
    'ReadingLevel',
    'AccessibilityLevel',
    'ReadabilityAnalysisResult',
    'ReadabilityMetrics',
    'TextComplexity',
    'VocabularyAnalysis',
    'AccessibilityScore',
    'ImprovementSuggestion',
    
    # Competitive Analyzer
    'CompetitiveAnalyzer',
    'CompetitiveStrength',
    'ContentGapPriority',
    'CompetitiveAnalysisResult',
    'ContentGap',
    'UniqueValueProposition',
    'CompetitiveAdvantage',
    'MarketPosition',
    'ContentDepthComparison',
    'StyleDifferentiation',
]

__version__ = '1.0.0'

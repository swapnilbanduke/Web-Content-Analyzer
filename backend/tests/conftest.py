"""
Pytest configuration and shared fixtures for testing

This module provides:
- Common test fixtures
- Mock data generators
- Test utilities
- Shared setup/teardown logic
"""

import pytest
import asyncio
from typing import Dict, Any
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_html():
    """Sample HTML content for testing"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sample Article About AI</title>
        <meta name="description" content="An informative article about artificial intelligence">
        <meta name="keywords" content="AI, machine learning, technology">
    </head>
    <body>
        <h1>Understanding Artificial Intelligence</h1>
        <p>Artificial intelligence (AI) is revolutionizing how we interact with technology. 
        This comprehensive guide explores the fundamentals of AI and its impact on society.</p>
        
        <h2>What is AI?</h2>
        <p>AI refers to computer systems that can perform tasks typically requiring human intelligence.
        These tasks include visual perception, speech recognition, decision-making, and language translation.</p>
        
        <h2>Applications of AI</h2>
        <p>Modern AI applications span healthcare, finance, transportation, and entertainment.
        Machine learning algorithms power recommendation systems, autonomous vehicles, and medical diagnosis tools.</p>
        
        <h3>Healthcare</h3>
        <p>AI assists doctors in diagnosing diseases, analyzing medical images, and predicting patient outcomes.</p>
        
        <h3>Finance</h3>
        <p>Financial institutions use AI for fraud detection, risk assessment, and algorithmic trading.</p>
        
        <p>The future of AI holds tremendous potential for solving complex global challenges.
        However, it also raises important ethical questions about privacy, bias, and job displacement.</p>
    </body>
    </html>
    """


@pytest.fixture
def sample_text():
    """Sample plain text content"""
    return """
    Understanding Artificial Intelligence
    
    Artificial intelligence (AI) is revolutionizing how we interact with technology. 
    This comprehensive guide explores the fundamentals of AI and its impact on society.
    
    What is AI?
    
    AI refers to computer systems that can perform tasks typically requiring human intelligence.
    These tasks include visual perception, speech recognition, decision-making, and language translation.
    
    Applications of AI
    
    Modern AI applications span healthcare, finance, transportation, and entertainment.
    Machine learning algorithms power recommendation systems, autonomous vehicles, and medical diagnosis tools.
    
    Healthcare
    
    AI assists doctors in diagnosing diseases, analyzing medical images, and predicting patient outcomes.
    
    Finance
    
    Financial institutions use AI for fraud detection, risk assessment, and algorithmic trading.
    
    The future of AI holds tremendous potential for solving complex global challenges.
    However, it also raises important ethical questions about privacy, bias, and job displacement.
    """


@pytest.fixture
def sample_url():
    """Sample URL for testing"""
    return "https://example.com/article/ai-guide"


@pytest.fixture
def mock_scrape_result():
    """Mock scrape result"""
    from src.models.data_models import ScrapeResult
    
    return ScrapeResult(
        url="https://example.com/article",
        title="Sample Article",
        content="This is sample content for testing purposes. " * 50,
        word_count=350,
        success=True,
        metadata={
            'description': 'Sample description',
            'keywords': ['test', 'sample', 'article']
        }
    )


@pytest.fixture
def mock_llm_summary_response():
    """Mock LLM response for summary analysis"""
    return {
        "short_summary": "A brief overview of artificial intelligence and its applications.",
        "medium_summary": "This article explores artificial intelligence, covering its definition, key applications in healthcare and finance, and future implications for society.",
        "long_summary": "This comprehensive guide to artificial intelligence discusses how AI is transforming technology and society. It defines AI as computer systems capable of performing human-like tasks, explores major applications in healthcare and finance sectors, and addresses both the tremendous potential and ethical challenges that AI presents for the future.",
        "main_takeaway": "AI is revolutionizing technology across multiple sectors while raising important ethical considerations.",
        "key_points": [
            {
                "point": "AI enables computers to perform tasks requiring human intelligence",
                "importance": 0.95
            },
            {
                "point": "Major applications include healthcare, finance, transportation, and entertainment",
                "importance": 0.85
            },
            {
                "point": "AI raises ethical questions about privacy, bias, and job displacement",
                "importance": 0.90
            }
        ]
    }


@pytest.fixture
def mock_llm_sentiment_response():
    """Mock LLM response for sentiment analysis"""
    return {
        "sentiment_score": 0.45,
        "confidence": 0.88,
        "tone": ["informative", "professional", "optimistic"],
        "emotions": {
            "optimism": 0.65,
            "concern": 0.35,
            "curiosity": 0.55,
            "neutral": 0.45
        },
        "positive_ratio": 0.60,
        "neutral_ratio": 0.30,
        "negative_ratio": 0.10
    }


@pytest.fixture
def mock_llm_topics_response():
    """Mock LLM response for topics analysis"""
    return {
        "topics": [
            {
                "name": "Artificial Intelligence",
                "relevance": 0.98,
                "subtopics": ["Machine Learning", "Deep Learning"]
            },
            {
                "name": "Healthcare Applications",
                "relevance": 0.75,
                "subtopics": ["Medical Diagnosis", "Patient Care"]
            },
            {
                "name": "Financial Technology",
                "relevance": 0.70,
                "subtopics": ["Fraud Detection", "Risk Assessment"]
            }
        ],
        "themes": [
            {
                "name": "Technological Innovation",
                "description": "Advancement in AI technology and applications"
            },
            {
                "name": "Ethical Considerations",
                "description": "Privacy, bias, and societal impact concerns"
            }
        ],
        "entities": [
            {"text": "AI", "type": "technology", "relevance": 0.95},
            {"text": "machine learning", "type": "technology", "relevance": 0.85},
            {"text": "healthcare", "type": "industry", "relevance": 0.75},
            {"text": "finance", "type": "industry", "relevance": 0.70}
        ],
        "keywords": [
            {"keyword": "artificial intelligence", "frequency": 8, "relevance": 0.98},
            {"keyword": "machine learning", "frequency": 3, "relevance": 0.85},
            {"keyword": "healthcare", "frequency": 4, "relevance": 0.75}
        ]
    }


@pytest.fixture
def mock_llm_seo_response():
    """Mock LLM response for SEO analysis"""
    return {
        "overall_score": 0.78,
        "content_score": 0.82,
        "technical_score": 0.75,
        "keyword_score": 0.80,
        "structure_score": 0.85,
        "links_score": 0.65,
        "meta_tags_score": 0.90,
        "keywords": [
            {
                "keyword": "artificial intelligence",
                "frequency": 8,
                "density": 0.023,
                "relevance": 0.98,
                "placement": ["title", "headings", "body"]
            },
            {
                "keyword": "machine learning",
                "frequency": 3,
                "density": 0.009,
                "relevance": 0.85,
                "placement": ["body"]
            }
        ],
        "issues": [
            {
                "category": "internal_linking",
                "severity": "medium",
                "description": "Limited internal linking structure",
                "recommendation": "Add more internal links to related content"
            }
        ],
        "recommendations": [
            "Increase keyword density for 'AI applications'",
            "Add more internal links to related articles",
            "Optimize image alt tags"
        ]
    }


@pytest.fixture
def mock_llm_readability_response():
    """Mock LLM response for readability analysis"""
    return {
        "overall_score": 0.75,
        "reading_level": "High School",
        "target_audience": "General public with basic technical knowledge",
        "formulas": {
            "flesch_reading_ease": {"score": 65.5, "grade": "Standard"},
            "flesch_kincaid_grade": {"score": 10.2, "grade": "10th grade"},
            "smog_index": {"score": 11.3, "grade": "11th grade"}
        },
        "metrics": {
            "avg_sentence_length": 18.5,
            "avg_word_length": 5.2,
            "complex_words_ratio": 0.15,
            "passive_voice_ratio": 0.08
        },
        "accessibility_score": 0.82,
        "improvement_suggestions": [
            "Reduce average sentence length to improve readability",
            "Simplify complex technical terms where possible",
            "Add more transition words for better flow"
        ]
    }


@pytest.fixture
def mock_analysis_config():
    """Mock analysis configuration"""
    from src.ai import AnalysisConfig
    
    return AnalysisConfig(
        include_summary=True,
        include_sentiment=True,
        include_topics=True,
        include_seo=True,
        include_readability=True,
        include_competitive=False
    )


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary directory for test outputs"""
    output_dir = tmp_path / "test_outputs"
    output_dir.mkdir()
    return output_dir


# Test utilities

def assert_valid_score(score: float, name: str = "score"):
    """Assert that a score is valid (0-1 range)"""
    assert isinstance(score, (int, float)), f"{name} must be numeric"
    assert 0 <= score <= 1, f"{name} must be between 0 and 1, got {score}"


def assert_valid_percentage(value: float, name: str = "percentage"):
    """Assert that a percentage is valid"""
    assert isinstance(value, (int, float)), f"{name} must be numeric"
    assert 0 <= value <= 100, f"{name} must be between 0 and 100, got {value}"


def assert_has_keys(data: Dict[str, Any], required_keys: list, name: str = "data"):
    """Assert that dictionary has all required keys"""
    missing = [key for key in required_keys if key not in data]
    assert not missing, f"{name} missing required keys: {missing}"


def assert_not_empty(value: Any, name: str = "value"):
    """Assert that value is not empty"""
    assert value, f"{name} should not be empty"
    if isinstance(value, (list, dict, str)):
        assert len(value) > 0, f"{name} should not be empty"

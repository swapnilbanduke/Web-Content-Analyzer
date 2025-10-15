"""
Unit tests for AI analysis service
Tests the orchestration of multiple analyzers and result aggregation
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

# Import modules to test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.ai.analysis_service import create_ai_analysis_service, AIAnalysisService
from src.ai.config import AnalysisConfig
from src.ai.models import AnalysisResult


class TestAIServiceCreation:
    """Test AI service initialization and configuration"""
    
    @pytest.mark.asyncio
    async def test_create_openai_service(self):
        """Test creating OpenAI-based service"""
        with patch('src.ai.llm_service.OpenAIService') as mock_openai:
            mock_openai.return_value = AsyncMock()
            
            service = await create_ai_analysis_service(
                provider="openai",
                model="gpt-4",
                api_key="test-key"
            )
            
            assert service is not None
            assert isinstance(service, AIAnalysisService)
    
    @pytest.mark.asyncio
    async def test_create_anthropic_service(self):
        """Test creating Anthropic-based service"""
        with patch('src.ai.llm_service.AnthropicService') as mock_anthropic:
            mock_anthropic.return_value = AsyncMock()
            
            service = await create_ai_analysis_service(
                provider="anthropic",
                model="claude-3-opus-20240229",
                api_key="test-key"
            )
            
            assert service is not None
            assert isinstance(service, AIAnalysisService)
    
    def test_invalid_provider(self):
        """Test error handling for invalid provider"""
        with pytest.raises(ValueError):
            asyncio.run(create_ai_analysis_service(provider="invalid"))


class TestAnalysisService:
    """Test main analysis service functionality"""
    
    @pytest.fixture
    def mock_llm_service(self):
        """Create a mock LLM service"""
        service = AsyncMock()
        service.generate.return_value = {"result": "test"}
        return service
    
    @pytest.fixture
    async def analysis_service(self, mock_llm_service):
        """Create analysis service with mocked LLM"""
        with patch('src.ai.llm_service.create_llm_service', return_value=mock_llm_service):
            service = await create_ai_analysis_service()
            return service
    
    @pytest.mark.asyncio
    async def test_analyze_basic(
        self,
        analysis_service,
        sample_text,
        mock_analysis_config
    ):
        """Test basic analysis"""
        result = await analysis_service.analyze(
            content=sample_text,
            title="Test Article",
            config=mock_analysis_config
        )
        
        assert result is not None
        assert isinstance(result, AnalysisResult)
        assert result.title == "Test Article"
        assert result.word_count > 0
    
    @pytest.mark.asyncio
    async def test_analyze_with_all_dimensions(
        self,
        analysis_service,
        sample_text,
        mock_llm_summary_response,
        mock_llm_sentiment_response,
        mock_llm_topics_response,
        mock_llm_seo_response,
        mock_llm_readability_response
    ):
        """Test analysis with all dimensions enabled"""
        # Mock all analyzer responses
        with patch.multiple(
            'src.ai.analyzers',
            ContentSummarizer=Mock(return_value=AsyncMock(analyze=AsyncMock(return_value=mock_llm_summary_response))),
            SentimentAnalyzer=Mock(return_value=AsyncMock(analyze=AsyncMock(return_value=mock_llm_sentiment_response))),
            TopicsAnalyzer=Mock(return_value=AsyncMock(analyze=AsyncMock(return_value=mock_llm_topics_response))),
            SEOAnalyzer=Mock(return_value=AsyncMock(analyze=AsyncMock(return_value=mock_llm_seo_response))),
            ReadabilityAnalyzer=Mock(return_value=AsyncMock(analyze=AsyncMock(return_value=mock_llm_readability_response)))
        ):
            config = AnalysisConfig(
                include_summary=True,
                include_sentiment=True,
                include_topics=True,
                include_seo=True,
                include_readability=True
            )
            
            result = await analysis_service.analyze(
                content=sample_text,
                title="Complete Test",
                url="https://example.com",
                config=config
            )
            
            # Verify all analyses are present
            assert result.content_summary is not None
            assert result.sentiment_analysis is not None
            assert result.topics_analysis is not None
            assert result.seo_analysis is not None
            assert result.readability_analysis is not None
    
    @pytest.mark.asyncio
    async def test_analyze_selective_dimensions(self, analysis_service, sample_text):
        """Test analysis with only specific dimensions"""
        config = AnalysisConfig(
            include_summary=True,
            include_sentiment=True,
            include_topics=False,
            include_seo=False,
            include_readability=False
        )
        
        result = await analysis_service.analyze(
            content=sample_text,
            title="Selective Test",
            config=config
        )
        
        # Only summary and sentiment should be present
        assert result.content_summary is not None
        assert result.sentiment_analysis is not None
        assert result.topics_analysis is None
        assert result.seo_analysis is None
        assert result.readability_analysis is None
    
    @pytest.mark.asyncio
    async def test_analyze_empty_content(self, analysis_service):
        """Test handling of empty content"""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            await analysis_service.analyze(
                content="",
                title="Empty Test"
            )
    
    @pytest.mark.asyncio
    async def test_analyze_very_short_content(self, analysis_service):
        """Test handling of very short content"""
        result = await analysis_service.analyze(
            content="Short text.",
            title="Short Test"
        )
        
        assert result is not None
        assert result.word_count == 2
    
    @pytest.mark.asyncio
    async def test_analyze_very_long_content(self, analysis_service):
        """Test handling of very long content"""
        # Generate long content (10,000 words)
        long_content = " ".join(["word"] * 10000)
        
        result = await analysis_service.analyze(
            content=long_content,
            title="Long Test"
        )
        
        assert result is not None
        assert result.word_count == 10000
    
    @pytest.mark.asyncio
    async def test_cost_tracking(self, analysis_service, sample_text):
        """Test that analysis tracks costs"""
        result = await analysis_service.analyze(
            content=sample_text,
            title="Cost Test"
        )
        
        assert hasattr(result, 'total_cost')
        assert result.total_cost >= 0
        assert isinstance(result.total_cost, float)
    
    @pytest.mark.asyncio
    async def test_processing_time_tracking(self, analysis_service, sample_text):
        """Test that analysis tracks processing time"""
        result = await analysis_service.analyze(
            content=sample_text,
            title="Time Test"
        )
        
        assert hasattr(result, 'processing_time_ms')
        assert result.processing_time_ms > 0
        assert isinstance(result.processing_time_ms, int)
    
    @pytest.mark.asyncio
    async def test_overall_quality_score(self, analysis_service, sample_text):
        """Test that overall quality score is calculated"""
        result = await analysis_service.analyze(
            content=sample_text,
            title="Quality Test"
        )
        
        assert hasattr(result, 'overall_quality_score')
        assert 0 <= result.overall_quality_score <= 1
    
    @pytest.mark.asyncio
    async def test_metadata_preservation(self, analysis_service, sample_text):
        """Test that metadata is preserved in results"""
        url = "https://example.com/article"
        
        result = await analysis_service.analyze(
            content=sample_text,
            title="Metadata Test",
            url=url
        )
        
        assert result.url == url
        assert result.title == "Metadata Test"
        assert isinstance(result.analyzed_at, datetime)


class TestBatchAnalysis:
    """Test batch analysis functionality"""
    
    @pytest.fixture
    async def analysis_service(self):
        """Create analysis service for batch tests"""
        with patch('src.ai.llm_service.create_llm_service'):
            service = await create_ai_analysis_service()
            return service
    
    @pytest.mark.asyncio
    async def test_analyze_batch(self, analysis_service):
        """Test analyzing multiple items in batch"""
        items = [
            {"content": "Content 1", "title": "Title 1", "url": "https://example.com/1"},
            {"content": "Content 2", "title": "Title 2", "url": "https://example.com/2"},
            {"content": "Content 3", "title": "Title 3", "url": "https://example.com/3"},
        ]
        
        results = await analysis_service.analyze_batch(items, max_concurrent=2)
        
        assert len(results) == 3
        assert all(isinstance(r, AnalysisResult) for r in results)
        assert results[0].title == "Title 1"
        assert results[1].title == "Title 2"
        assert results[2].title == "Title 3"
    
    @pytest.mark.asyncio
    async def test_batch_empty_list(self, analysis_service):
        """Test batch analysis with empty list"""
        results = await analysis_service.analyze_batch([])
        
        assert results == []
    
    @pytest.mark.asyncio
    async def test_batch_concurrent_limit(self, analysis_service, mocker):
        """Test that batch respects concurrent limit"""
        items = [{"content": f"Content {i}", "title": f"Title {i}"} for i in range(10)]
        
        # Mock analyze to track concurrent calls
        concurrent_calls = []
        original_analyze = analysis_service.analyze
        
        async def mock_analyze(*args, **kwargs):
            concurrent_calls.append(len([c for c in concurrent_calls if c]))
            result = await original_analyze(*args, **kwargs)
            concurrent_calls.pop()
            return result
        
        analysis_service.analyze = mock_analyze
        
        await analysis_service.analyze_batch(items, max_concurrent=3)
        
        # Max concurrent should not exceed 3
        assert max(concurrent_calls) <= 3


class TestErrorHandling:
    """Test error handling in AI service"""
    
    @pytest.mark.asyncio
    async def test_llm_api_error(self):
        """Test handling of LLM API errors"""
        with patch('src.ai.llm_service.create_llm_service') as mock_create:
            mock_llm = AsyncMock()
            mock_llm.generate.side_effect = Exception("API Error")
            mock_create.return_value = mock_llm
            
            service = await create_ai_analysis_service()
            
            with pytest.raises(Exception, match="API Error"):
                await service.analyze(content="Test", title="Error Test")
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test handling of timeouts"""
        with patch('src.ai.llm_service.create_llm_service') as mock_create:
            mock_llm = AsyncMock()
            mock_llm.generate.side_effect = asyncio.TimeoutError()
            mock_create.return_value = mock_llm
            
            service = await create_ai_analysis_service()
            
            with pytest.raises(asyncio.TimeoutError):
                await service.analyze(content="Test", title="Timeout Test")
    
    @pytest.mark.asyncio
    async def test_invalid_config(self):
        """Test handling of invalid configuration"""
        service = await create_ai_analysis_service()
        
        # Invalid temperature
        with pytest.raises(ValueError):
            config = AnalysisConfig(temperature=-1)
            await service.analyze(
                content="Test",
                title="Invalid Config",
                config=config
            )


class TestAnalysisConfiguration:
    """Test analysis configuration"""
    
    def test_default_config(self):
        """Test default analysis configuration"""
        config = AnalysisConfig()
        
        assert config.include_summary is True
        assert config.include_sentiment is True
        assert config.include_topics is True
        assert config.include_seo is True
        assert config.include_readability is True
        assert config.include_competitive is False
        assert config.temperature == 0.3
        assert config.max_tokens == 4000
    
    def test_custom_config(self):
        """Test custom analysis configuration"""
        config = AnalysisConfig(
            include_summary=False,
            include_competitive=True,
            temperature=0.7,
            max_tokens=2000,
            num_key_points=10
        )
        
        assert config.include_summary is False
        assert config.include_competitive is True
        assert config.temperature == 0.7
        assert config.max_tokens == 2000
        assert config.num_key_points == 10
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Temperature must be 0-2
        with pytest.raises(ValueError):
            AnalysisConfig(temperature=3.0)
        
        # Max tokens must be positive
        with pytest.raises(ValueError):
            AnalysisConfig(max_tokens=-100)
        
        # Num key points must be positive
        with pytest.raises(ValueError):
            AnalysisConfig(num_key_points=0)


@pytest.mark.integration
class TestIntegrationAIService:
    """Integration tests for AI service (requires real API key)"""
    
    @pytest.mark.skip(reason="Requires API key and costs money")
    @pytest.mark.asyncio
    async def test_real_openai_analysis(self):
        """Test real OpenAI analysis (skipped by default)"""
        import os
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")
        
        service = await create_ai_analysis_service(
            provider="openai",
            model="gpt-3.5-turbo",  # Use cheaper model for testing
            api_key=api_key
        )
        
        result = await service.analyze(
            content="Artificial intelligence is transforming technology.",
            title="AI Impact"
        )
        
        assert result is not None
        assert result.overall_quality_score > 0
        assert result.content_summary is not None
    
    @pytest.mark.skip(reason="Requires API key and costs money")
    @pytest.mark.asyncio
    async def test_real_anthropic_analysis(self):
        """Test real Anthropic analysis (skipped by default)"""
        import os
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not set")
        
        service = await create_ai_analysis_service(
            provider="anthropic",
            model="claude-3-haiku-20240307",  # Use cheaper model
            api_key=api_key
        )
        
        result = await service.analyze(
            content="Machine learning enables computers to learn from data.",
            title="ML Basics"
        )
        
        assert result is not None
        assert result.overall_quality_score > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

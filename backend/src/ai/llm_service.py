"""
LLM Service for AI-Powered Content Analysis

Provides a unified interface for LLM API calls with:
- Support for OpenAI and Anthropic APIs
- Retry logic with exponential backoff
- Rate limiting and token management
- Error handling and fallback mechanisms
- Cost tracking and usage monitoring
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class LLMModel(str, Enum):
    """Supported LLM models"""
    # OpenAI models
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4 = "gpt-4"
    GPT_35_TURBO = "gpt-3.5-turbo"
    
    # Anthropic models
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"


@dataclass
class LLMConfig:
    """LLM service configuration"""
    provider: LLMProvider
    model: LLMModel
    api_key: str
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    # Rate limiting
    max_requests_per_minute: int = 60
    max_tokens_per_minute: int = 90000
    
    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_exponential_base: float = 2.0
    
    # Cost tracking
    track_costs: bool = True
    
    # Timeouts
    request_timeout: int = 60


@dataclass
class LLMResponse:
    """LLM API response wrapper"""
    content: str
    model: str
    provider: LLMProvider
    usage: Dict[str, int]
    finish_reason: str
    response_time_ms: float
    estimated_cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UsageStats:
    """Track LLM usage statistics"""
    total_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    total_time_ms: float = 0.0
    errors: int = 0
    provider_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, requests_per_minute: int, tokens_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.tokens_per_minute = tokens_per_minute
        
        self.request_tokens = requests_per_minute
        self.token_tokens = tokens_per_minute
        
        self.last_request_update = time.time()
        self.last_token_update = time.time()
    
    def _refill_tokens(self):
        """Refill rate limit tokens"""
        now = time.time()
        
        # Refill request tokens
        time_since_request = now - self.last_request_update
        request_refill = (time_since_request / 60.0) * self.requests_per_minute
        self.request_tokens = min(
            self.requests_per_minute,
            self.request_tokens + request_refill
        )
        self.last_request_update = now
        
        # Refill token tokens
        time_since_token = now - self.last_token_update
        token_refill = (time_since_token / 60.0) * self.tokens_per_minute
        self.token_tokens = min(
            self.tokens_per_minute,
            self.token_tokens + token_refill
        )
        self.last_token_update = now
    
    async def acquire(self, estimated_tokens: int = 1000) -> bool:
        """Acquire rate limit tokens"""
        self._refill_tokens()
        
        # Check if we have enough tokens
        if self.request_tokens >= 1 and self.token_tokens >= estimated_tokens:
            self.request_tokens -= 1
            self.token_tokens -= estimated_tokens
            return True
        
        # Calculate wait time
        wait_time = 0.0
        if self.request_tokens < 1:
            wait_time = max(wait_time, (1 - self.request_tokens) / self.requests_per_minute * 60)
        if self.token_tokens < estimated_tokens:
            wait_time = max(wait_time, (estimated_tokens - self.token_tokens) / self.tokens_per_minute * 60)
        
        if wait_time > 0:
            logger.info(f"Rate limit reached, waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
            return await self.acquire(estimated_tokens)
        
        return False


class BaseLLMClient(ABC):
    """Base class for LLM clients"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.usage_stats = UsageStats()
        self.rate_limiter = RateLimiter(
            config.max_requests_per_minute,
            config.max_tokens_per_minute
        )
    
    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion"""
        pass
    
    @abstractmethod
    def estimate_cost(self, usage: Dict[str, int]) -> float:
        """Estimate API cost"""
        pass
    
    async def complete_with_retry(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Complete with retry logic"""
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                # Wait for rate limit
                await self.rate_limiter.acquire(
                    estimated_tokens=len(prompt.split()) * 2
                )
                
                # Make request
                response = await self.complete(prompt, system_prompt, **kwargs)
                
                # Update stats
                self.usage_stats.total_requests += 1
                self.usage_stats.total_tokens += response.usage.get('total_tokens', 0)
                self.usage_stats.total_cost += response.estimated_cost
                self.usage_stats.total_time_ms += response.response_time_ms
                
                return response
                
            except Exception as e:
                last_error = e
                self.usage_stats.errors += 1
                
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (self.config.retry_exponential_base ** attempt)
                    logger.warning(f"Request failed (attempt {attempt + 1}/{self.config.max_retries}): {e}")
                    logger.info(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Request failed after {self.config.max_retries} attempts: {e}")
        
        raise last_error


class OpenAIClient(BaseLLMClient):
    """OpenAI API client"""
    
    def __init__(self, config: LLMConfig):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package not installed. Install with: pip install openai")
        
        super().__init__(config)
        self.client = openai.AsyncOpenAI(api_key=config.api_key)
        
        # Pricing per 1K tokens (as of 2024)
        self.pricing = {
            "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        }
    
    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion using OpenAI API"""
        start_time = time.time()
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Make API call
        response = await self.client.chat.completions.create(
            model=self.config.model.value,
            messages=messages,
            temperature=kwargs.get('temperature', self.config.temperature),
            max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
            top_p=kwargs.get('top_p', self.config.top_p),
            frequency_penalty=kwargs.get('frequency_penalty', self.config.frequency_penalty),
            presence_penalty=kwargs.get('presence_penalty', self.config.presence_penalty),
            timeout=self.config.request_timeout
        )
        
        end_time = time.time()
        
        # Extract response
        content = response.choices[0].message.content
        usage = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens
        }
        
        # Calculate cost
        cost = self.estimate_cost(usage)
        
        return LLMResponse(
            content=content,
            model=response.model,
            provider=LLMProvider.OPENAI,
            usage=usage,
            finish_reason=response.choices[0].finish_reason,
            response_time_ms=(end_time - start_time) * 1000,
            estimated_cost=cost,
            metadata={
                'created': response.created,
                'id': response.id
            }
        )
    
    def estimate_cost(self, usage: Dict[str, int]) -> float:
        """Estimate OpenAI API cost"""
        model_key = self.config.model.value
        if model_key not in self.pricing:
            return 0.0
        
        pricing = self.pricing[model_key]
        input_cost = (usage.get('prompt_tokens', 0) / 1000) * pricing['input']
        output_cost = (usage.get('completion_tokens', 0) / 1000) * pricing['output']
        
        return input_cost + output_cost


class AnthropicClient(BaseLLMClient):
    """Anthropic API client"""
    
    def __init__(self, config: LLMConfig):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")
        
        super().__init__(config)
        self.client = anthropic.AsyncAnthropic(api_key=config.api_key)
        
        # Pricing per 1K tokens (as of 2024)
        self.pricing = {
            "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
            "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
        }
    
    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion using Anthropic API"""
        start_time = time.time()
        
        # Make API call
        response = await self.client.messages.create(
            model=self.config.model.value,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get('temperature', self.config.temperature),
            max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
            top_p=kwargs.get('top_p', self.config.top_p),
            timeout=self.config.request_timeout
        )
        
        end_time = time.time()
        
        # Extract response
        content = response.content[0].text
        usage = {
            'prompt_tokens': response.usage.input_tokens,
            'completion_tokens': response.usage.output_tokens,
            'total_tokens': response.usage.input_tokens + response.usage.output_tokens
        }
        
        # Calculate cost
        cost = self.estimate_cost(usage)
        
        return LLMResponse(
            content=content,
            model=response.model,
            provider=LLMProvider.ANTHROPIC,
            usage=usage,
            finish_reason=response.stop_reason,
            response_time_ms=(end_time - start_time) * 1000,
            estimated_cost=cost,
            metadata={
                'id': response.id,
                'type': response.type
            }
        )
    
    def estimate_cost(self, usage: Dict[str, int]) -> float:
        """Estimate Anthropic API cost"""
        model_key = self.config.model.value
        if model_key not in self.pricing:
            return 0.0
        
        pricing = self.pricing[model_key]
        input_cost = (usage.get('prompt_tokens', 0) / 1000) * pricing['input']
        output_cost = (usage.get('completion_tokens', 0) / 1000) * pricing['output']
        
        return input_cost + output_cost


class LLMService:
    """
    Unified LLM service with multi-provider support.
    
    Features:
    - Automatic provider selection
    - Fallback to alternative providers
    - Cost optimization
    - Usage tracking
    """
    
    def __init__(
        self,
        primary_config: LLMConfig,
        fallback_configs: Optional[List[LLMConfig]] = None
    ):
        self.primary_client = self._create_client(primary_config)
        self.fallback_clients = [
            self._create_client(config) for config in (fallback_configs or [])
        ]
        self.all_clients = [self.primary_client] + self.fallback_clients
    
    def _create_client(self, config: LLMConfig) -> BaseLLMClient:
        """Create LLM client based on provider"""
        if config.provider == LLMProvider.OPENAI:
            return OpenAIClient(config)
        elif config.provider == LLMProvider.ANTHROPIC:
            return AnthropicClient(config)
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")
    
    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        use_fallback: bool = True,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion with automatic fallback.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            use_fallback: Whether to use fallback providers on failure
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse with generated content
        """
        clients_to_try = self.all_clients if use_fallback else [self.primary_client]
        last_error = None
        
        for client in clients_to_try:
            try:
                response = await client.complete_with_retry(prompt, system_prompt, **kwargs)
                return response
            except Exception as e:
                last_error = e
                logger.warning(f"Client {client.config.provider.value} failed: {e}")
                if client != clients_to_try[-1]:
                    logger.info("Trying fallback provider...")
                continue
        
        raise last_error or Exception("All LLM providers failed")
    
    async def complete_batch(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        max_concurrent: int = 5,
        **kwargs
    ) -> List[LLMResponse]:
        """
        Generate completions for multiple prompts concurrently.
        
        Args:
            prompts: List of prompts
            system_prompt: System prompt (optional)
            max_concurrent: Maximum concurrent requests
            **kwargs: Additional parameters
            
        Returns:
            List of LLMResponse objects
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def complete_with_semaphore(prompt: str) -> LLMResponse:
            async with semaphore:
                return await self.complete(prompt, system_prompt, **kwargs)
        
        tasks = [complete_with_semaphore(prompt) for prompt in prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log errors
        responses = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Prompt {i} failed: {result}")
            else:
                responses.append(result)
        
        return responses
    
    def get_usage_stats(self) -> Dict[str, UsageStats]:
        """Get usage statistics for all clients"""
        return {
            f"{client.config.provider.value}_{client.config.model.value}": client.usage_stats
            for client in self.all_clients
        }
    
    def get_total_cost(self) -> float:
        """Get total estimated cost across all clients"""
        return sum(client.usage_stats.total_cost for client in self.all_clients)
    
    def reset_stats(self):
        """Reset usage statistics"""
        for client in self.all_clients:
            client.usage_stats = UsageStats()


# Helper function for easy service creation
def create_llm_service(
    provider: str = "openai",
    model: str = "gpt-3.5-turbo",
    api_key: Optional[str] = None,
    **kwargs
) -> LLMService:
    """
    Create LLM service with simple configuration.
    
    Args:
        provider: Provider name ('openai' or 'anthropic')
        model: Model name
        api_key: API key (uses environment variable if not provided)
        **kwargs: Additional configuration
        
    Returns:
        Configured LLMService
    """
    import os
    
    # Get API key from environment if not provided
    if api_key is None:
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        raise ValueError(f"API key required for {provider}")
    
    # Create configuration
    config = LLMConfig(
        provider=LLMProvider(provider),
        model=LLMModel(model),
        api_key=api_key,
        **kwargs
    )
    
    return LLMService(config)

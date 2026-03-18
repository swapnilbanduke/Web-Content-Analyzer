"""
Configuration Examples for Semantic Search System

This file demonstrates various configuration options for the semantic search system.
"""

from backend.src.knowledge.semantic_search import SemanticSearchService
from backend.src.knowledge.vector_store import VectorStore, EmbeddingProvider
from backend.src.knowledge.query_expansion import QueryExpander


# ============================================================================
# CONFIGURATION 1: Development Setup (Fast, Local, Free)
# ============================================================================
def config_development():
    """
    Best for development and testing.
    - Uses Sentence Transformers (local, no API costs)
    - Smallest fast model
    - All features enabled
    """
    return SemanticSearchService(
        embedding_provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
        model_name="all-MiniLM-L6-v2",  # 384 dimensions, very fast
        storage_path="data/vectors/dev",
        enable_query_expansion=True,
        enable_hybrid_search=True
    )


# ============================================================================
# CONFIGURATION 2: Production Setup (Best Quality)
# ============================================================================
def config_production():
    """
    Best for production with highest quality.
    - Uses OpenAI embeddings (requires API key)
    - High-quality results
    - All optimizations enabled
    """
    import os
    os.environ['OPENAI_API_KEY'] = 'your-api-key-here'
    
    return SemanticSearchService(
        embedding_provider=EmbeddingProvider.OPENAI,
        model_name="text-embedding-3-small",  # 1536 dimensions
        storage_path="data/vectors/prod",
        enable_query_expansion=True,
        enable_hybrid_search=True
    )


# ============================================================================
# CONFIGURATION 3: High Volume Setup (Speed Optimized)
# ============================================================================
def config_high_volume():
    """
    Optimized for high-volume, low-latency searches.
    - Uses smallest Sentence Transformer model
    - Simplified ranking
    - Keyword search for speed
    """
    return SemanticSearchService(
        embedding_provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
        model_name="paraphrase-MiniLM-L3-v2",  # 384 dimensions, fastest
        storage_path="data/vectors/highvol",
        enable_query_expansion=False,  # Disable for speed
        enable_hybrid_search=False  # Use semantic only
    )


# ============================================================================
# CONFIGURATION 4: Multilingual Setup
# ============================================================================
def config_multilingual():
    """
    For multilingual content.
    - Uses multilingual Sentence Transformer
    - Supports 50+ languages
    """
    return SemanticSearchService(
        embedding_provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
        model_name="paraphrase-multilingual-MiniLM-L12-v2",
        storage_path="data/vectors/multilingual",
        enable_query_expansion=True,
        enable_hybrid_search=True
    )


# ============================================================================
# CONFIGURATION 5: Domain-Specific (Technical Content)
# ============================================================================
def config_technical():
    """
    Optimized for technical/scientific content.
    - Uses model trained on scientific papers
    - Better for technical terminology
    """
    return SemanticSearchService(
        embedding_provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
        model_name="allenai-specter",  # Scientific papers
        storage_path="data/vectors/technical",
        enable_query_expansion=True,
        enable_hybrid_search=True
    )


# ============================================================================
# CONFIGURATION 6: Custom Query Expansion
# ============================================================================
def config_custom_expansion():
    """
    With custom query expansion settings.
    """
    service = SemanticSearchService(
        embedding_provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
        enable_query_expansion=False  # We'll add custom expander
    )
    
    # Custom query expander with specific settings
    custom_expander = QueryExpander(
        use_synonyms=True,
        use_concepts=True,
        use_spelling=True,
        max_expansions=15  # More expansions
    )
    
    # Replace default expander
    service.query_expander = custom_expander
    
    return service


# ============================================================================
# CONFIGURATION 7: Memory-Constrained Setup
# ============================================================================
def config_memory_constrained():
    """
    For systems with limited memory.
    - Smallest model
    - Limited cache
    - Frequent saves to disk
    """
    return SemanticSearchService(
        embedding_provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
        model_name="all-MiniLM-L6-v2",
        storage_path="data/vectors/small",
        enable_query_expansion=False,
        enable_hybrid_search=False
    )


# ============================================================================
# CONFIGURATION 8: Custom Vector Store
# ============================================================================
def config_custom_vector_store():
    """
    Using a custom-configured vector store.
    """
    # Create custom vector store
    vector_store = VectorStore(
        provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
        model_name="all-mpnet-base-v2",  # Higher quality, larger
        storage_path="data/vectors/custom",
        dimension=768  # Explicitly set dimension
    )
    
    # Create service with custom store
    service = SemanticSearchService()
    service.vector_store = vector_store
    
    return service


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

async def example_usage():
    """Demonstrate using different configurations"""
    
    # Use development config
    dev_service = config_development()
    
    # Index some content
    await dev_service.index_content(
        content_id=1,
        url="https://example.com",
        title="Test Document",
        content="This is a test document for semantic search."
    )
    
    # Search
    results, metrics = await dev_service.search(
        query="semantic search test",
        top_k=5,
        search_strategy="hybrid"
    )
    
    print(f"Found {len(results)} results in {metrics.search_time_ms:.2f}ms")


# ============================================================================
# ENVIRONMENT-BASED CONFIGURATION
# ============================================================================

def get_service_for_environment(env: str = "development"):
    """
    Get appropriate service based on environment.
    
    Args:
        env: Environment name ('development', 'production', 'testing')
    
    Returns:
        Configured SemanticSearchService
    """
    configs = {
        'development': config_development,
        'production': config_production,
        'testing': config_high_volume,
        'multilingual': config_multilingual,
        'technical': config_technical
    }
    
    config_func = configs.get(env, config_development)
    return config_func()


# ============================================================================
# ADVANCED CONFIGURATION OPTIONS
# ============================================================================

class SearchConfig:
    """Advanced configuration class"""
    
    # Embedding settings
    EMBEDDING_PROVIDER = EmbeddingProvider.SENTENCE_TRANSFORMERS
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION = 384
    
    # Storage settings
    STORAGE_PATH = "data/vectors"
    AUTO_SAVE = True
    SAVE_INTERVAL = 100  # Save after N documents
    
    # Search settings
    ENABLE_QUERY_EXPANSION = True
    ENABLE_HYBRID_SEARCH = True
    DEFAULT_TOP_K = 10
    DEFAULT_MIN_SCORE = 0.3
    DEFAULT_STRATEGY = "hybrid"
    
    # Query expansion settings
    MAX_EXPANSIONS = 10
    USE_SYNONYMS = True
    USE_CONCEPTS = True
    USE_SPELLING = True
    
    # Ranking weights
    SIMILARITY_WEIGHT = 0.4
    RELEVANCE_WEIGHT = 0.3
    KEYWORD_WEIGHT = 0.15
    QUALITY_WEIGHT = 0.1
    FRESHNESS_WEIGHT = 0.05
    
    # Performance settings
    BATCH_SIZE = 100
    MAX_CACHE_SIZE = 10000
    ENABLE_LOGGING = True
    LOG_LEVEL = "INFO"


def create_service_from_config(config: SearchConfig):
    """Create service from configuration class"""
    return SemanticSearchService(
        embedding_provider=config.EMBEDDING_PROVIDER,
        model_name=config.EMBEDDING_MODEL,
        storage_path=config.STORAGE_PATH,
        enable_query_expansion=config.ENABLE_QUERY_EXPANSION,
        enable_hybrid_search=config.ENABLE_HYBRID_SEARCH
    )


# ============================================================================
# EXAMPLE: Loading from Environment Variables
# ============================================================================

def config_from_env():
    """Load configuration from environment variables"""
    import os
    
    provider_map = {
        'openai': EmbeddingProvider.OPENAI,
        'sentence_transformers': EmbeddingProvider.SENTENCE_TRANSFORMERS,
        'huggingface': EmbeddingProvider.HUGGINGFACE
    }
    
    provider_name = os.getenv('EMBEDDING_PROVIDER', 'sentence_transformers')
    provider = provider_map.get(provider_name, EmbeddingProvider.SENTENCE_TRANSFORMERS)
    
    return SemanticSearchService(
        embedding_provider=provider,
        model_name=os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2'),
        storage_path=os.getenv('VECTOR_STORAGE_PATH', 'data/vectors'),
        enable_query_expansion=os.getenv('ENABLE_QUERY_EXPANSION', 'true').lower() == 'true',
        enable_hybrid_search=os.getenv('ENABLE_HYBRID_SEARCH', 'true').lower() == 'true'
    )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    print("Available Configurations:")
    print("1. Development (Fast, Local, Free)")
    print("2. Production (Best Quality)")
    print("3. High Volume (Speed Optimized)")
    print("4. Multilingual (50+ Languages)")
    print("5. Technical (Scientific Content)")
    print("6. Custom Expansion")
    print("7. Memory Constrained")
    print("8. Custom Vector Store")
    
    # Example: Use development config
    print("\nUsing Development Configuration...")
    asyncio.run(example_usage())

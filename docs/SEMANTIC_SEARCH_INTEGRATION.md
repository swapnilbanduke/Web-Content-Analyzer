# Integration Guide - Semantic Search System

## Overview

This guide explains how to integrate the vector embedding and semantic search system into the existing Web Content Analyzer application.

## Prerequisites

1. Install required dependencies:
```bash
pip install sentence-transformers transformers torch numpy scikit-learn
```

2. Verify installation:
```bash
python backend/src/quick_semantic_test.py
```

## Integration Steps

### Step 1: Update Main Application Routes

Update `backend/src/api/routes.py` to include semantic search routes:

```python
from fastapi import FastAPI
from .semantic_routes import router as semantic_router

app = FastAPI()

# Include semantic search routes
app.include_router(semantic_router)

# ... existing routes ...
```

### Step 2: Initialize Service on Startup

Add startup event handler in `backend/main.py`:

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.knowledge.semantic_search import SemanticSearchService
from src.knowledge.vector_store import EmbeddingProvider

# Global service instance
semantic_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global semantic_service
    print("Initializing semantic search service...")
    
    semantic_service = SemanticSearchService(
        embedding_provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
        enable_query_expansion=True,
        enable_hybrid_search=True
    )
    
    yield
    
    # Shutdown
    print("Saving semantic search index...")
    semantic_service.save_index()

app = FastAPI(lifespan=lifespan)
```

### Step 3: Auto-Index Content on Scraping

Update your content scraper to automatically index content:

```python
# In backend/src/scrapers/web_scraper.py or similar

from src.knowledge.semantic_search import SemanticSearchService

class WebScraper:
    def __init__(self, semantic_service: SemanticSearchService = None):
        self.semantic_service = semantic_service
    
    async def scrape_and_analyze(self, url: str):
        # ... existing scraping logic ...
        
        # After successful scraping, index for semantic search
        if self.semantic_service and content:
            try:
                await self.semantic_service.index_content(
                    content_id=content.id,
                    url=content.url,
                    title=content.title,
                    content=content.main_content,
                    metadata={
                        'category': content.category,
                        'tags': content.tags,
                        'created_at': content.created_at.isoformat(),
                        'domain': content.domain,
                        'has_images': len(content.images) > 0,
                        'content_length': len(content.main_content)
                    }
                )
                logger.info(f"Indexed content {content.id} for semantic search")
            except Exception as e:
                logger.error(f"Failed to index content {content.id}: {e}")
        
        return content
```

### Step 4: Add Search to Knowledge Base

Update `backend/src/knowledge/knowledge_base.py`:

```python
from .semantic_search import SemanticSearchService

class KnowledgeBase:
    def __init__(self):
        self.store = ContentStore()
        self.db = get_db()
        
        # Initialize semantic search
        self.semantic_search = SemanticSearchService()
    
    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        use_semantic: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Enhanced search with semantic capabilities.
        """
        if use_semantic:
            # Use semantic search
            results, metrics = await self.semantic_search.search(
                query=query,
                top_k=limit,
                filters=filters,
                search_strategy="hybrid"
            )
            
            # Convert to knowledge base format
            return [
                {
                    'id': r.content_id,
                    'url': r.url,
                    'title': r.title,
                    'preview': r.content_preview,
                    'score': r.final_score,
                    'metadata': r.metadata
                }
                for r in results
            ]
        else:
            # Fall back to keyword search
            return self.store.search_content(query, limit)
```

### Step 5: Update Q&A System

Enhance `backend/src/knowledge/qa_system.py` with semantic retrieval:

```python
from .semantic_search import SemanticSearchService

class QASystem:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        self.kb = KnowledgeBase()
        self.semantic_search = SemanticSearchService()
    
    async def _retrieve_context(
        self,
        question: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context using semantic search.
        """
        # Use semantic search for better retrieval
        results, metrics = await self.semantic_search.search(
            query=question,
            top_k=top_k,
            search_strategy="hybrid",
            min_score=0.3
        )
        
        # Convert to context format
        context = []
        for result in results:
            context.append({
                'content_id': result.content_id,
                'url': result.url,
                'title': result.title,
                'content': result.content_preview,
                'relevance_score': result.final_score
            })
        
        return context
```

### Step 6: Add Search Endpoint to UI

Create a search interface in the frontend or Streamlit UI:

```python
# In backend/launch_ui.py or frontend

import streamlit as st
from src.knowledge.semantic_search import SemanticSearchService

# Initialize service
@st.cache_resource
def get_search_service():
    return SemanticSearchService()

def search_page():
    st.title("Semantic Search")
    
    # Search input
    query = st.text_input("Search query:")
    
    # Search strategy
    strategy = st.selectbox(
        "Search strategy:",
        ["hybrid", "semantic", "keyword"]
    )
    
    # Number of results
    top_k = st.slider("Number of results:", 1, 50, 10)
    
    if st.button("Search"):
        service = get_search_service()
        
        with st.spinner("Searching..."):
            results, metrics = await service.search(
                query=query,
                top_k=top_k,
                search_strategy=strategy
            )
        
        # Display metrics
        st.info(f"Found {len(results)} results in {metrics.search_time_ms:.2f}ms")
        
        # Display results
        for result in results:
            with st.expander(f"{result.rank}. {result.title}"):
                st.write(f"**URL:** {result.url}")
                st.write(f"**Score:** {result.final_score:.3f}")
                st.write(f"**Preview:** {result.content_preview}")
                st.write(f"**Matched terms:** {', '.join(result.matched_terms)}")
```

### Step 7: Background Indexing Task

Set up background indexing for existing content:

```python
# Create a script: backend/scripts/index_existing_content.py

import asyncio
from src.storage.content_store import ContentStore
from src.knowledge.semantic_search import SemanticSearchService

async def index_all_content():
    """Index all existing content for semantic search"""
    
    store = ContentStore()
    service = SemanticSearchService()
    
    # Get all content
    all_content = store.get_all_content()
    
    print(f"Found {len(all_content)} documents to index")
    
    # Prepare for batch indexing
    batch_size = 100
    for i in range(0, len(all_content), batch_size):
        batch = all_content[i:i+batch_size]
        
        documents = [
            {
                'id': content['id'],
                'url': content['url'],
                'title': content.get('title', ''),
                'content': content.get('content', ''),
                'metadata': content.get('metadata', {})
            }
            for content in batch
        ]
        
        success, failed = await service.index_contents_batch(documents)
        print(f"Indexed batch {i//batch_size + 1}: {success} success, {failed} failed")
    
    # Save index
    service.save_index()
    print("Indexing complete and saved!")

if __name__ == "__main__":
    asyncio.run(index_all_content())
```

Run it:
```bash
python backend/scripts/index_existing_content.py
```

### Step 8: Add Periodic Re-indexing

Set up scheduled task for re-indexing:

```python
# In backend/main.py or separate scheduler

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.knowledge.semantic_search import SemanticSearchService

scheduler = AsyncIOScheduler()

async def reindex_recent_content():
    """Re-index recently updated content"""
    service = SemanticSearchService()
    store = ContentStore()
    
    # Get content updated in last 24 hours
    recent = store.get_recent_content(hours=24)
    
    # Re-index
    for content in recent:
        await service.index_content(
            content_id=content['id'],
            url=content['url'],
            title=content['title'],
            content=content['content'],
            metadata=content.get('metadata', {})
        )
    
    service.save_index()

# Schedule to run daily at 2 AM
scheduler.add_job(reindex_recent_content, 'cron', hour=2)
scheduler.start()
```

## Configuration

### Environment Variables

Add to `.env` file:

```bash
# Semantic Search Configuration
EMBEDDING_PROVIDER=sentence_transformers
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_STORAGE_PATH=data/vectors
ENABLE_QUERY_EXPANSION=true
ENABLE_HYBRID_SEARCH=true

# Optional: OpenAI (for better quality)
# EMBEDDING_PROVIDER=openai
# OPENAI_API_KEY=your-key-here
# EMBEDDING_MODEL=text-embedding-3-small
```

### Settings Integration

Update `backend/src/config/settings.py`:

```python
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Semantic Search
    EMBEDDING_PROVIDER: str = "sentence_transformers"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    VECTOR_STORAGE_PATH: str = "data/vectors"
    ENABLE_QUERY_EXPANSION: bool = True
    ENABLE_HYBRID_SEARCH: bool = True
    SEMANTIC_SEARCH_TOP_K: int = 10
    SEMANTIC_MIN_SCORE: float = 0.3
```

## Testing the Integration

### 1. Test API Endpoints

```bash
# Start server
python -m uvicorn backend.main:app --reload

# Test indexing
curl -X POST http://localhost:8000/api/v1/semantic/index \
  -H "Content-Type: application/json" \
  -d '{"content_id": 1, "url": "https://test.com", "title": "Test", "content": "Test content"}'

# Test search
curl -X POST http://localhost:8000/api/v1/semantic/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 5}'
```

### 2. Test Integration

```python
# Create test script: backend/tests/test_integration.py

import pytest
from src.knowledge.semantic_search import SemanticSearchService
from src.scrapers.web_scraper import WebScraper

@pytest.mark.asyncio
async def test_scrape_and_index():
    """Test that scraping automatically indexes content"""
    service = SemanticSearchService()
    scraper = WebScraper(semantic_service=service)
    
    # Scrape content
    content = await scraper.scrape_and_analyze("https://example.com")
    
    # Verify it's indexed
    results, _ = await service.search(content.title, top_k=1)
    assert len(results) > 0
    assert results[0].content_id == content.id
```

## Monitoring and Maintenance

### 1. Add Logging

```python
import logging

logger = logging.getLogger(__name__)

# Log search queries
logger.info(f"Semantic search: query='{query}', results={len(results)}, time={metrics.search_time_ms}ms")

# Log indexing
logger.info(f"Indexed content {content_id} for semantic search")
```

### 2. Add Metrics

```python
from prometheus_client import Counter, Histogram

# Metrics
search_queries = Counter('semantic_search_queries_total', 'Total search queries')
search_duration = Histogram('semantic_search_duration_seconds', 'Search duration')
index_operations = Counter('semantic_index_operations_total', 'Total index operations')

# Use in code
search_queries.inc()
with search_duration.time():
    results, metrics = await service.search(query)
```

### 3. Health Check

```python
@app.get("/health/semantic-search")
async def semantic_search_health():
    """Health check for semantic search system"""
    try:
        stats = semantic_service.get_search_stats()
        return {
            "status": "healthy",
            "indexed_documents": stats['total_indexed_documents'],
            "provider": stats['vector_store']['provider']
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## Troubleshooting

### Issue: Search returns no results
**Solution**: Check if content is indexed. Run: `GET /api/v1/semantic/stats`

### Issue: Slow search performance
**Solution**: 
- Reduce `top_k` value
- Disable query expansion for speed
- Use smaller embedding model

### Issue: High memory usage
**Solution**:
- Save index periodically: `service.save_index()`
- Use smaller embedding model
- Clear old documents from index

## Best Practices

1. **Index on creation**: Auto-index when content is scraped/created
2. **Batch operations**: Use `index_contents_batch()` for multiple documents
3. **Hybrid search**: Use hybrid strategy for best results
4. **Save regularly**: Save index after batch operations
5. **Monitor performance**: Track search times and result quality
6. **Clean old data**: Remove outdated documents from index

## Next Steps

1. ✅ Complete integration steps above
2. ✅ Test with sample content
3. ✅ Index existing content
4. ✅ Add to UI/frontend
5. ✅ Monitor and optimize
6. ✅ Consider FAISS for scale (if >100k documents)

## Support

For issues or questions:
- Check [SEMANTIC_SEARCH_GUIDE.md](../docs/SEMANTIC_SEARCH_GUIDE.md)
- Review examples in `backend/examples/semantic_search_examples.py`
- Run tests: `pytest backend/tests/test_semantic_search.py -v`

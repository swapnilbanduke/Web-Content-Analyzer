# Vector Embedding & Semantic Search System

## Overview

This document describes the comprehensive vector embedding and semantic search system built for the Web Content Analyzer. The system provides advanced semantic search capabilities using state-of-the-art embedding models and sophisticated ranking algorithms.

## Architecture

### Components

1. **Vector Store** (`vector_store.py`)
   - Manages vector embeddings and similarity computations
   - Supports multiple embedding providers (OpenAI, Sentence Transformers, HuggingFace)
   - Efficient in-memory vector index with persistence
   - Multiple similarity metrics (cosine, dot product, Euclidean)

2. **Query Expansion** (`query_expansion.py`)
   - Expands queries with synonyms and related concepts
   - N-gram generation for better matching
   - Spelling correction
   - LLM-powered semantic expansion
   - Query rewriting and intent detection

3. **Semantic Search Service** (`semantic_search.py`)
   - High-level search API integrating all components
   - Hybrid search (semantic + keyword)
   - Multi-factor relevance ranking
   - Batch indexing capabilities
   - Similar document discovery

## Features

### 1. Content Vectorization Pipeline

The system converts text content into high-dimensional vector embeddings:

```python
from backend.src.knowledge.semantic_search import SemanticSearchService

# Initialize service
search_service = SemanticSearchService(
    embedding_provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
    model_name="all-MiniLM-L6-v2"
)

# Index content
await search_service.index_content(
    content_id=1,
    url="https://example.com/article",
    title="Machine Learning Basics",
    content="Full article text here...",
    metadata={'category': 'AI', 'tags': ['ml', 'tutorial']}
)
```

**Supported Embedding Providers:**
- **Sentence Transformers**: Fast, open-source, runs locally
- **OpenAI**: High-quality embeddings via API
- **HuggingFace**: Flexible transformer models

### 2. Similarity Computation Algorithms

Three similarity metrics are supported:

#### Cosine Similarity
Best for most use cases. Measures angle between vectors.

```python
similarities = vector_store.compute_similarity(
    query_embedding,
    method="cosine"
)
```

#### Dot Product
Faster but considers magnitude. Good for normalized vectors.

```python
similarities = vector_store.compute_similarity(
    query_embedding,
    method="dot_product"
)
```

#### Euclidean Distance
Measures absolute distance. Converted to similarity score.

```python
similarities = vector_store.compute_similarity(
    query_embedding,
    method="euclidean"
)
```

### 3. Relevance Scoring Mechanisms

Multi-factor scoring combines several signals:

**Scoring Formula:**
```
final_score = 0.4 × similarity_score +
              0.3 × relevance_score +
              0.15 × keyword_score +
              0.1 × quality_score +
              0.05 × freshness_score
```

**Components:**
- **Similarity Score**: Vector similarity from embeddings
- **Relevance Score**: Context-aware relevance from hybrid search
- **Keyword Score**: Direct keyword matching
- **Quality Score**: Content quality signals (length, structure, images)
- **Freshness Score**: Time-based decay for recency

### 4. Query Expansion Techniques

The system automatically expands queries to improve recall:

```python
from backend.src.knowledge.query_expansion import QueryExpander

expander = QueryExpander(
    use_synonyms=True,
    use_concepts=True,
    max_expansions=10
)

expanded = await expander.expand("machine learning")
# Returns: ExpandedQuery with:
# - expanded_terms: ['machine learning']
# - synonyms: ['ai', 'artificial intelligence', 'ml']
# - related_concepts: ['neural networks', 'deep learning', 'algorithms']
# - weights: {'ai': 0.7, 'neural networks': 0.6, ...}
```

**Expansion Strategies:**
1. **Synonym Expansion**: Built-in dictionary of technical and business terms
2. **Domain Concepts**: Industry-specific term relationships
3. **N-grams**: Bi-grams and tri-grams for phrase matching
4. **Spelling Correction**: Fix common typos
5. **Word Variations**: Plurals, verb forms
6. **LLM Expansion**: Semantic expansion using language models

### 5. Result Ranking Optimization

#### Reciprocal Rank Fusion (RRF)

Merges results from multiple search strategies:

```python
RRF_score = Σ(1 / (k + rank))
```

where k=60 (standard constant)

#### Advanced Re-ranking

After initial retrieval, results are re-ranked considering:
- Matched keywords in content
- Document quality metrics
- Content freshness (exponential decay)
- Metadata relevance (title, tags, category)

```python
results, metrics = await search_service.search(
    query="machine learning tutorial",
    top_k=10,
    search_strategy="hybrid",  # Best for most cases
    min_score=0.3
)
```

## Usage Examples

### Basic Search

```python
# Semantic search (vector similarity only)
results, metrics = await search_service.search(
    query="artificial intelligence",
    top_k=5,
    search_strategy="semantic"
)

for result in results:
    print(f"{result.rank}. {result.title}")
    print(f"   Similarity: {result.similarity_score:.3f}")
    print(f"   Relevance: {result.final_score:.3f}")
```

### Hybrid Search (Recommended)

```python
# Combines semantic + keyword for best results
results, metrics = await search_service.search(
    query="deep learning neural networks",
    top_k=10,
    search_strategy="hybrid"
)

print(f"Search completed in {metrics.search_time_ms:.2f}ms")
print(f"Expanded query: {metrics.expansion_terms}")
```

### Filtered Search

```python
# Search within specific categories
results, metrics = await search_service.search(
    query="optimization",
    top_k=10,
    filters={'category': 'AI/ML'},
    search_strategy="hybrid"
)
```

### Similar Document Discovery

```python
# Find documents similar to a specific one
similar = await search_service.get_similar_documents(
    content_id=123,
    top_k=5
)

for doc in similar:
    print(f"{doc.title} - Similarity: {doc.similarity_score:.3f}")
```

### Batch Indexing

```python
# Efficiently index multiple documents
contents = [
    {
        'id': 1,
        'url': 'https://example.com/1',
        'title': 'Document 1',
        'content': 'Content 1...',
        'metadata': {'category': 'Tech'}
    },
    # ... more documents
]

success, failed = await search_service.index_contents_batch(contents)
print(f"Indexed {success} documents")
```

## API Endpoints

### POST /api/v1/semantic/index
Index a single content for semantic search.

**Request:**
```json
{
  "content_id": 1,
  "url": "https://example.com/article",
  "title": "Article Title",
  "content": "Full article content...",
  "metadata": {
    "category": "Technology",
    "tags": ["ai", "ml"]
  }
}
```

### POST /api/v1/semantic/index/batch
Batch index multiple contents.

**Request:**
```json
{
  "contents": [
    {
      "content_id": 1,
      "url": "...",
      "title": "...",
      "content": "...",
      "metadata": {}
    }
  ]
}
```

### POST /api/v1/semantic/search
Perform semantic search.

**Request:**
```json
{
  "query": "machine learning tutorial",
  "top_k": 10,
  "filters": {"category": "AI"},
  "min_score": 0.3,
  "search_strategy": "hybrid"
}
```

**Response:**
```json
{
  "results": [
    {
      "content_id": 1,
      "url": "...",
      "title": "...",
      "content_preview": "...",
      "similarity_score": 0.85,
      "relevance_score": 0.82,
      "keyword_score": 0.75,
      "final_score": 0.81,
      "rank": 1,
      "matched_terms": ["machine", "learning"],
      "metadata": {},
      "explanation": "..."
    }
  ],
  "metrics": {
    "search_time_ms": 45.2,
    "vectorization_time_ms": 12.3,
    "ranking_time_ms": 8.5
  },
  "query": "machine learning tutorial",
  "total_results": 10,
  "search_time_ms": 45.2
}
```

### GET /api/v1/semantic/expand
Expand a query to see how it will be enhanced.

**Query Params:**
- `query`: Query string to expand

**Response:**
```json
{
  "original": "ai tutorial",
  "expanded_terms": ["ai tutorial"],
  "synonyms": ["artificial intelligence", "machine learning"],
  "related_concepts": ["neural networks", "deep learning"],
  "weighted_terms": {
    "ai": 1.0,
    "tutorial": 1.0,
    "artificial intelligence": 0.7
  }
}
```

### POST /api/v1/semantic/similar
Find similar documents.

**Request:**
```json
{
  "content_id": 123,
  "top_k": 5
}
```

### GET /api/v1/semantic/stats
Get system statistics.

**Response:**
```json
{
  "total_indexed_documents": 1500,
  "vector_store_provider": "sentence_transformers",
  "embedding_model": "all-MiniLM-L6-v2",
  "embedding_dimension": 384,
  "query_expansion_enabled": true,
  "hybrid_search_enabled": true
}
```

## Performance Optimization

### Batch Processing
Always use batch operations when indexing multiple documents:
```python
# Good - Batch indexing
await search_service.index_contents_batch(contents)

# Bad - Individual indexing in loop
for content in contents:
    await search_service.index_content(**content)
```

### Caching
Vector embeddings are cached in memory for fast retrieval.

### Persistence
Save the index to disk to avoid re-indexing:
```python
search_service.save_index()  # Save to disk
```

On restart, the index is automatically loaded.

## Configuration

### Choosing an Embedding Provider

**Sentence Transformers (Recommended for most cases)**
- ✅ Fast, runs locally
- ✅ No API costs
- ✅ Good quality
- ❌ Lower quality than OpenAI

```python
service = SemanticSearchService(
    embedding_provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
    model_name="all-MiniLM-L6-v2"  # Fast, 384 dimensions
)
```

**OpenAI (Best quality)**
- ✅ Highest quality embeddings
- ✅ Large context window
- ❌ API costs
- ❌ Network latency

```python
service = SemanticSearchService(
    embedding_provider=EmbeddingProvider.OPENAI,
    model_name="text-embedding-3-small"  # 1536 dimensions
)
```

### Search Strategy Selection

- **semantic**: Pure vector search, best for conceptual similarity
- **keyword**: Traditional search with expansion, best for exact matches
- **hybrid**: Combines both (recommended for most use cases)

## Testing

Run comprehensive tests:
```bash
pytest backend/tests/test_semantic_search.py -v
```

Run examples:
```bash
python backend/examples/semantic_search_examples.py
```

## Dependencies

Required packages (in requirements.txt):
```
sentence-transformers==2.2.2
transformers==4.35.0
torch==2.1.0
numpy==1.24.3
scikit-learn==1.3.2
openai==1.3.5  # Optional, for OpenAI embeddings
```

## Troubleshooting

### Issue: Slow indexing
**Solution**: Use batch indexing and consider using a smaller embedding model.

### Issue: Poor search results
**Solution**: 
1. Enable hybrid search
2. Ensure enough content is indexed (>50 documents)
3. Try different embedding models
4. Adjust min_score threshold

### Issue: Out of memory
**Solution**: 
1. Use a smaller embedding model
2. Index in smaller batches
3. Save index to disk and clear memory periodically

## Future Enhancements

1. **FAISS Integration**: For very large-scale vector search
2. **Multi-language Support**: Cross-lingual embeddings
3. **Contextual Reranking**: Use LLM to rerank top results
4. **Approximate Nearest Neighbor**: For faster similarity search
5. **Incremental Updates**: Update embeddings without full rebuild

## References

- [Sentence Transformers Documentation](https://www.sbert.net/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Vector Search Best Practices](https://www.pinecone.io/learn/vector-search/)

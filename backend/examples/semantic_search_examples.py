"""
Semantic Search Examples

Demonstrates how to use the vector embedding and semantic search system.
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.knowledge.semantic_search import SemanticSearchService, SemanticSearchResult
from src.knowledge.vector_store import EmbeddingProvider
from src.knowledge.query_expansion import QueryExpander


async def example_1_basic_indexing():
    """Example 1: Basic content indexing"""
    print("\n=== Example 1: Basic Content Indexing ===\n")
    
    # Initialize semantic search service
    search_service = SemanticSearchService(
        embedding_provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
        enable_query_expansion=True,
        enable_hybrid_search=True
    )
    
    # Sample content to index
    contents = [
        {
            'id': 1,
            'url': 'https://example.com/ml-basics',
            'title': 'Introduction to Machine Learning',
            'content': '''Machine learning is a subset of artificial intelligence that 
            enables systems to learn and improve from experience without being explicitly 
            programmed. It focuses on developing computer programs that can access data 
            and use it to learn for themselves.''',
            'metadata': {
                'category': 'AI/ML',
                'tags': ['machine learning', 'AI', 'tutorial'],
                'created_at': '2024-01-15T10:00:00'
            }
        },
        {
            'id': 2,
            'url': 'https://example.com/deep-learning',
            'title': 'Deep Learning Fundamentals',
            'content': '''Deep learning is a subset of machine learning that uses neural 
            networks with multiple layers. These neural networks attempt to simulate the 
            behavior of the human brain to learn from large amounts of data.''',
            'metadata': {
                'category': 'AI/ML',
                'tags': ['deep learning', 'neural networks', 'AI'],
                'created_at': '2024-01-20T14:30:00'
            }
        },
        {
            'id': 3,
            'url': 'https://example.com/seo-guide',
            'title': 'SEO Best Practices',
            'content': '''Search Engine Optimization (SEO) is the practice of increasing 
            the quantity and quality of traffic to your website through organic search 
            engine results. Key factors include keywords, content quality, and backlinks.''',
            'metadata': {
                'category': 'Marketing',
                'tags': ['SEO', 'marketing', 'web'],
                'created_at': '2024-02-01T09:00:00'
            }
        }
    ]
    
    # Index content in batch
    success, failed = await search_service.index_contents_batch(contents)
    print(f"✓ Indexed {success} documents successfully ({failed} failed)")
    
    # Get stats
    stats = search_service.get_search_stats()
    print(f"✓ Total documents in index: {stats['total_indexed_documents']}")
    print(f"✓ Vector store provider: {stats['vector_store']['provider']}")
    print(f"✓ Embedding dimension: {stats['vector_store']['dimension']}")
    
    return search_service


async def example_2_semantic_search(search_service: SemanticSearchService):
    """Example 2: Semantic search with different queries"""
    print("\n=== Example 2: Semantic Search ===\n")
    
    queries = [
        "What is artificial intelligence?",
        "Neural network tutorial",
        "Website optimization techniques"
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        print("-" * 60)
        
        # Perform search
        results, metrics = await search_service.search(
            query=query,
            top_k=3,
            search_strategy="semantic"
        )
        
        # Display results
        print(f"Found {metrics.total_results} results in {metrics.search_time_ms:.2f}ms")
        
        for result in results:
            print(f"\n  Rank {result.rank}: {result.title}")
            print(f"  URL: {result.url}")
            print(f"  Similarity: {result.similarity_score:.3f}, Relevance: {result.final_score:.3f}")
            print(f"  Preview: {result.content_preview[:100]}...")


async def example_3_hybrid_search(search_service: SemanticSearchService):
    """Example 3: Hybrid search (semantic + keyword)"""
    print("\n=== Example 3: Hybrid Search ===\n")
    
    query = "machine learning algorithms"
    
    # Compare different search strategies
    strategies = ["semantic", "keyword", "hybrid"]
    
    for strategy in strategies:
        print(f"\nStrategy: {strategy.upper()}")
        print("-" * 60)
        
        results, metrics = await search_service.search(
            query=query,
            top_k=3,
            search_strategy=strategy
        )
        
        print(f"Results: {len(results)}")
        for result in results[:2]:  # Show top 2
            print(f"  • {result.title} (score: {result.final_score:.3f})")


async def example_4_query_expansion():
    """Example 4: Query expansion techniques"""
    print("\n=== Example 4: Query Expansion ===\n")
    
    # Initialize query expander
    expander = QueryExpander(
        use_synonyms=True,
        use_concepts=True,
        max_expansions=10
    )
    
    queries = [
        "AI models",
        "website SEO",
        "data analysis"
    ]
    
    for query in queries:
        print(f"\nOriginal Query: '{query}'")
        print("-" * 60)
        
        # Expand query
        expanded = await expander.expand(query)
        
        print(f"Expanded Terms: {expanded.expanded_terms[:3]}")
        print(f"Synonyms: {expanded.synonyms[:3]}")
        print(f"Related Concepts: {expanded.related_concepts[:3]}")
        
        # Get weighted terms
        weighted = expanded.get_weighted_terms()
        print("\nWeighted Terms:")
        for term, weight in list(weighted.items())[:5]:
            print(f"  • {term}: {weight:.2f}")


async def example_5_similarity_search(search_service: SemanticSearchService):
    """Example 5: Find similar documents"""
    print("\n=== Example 5: Similar Document Search ===\n")
    
    # Find documents similar to content_id=1
    source_id = 1
    similar_docs = await search_service.get_similar_documents(
        content_id=source_id,
        top_k=3
    )
    
    print(f"Documents similar to content ID {source_id}:")
    print("-" * 60)
    
    for doc in similar_docs:
        print(f"\n  {doc.title}")
        print(f"  Similarity: {doc.similarity_score:.3f}")
        print(f"  URL: {doc.url}")


async def example_6_filtered_search(search_service: SemanticSearchService):
    """Example 6: Search with metadata filters"""
    print("\n=== Example 6: Filtered Search ===\n")
    
    query = "learning"
    
    # Search with category filter
    filters = {
        'category': 'AI/ML'
    }
    
    print(f"Query: '{query}' with filters: {filters}")
    print("-" * 60)
    
    results, metrics = await search_service.search(
        query=query,
        top_k=5,
        filters=filters,
        search_strategy="hybrid"
    )
    
    print(f"Found {len(results)} results")
    for result in results:
        print(f"\n  {result.title}")
        print(f"  Category: {result.metadata.get('category')}")
        print(f"  Tags: {result.metadata.get('tags')}")
        print(f"  Score: {result.final_score:.3f}")


async def example_7_advanced_ranking():
    """Example 7: Advanced relevance ranking"""
    print("\n=== Example 7: Advanced Relevance Ranking ===\n")
    
    search_service = SemanticSearchService(
        embedding_provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
        enable_query_expansion=True,
        enable_hybrid_search=True
    )
    
    # Index content with quality signals
    contents = [
        {
            'id': 10,
            'url': 'https://example.com/comprehensive-guide',
            'title': 'Comprehensive AI Guide',
            'content': 'Long detailed content about AI...' * 100,
            'metadata': {
                'category': 'AI/ML',
                'content_length': 5000,
                'has_images': True,
                'has_structured_data': True,
                'domain_authority': 0.8,
                'created_at': '2024-10-01T10:00:00'
            }
        },
        {
            'id': 11,
            'url': 'https://example.com/short-post',
            'title': 'AI Basics',
            'content': 'Short content about AI',
            'metadata': {
                'category': 'AI/ML',
                'content_length': 100,
                'has_images': False,
                'domain_authority': 0.3,
                'created_at': '2020-01-01T10:00:00'
            }
        }
    ]
    
    await search_service.index_contents_batch(contents)
    
    # Search and see ranking
    results, metrics = await search_service.search(
        query="artificial intelligence",
        top_k=5,
        search_strategy="hybrid"
    )
    
    print("Ranking breakdown:")
    print("-" * 60)
    
    for result in results:
        print(f"\n  Rank {result.rank}: {result.title}")
        print(f"  Similarity: {result.similarity_score:.3f}")
        print(f"  Keyword: {result.keyword_score:.3f}")
        print(f"  Final: {result.final_score:.3f}")
        print(f"  Explanation: {result.explanation}")


async def example_8_persistence():
    """Example 8: Save and load vector index"""
    print("\n=== Example 8: Index Persistence ===\n")
    
    # Create new service and index content
    search_service = SemanticSearchService()
    
    content = {
        'content_id': 100,
        'url': 'https://example.com/test',
        'title': 'Test Document',
        'content': 'This is a test document for persistence.',
        'metadata': {}
    }
    
    await search_service.index_content(**content)
    
    # Save index
    search_service.save_index()
    print("✓ Vector index saved to disk")
    
    # Create new service instance (loads from disk)
    new_service = SemanticSearchService()
    stats = new_service.get_search_stats()
    
    print(f"✓ Loaded index with {stats['total_indexed_documents']} documents")


async def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("SEMANTIC SEARCH SYSTEM - EXAMPLES")
    print("="*70)
    
    # Run examples
    search_service = await example_1_basic_indexing()
    await example_2_semantic_search(search_service)
    await example_3_hybrid_search(search_service)
    await example_4_query_expansion()
    await example_5_similarity_search(search_service)
    await example_6_filtered_search(search_service)
    await example_7_advanced_ranking()
    await example_8_persistence()
    
    print("\n" + "="*70)
    print("All examples completed successfully!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

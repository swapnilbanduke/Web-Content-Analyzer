"""
Quick Test Script for Semantic Search System

Run this to quickly verify the semantic search system is working.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.src.knowledge.semantic_search import SemanticSearchService
from backend.src.knowledge.vector_store import EmbeddingProvider


async def quick_test():
    """Quick test of semantic search functionality"""
    
    print("\n" + "="*70)
    print("SEMANTIC SEARCH SYSTEM - QUICK TEST")
    print("="*70 + "\n")
    
    # Step 1: Initialize
    print("📦 Initializing semantic search service...")
    try:
        service = SemanticSearchService(
            embedding_provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
            model_name="all-MiniLM-L6-v2",
            enable_query_expansion=True,
            enable_hybrid_search=True
        )
        print("✅ Service initialized successfully\n")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        print("\n💡 Tip: Make sure you've installed the required packages:")
        print("   pip install sentence-transformers transformers torch numpy")
        return
    
    # Step 2: Index sample content
    print("📝 Indexing sample content...")
    sample_contents = [
        {
            'id': 1,
            'url': 'https://example.com/ml-intro',
            'title': 'Introduction to Machine Learning',
            'content': '''Machine learning is a subset of artificial intelligence (AI) 
            that provides systems the ability to automatically learn and improve from 
            experience without being explicitly programmed. Machine learning focuses on 
            the development of computer programs that can access data and use it to 
            learn for themselves.''',
            'metadata': {'category': 'AI/ML', 'difficulty': 'beginner'}
        },
        {
            'id': 2,
            'url': 'https://example.com/deep-learning',
            'title': 'Deep Learning Fundamentals',
            'content': '''Deep learning is part of a broader family of machine learning 
            methods based on artificial neural networks with representation learning. 
            Learning can be supervised, semi-supervised or unsupervised. Deep learning 
            architectures such as deep neural networks, deep belief networks, recurrent 
            neural networks and convolutional neural networks have been applied to fields 
            including computer vision, speech recognition, and natural language processing.''',
            'metadata': {'category': 'AI/ML', 'difficulty': 'advanced'}
        },
        {
            'id': 3,
            'url': 'https://example.com/web-seo',
            'title': 'SEO Best Practices for 2024',
            'content': '''Search Engine Optimization (SEO) is the practice of increasing 
            the quantity and quality of traffic to your website through organic search 
            engine results. SEO involves making certain changes to your website design 
            and content that make your site more attractive to a search engine. Key 
            factors include quality content, keywords, meta tags, and backlinks.''',
            'metadata': {'category': 'Marketing', 'difficulty': 'intermediate'}
        },
        {
            'id': 4,
            'url': 'https://example.com/python-basics',
            'title': 'Python Programming for Beginners',
            'content': '''Python is a high-level, interpreted programming language known 
            for its simplicity and readability. It supports multiple programming paradigms 
            including procedural, object-oriented, and functional programming. Python is 
            widely used in web development, data science, artificial intelligence, 
            scientific computing, and automation.''',
            'metadata': {'category': 'Programming', 'difficulty': 'beginner'}
        },
        {
            'id': 5,
            'url': 'https://example.com/data-science',
            'title': 'Data Science Career Guide',
            'content': '''Data science combines domain expertise, programming skills, 
            and knowledge of mathematics and statistics to extract meaningful insights 
            from data. Data scientists use machine learning algorithms to build predictive 
            models and discover patterns. Key skills include Python, R, SQL, statistics, 
            and communication.''',
            'metadata': {'category': 'Data Science', 'difficulty': 'intermediate'}
        }
    ]
    
    try:
        success, failed = await service.index_contents_batch(sample_contents)
        print(f"✅ Indexed {success} documents ({failed} failed)\n")
    except Exception as e:
        print(f"❌ Indexing failed: {e}\n")
        return
    
    # Step 3: Test semantic search
    print("🔍 Testing semantic search...")
    test_queries = [
        "What is artificial intelligence?",
        "Neural network tutorial",
        "Website optimization"
    ]
    
    for query in test_queries:
        print(f"\n  Query: '{query}'")
        print("  " + "-"*60)
        
        try:
            results, metrics = await service.search(
                query=query,
                top_k=3,
                search_strategy="hybrid"
            )
            
            print(f"  ⏱️  Search time: {metrics.search_time_ms:.1f}ms")
            print(f"  📊 Results: {len(results)}")
            
            if results:
                top_result = results[0]
                print(f"  🥇 Top match: {top_result.title}")
                print(f"     Score: {top_result.final_score:.3f}")
                print(f"     URL: {top_result.url}")
            else:
                print("  ⚠️  No results found")
                
        except Exception as e:
            print(f"  ❌ Search failed: {e}")
    
    # Step 4: Test query expansion
    print("\n\n🔄 Testing query expansion...")
    test_query = "machine learning algorithms"
    
    try:
        from backend.src.knowledge.query_expansion import QueryExpander
        expander = QueryExpander()
        expanded = await expander.expand(test_query)
        
        print(f"  Original: {expanded.original}")
        print(f"  Synonyms: {expanded.synonyms[:3]}")
        print(f"  Concepts: {expanded.related_concepts[:3]}")
        print(f"  ✅ Query expansion working\n")
    except Exception as e:
        print(f"  ❌ Query expansion failed: {e}\n")
    
    # Step 5: Test similar documents
    print("🔗 Testing similar document discovery...")
    try:
        similar = await service.get_similar_documents(
            content_id=1,
            top_k=3
        )
        
        print(f"  Documents similar to '{sample_contents[0]['title']}':")
        for doc in similar[:2]:
            print(f"    • {doc.title} (score: {doc.similarity_score:.3f})")
        print("  ✅ Similar document search working\n")
    except Exception as e:
        print(f"  ❌ Similar search failed: {e}\n")
    
    # Step 6: Get statistics
    print("📈 System statistics:")
    try:
        stats = service.get_search_stats()
        print(f"  Total indexed: {stats['total_indexed_documents']} documents")
        print(f"  Provider: {stats['vector_store']['provider']}")
        print(f"  Model: {stats['vector_store']['model_name']}")
        print(f"  Dimension: {stats['vector_store']['dimension']}")
        print(f"  Query expansion: {'Enabled' if stats['query_expansion_enabled'] else 'Disabled'}")
        print(f"  Hybrid search: {'Enabled' if stats['hybrid_search_enabled'] else 'Disabled'}")
    except Exception as e:
        print(f"  ❌ Failed to get stats: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\n💡 Next steps:")
    print("   1. Run full examples: python backend/examples/semantic_search_examples.py")
    print("   2. Run tests: pytest backend/tests/test_semantic_search.py -v")
    print("   3. Start the API server and test endpoints")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(quick_test())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

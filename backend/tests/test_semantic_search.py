"""
Tests for Semantic Search System

Tests vector embeddings, query expansion, and semantic search functionality.
"""

import pytest
import numpy as np
from datetime import datetime

from backend.src.knowledge.vector_store import (
    VectorStore,
    VectorDocument,
    SearchResult,
    EmbeddingProvider
)
from backend.src.knowledge.query_expansion import (
    QueryExpander,
    ExpandedQuery,
    SemanticQueryRewriter
)
from backend.src.knowledge.semantic_search import (
    SemanticSearchService,
    SemanticSearchResult
)


class TestVectorStore:
    """Test VectorStore functionality"""
    
    @pytest.fixture
    def vector_store(self):
        """Create a vector store for testing"""
        return VectorStore(
            provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
            model_name="all-MiniLM-L6-v2",
            storage_path="data/test_vectors"
        )
    
    @pytest.mark.asyncio
    async def test_embed_text(self, vector_store):
        """Test text embedding generation"""
        text = "This is a test document about machine learning"
        embedding = await vector_store.embed_text(text)
        
        assert isinstance(embedding, np.ndarray)
        assert len(embedding) > 0
        assert embedding.dtype == np.float32 or embedding.dtype == np.float64
    
    @pytest.mark.asyncio
    async def test_embed_batch(self, vector_store):
        """Test batch embedding generation"""
        texts = [
            "Machine learning is fascinating",
            "Deep learning uses neural networks",
            "Natural language processing is important"
        ]
        
        embeddings = await vector_store.embed_batch(texts)
        
        assert len(embeddings) == len(texts)
        assert all(isinstance(emb, np.ndarray) for emb in embeddings)
        
        # All embeddings should have same dimension
        dimensions = [len(emb) for emb in embeddings]
        assert len(set(dimensions)) == 1
    
    @pytest.mark.asyncio
    async def test_add_document(self, vector_store):
        """Test adding a document"""
        doc = await vector_store.add_document(
            doc_id="test_1",
            content="This is a test document",
            metadata={'category': 'test'}
        )
        
        assert isinstance(doc, VectorDocument)
        assert doc.id == "test_1"
        assert doc.content == "This is a test document"
        assert doc.metadata['category'] == 'test'
        assert len(doc.embedding) > 0
    
    @pytest.mark.asyncio
    async def test_add_documents_batch(self, vector_store):
        """Test batch document addition"""
        documents = [
            {
                'id': 'batch_1',
                'content': 'First document',
                'metadata': {'type': 'test'}
            },
            {
                'id': 'batch_2',
                'content': 'Second document',
                'metadata': {'type': 'test'}
            }
        ]
        
        docs = await vector_store.add_documents(documents)
        
        assert len(docs) == 2
        assert all(isinstance(d, VectorDocument) for d in docs)
        assert vector_store.get_document('batch_1') is not None
        assert vector_store.get_document('batch_2') is not None
    
    @pytest.mark.asyncio
    async def test_search(self, vector_store):
        """Test semantic search"""
        # Add test documents
        await vector_store.add_documents([
            {'id': 'ml_1', 'content': 'Machine learning is a field of AI'},
            {'id': 'dl_1', 'content': 'Deep learning uses neural networks'},
            {'id': 'nlp_1', 'content': 'Natural language processing for text'}
        ])
        
        # Search
        results = await vector_store.search(
            query="artificial intelligence machine learning",
            top_k=2
        )
        
        assert len(results) > 0
        assert all(isinstance(r, SearchResult) for r in results)
        assert results[0].similarity_score >= results[1].similarity_score  # Sorted by score
    
    def test_compute_similarity_cosine(self, vector_store):
        """Test cosine similarity computation"""
        # Create sample embeddings
        query_emb = np.array([1.0, 0.0, 0.0])
        vector_store.embeddings_matrix = np.array([
            [1.0, 0.0, 0.0],  # Perfect match
            [0.0, 1.0, 0.0],  # Orthogonal
            [0.5, 0.5, 0.0]   # Partial match
        ])
        
        similarities = vector_store.compute_similarity(query_emb, method="cosine")
        
        assert len(similarities) == 3
        assert abs(similarities[0] - 1.0) < 0.01  # Perfect match
        assert abs(similarities[1] - 0.0) < 0.01  # No match
        assert 0.0 < similarities[2] < 1.0  # Partial match
    
    def test_compute_similarity_dot_product(self, vector_store):
        """Test dot product similarity"""
        query_emb = np.array([2.0, 1.0])
        vector_store.embeddings_matrix = np.array([
            [1.0, 1.0],
            [2.0, 0.0]
        ])
        
        similarities = vector_store.compute_similarity(query_emb, method="dot_product")
        
        assert len(similarities) == 2
        assert similarities[0] == 3.0  # 2*1 + 1*1
        assert similarities[1] == 4.0  # 2*2 + 1*0
    
    @pytest.mark.asyncio
    async def test_delete_document(self, vector_store):
        """Test document deletion"""
        await vector_store.add_document(
            doc_id="delete_test",
            content="Document to delete"
        )
        
        assert vector_store.get_document("delete_test") is not None
        
        success = vector_store.delete_document("delete_test")
        
        assert success is True
        assert vector_store.get_document("delete_test") is None
    
    def test_get_stats(self, vector_store):
        """Test statistics retrieval"""
        stats = vector_store.get_stats()
        
        assert 'total_documents' in stats
        assert 'provider' in stats
        assert 'model_name' in stats
        assert 'dimension' in stats


class TestQueryExpander:
    """Test QueryExpander functionality"""
    
    @pytest.fixture
    def expander(self):
        """Create a query expander"""
        return QueryExpander(
            use_synonyms=True,
            use_concepts=True,
            max_expansions=10
        )
    
    @pytest.mark.asyncio
    async def test_basic_expansion(self, expander):
        """Test basic query expansion"""
        query = "machine learning"
        expanded = await expander.expand(query)
        
        assert isinstance(expanded, ExpandedQuery)
        assert expanded.original == query
        assert len(expanded.get_all_terms()) > 1  # Should have expansions
    
    @pytest.mark.asyncio
    async def test_synonym_expansion(self, expander):
        """Test synonym expansion"""
        query = "ai models"
        expanded = await expander.expand(query)
        
        # Should find synonyms for 'ai'
        all_terms = expanded.get_all_terms()
        assert any('artificial intelligence' in term.lower() for term in all_terms)
    
    @pytest.mark.asyncio
    async def test_domain_expansion(self, expander):
        """Test domain-specific expansion"""
        query = "seo optimization"
        expanded = await expander.expand(query)
        
        # Should expand SEO-related concepts
        related = [term.lower() for term in expanded.related_concepts]
        assert len(related) > 0
    
    @pytest.mark.asyncio
    async def test_weighted_terms(self, expander):
        """Test term weighting"""
        query = "search algorithms"
        expanded = await expander.expand(query)
        
        weighted = expanded.get_weighted_terms()
        
        assert isinstance(weighted, dict)
        assert len(weighted) > 0
        
        # Original terms should have highest weight
        for word in query.split():
            if word in weighted:
                assert weighted[word] == 1.0
    
    def test_extract_terms(self, expander):
        """Test term extraction"""
        query = "The quick brown fox jumps over the lazy dog"
        terms = expander._extract_terms(query)
        
        # Should remove stop words
        assert 'the' not in terms
        assert 'over' not in terms
        
        # Should keep meaningful words
        assert 'quick' in terms
        assert 'brown' in terms
        assert 'fox' in terms
    
    def test_extract_ngrams(self, expander):
        """Test n-gram extraction"""
        text = "machine learning algorithms"
        bigrams = expander._extract_ngrams(text, n=2)
        
        assert 'machine learning' in bigrams
        assert 'learning algorithms' in bigrams
        assert len(bigrams) == 2
    
    def test_spell_correction(self, expander):
        """Test spelling correction"""
        assert expander._spell_correct('machien') == 'machine'
        assert expander._spell_correct('learing') == 'learning'
        assert expander._spell_correct('correct') == 'correct'  # Already correct
    
    def test_generate_variations(self, expander):
        """Test word variations"""
        terms = ['learn', 'optimize']
        variations = expander._generate_variations(terms)
        
        # Should generate plurals and -ing forms
        assert 'learning' in variations
        assert 'optimizing' in variations


class TestSemanticQueryRewriter:
    """Test SemanticQueryRewriter functionality"""
    
    @pytest.fixture
    def rewriter(self):
        """Create a query rewriter"""
        return SemanticQueryRewriter()
    
    def test_rewrite_what_question(self, rewriter):
        """Test 'what is' question rewriting"""
        query = "what is machine learning"
        rewritten = rewriter.rewrite(query)
        
        assert "definition" in rewritten or "explanation" in rewritten
    
    def test_rewrite_how_question(self, rewriter):
        """Test 'how to' question rewriting"""
        query = "how to optimize seo"
        rewritten = rewriter.rewrite(query)
        
        assert "tutorial" in rewritten or "guide" in rewritten or "steps" in rewritten
    
    def test_detect_intent_transactional(self, rewriter):
        """Test transactional intent detection"""
        query = "buy machine learning course"
        intent = rewriter.detect_intent(query)
        
        assert intent == "transactional"
    
    def test_detect_intent_navigational(self, rewriter):
        """Test navigational intent detection"""
        query = "login to website"
        intent = rewriter.detect_intent(query)
        
        assert intent == "navigational"
    
    def test_detect_intent_informational(self, rewriter):
        """Test informational intent detection"""
        query = "machine learning tutorial"
        intent = rewriter.detect_intent(query)
        
        assert intent == "informational"


class TestSemanticSearchService:
    """Test SemanticSearchService functionality"""
    
    @pytest.fixture
    def search_service(self):
        """Create a semantic search service"""
        return SemanticSearchService(
            embedding_provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
            enable_query_expansion=True,
            enable_hybrid_search=True
        )
    
    @pytest.mark.asyncio
    async def test_index_content(self, search_service):
        """Test content indexing"""
        success = await search_service.index_content(
            content_id=1,
            url="https://test.com",
            title="Test Document",
            content="This is a test document about AI",
            metadata={'category': 'test'}
        )
        
        assert success is True
    
    @pytest.mark.asyncio
    async def test_index_batch(self, search_service):
        """Test batch indexing"""
        contents = [
            {
                'id': 1,
                'url': 'https://test.com/1',
                'title': 'Doc 1',
                'content': 'Content 1',
                'metadata': {}
            },
            {
                'id': 2,
                'url': 'https://test.com/2',
                'title': 'Doc 2',
                'content': 'Content 2',
                'metadata': {}
            }
        ]
        
        success, failed = await search_service.index_contents_batch(contents)
        
        assert success == 2
        assert failed == 0
    
    @pytest.mark.asyncio
    async def test_semantic_search(self, search_service):
        """Test semantic search"""
        # Index test documents
        await search_service.index_contents_batch([
            {
                'id': 10,
                'url': 'https://test.com/ml',
                'title': 'Machine Learning Guide',
                'content': 'Machine learning is a subset of AI',
                'metadata': {'category': 'AI'}
            },
            {
                'id': 11,
                'url': 'https://test.com/seo',
                'title': 'SEO Tips',
                'content': 'Search engine optimization techniques',
                'metadata': {'category': 'Marketing'}
            }
        ])
        
        # Search
        results, metrics = await search_service.search(
            query="artificial intelligence",
            top_k=5,
            search_strategy="semantic"
        )
        
        assert len(results) > 0
        assert isinstance(metrics.search_time_ms, float)
        assert metrics.total_results == len(results)
        
        # First result should be ML-related
        assert 'machine learning' in results[0].content_preview.lower() or \
               'ai' in results[0].content_preview.lower()
    
    @pytest.mark.asyncio
    async def test_hybrid_search(self, search_service):
        """Test hybrid search"""
        # Index documents
        await search_service.index_content(
            content_id=20,
            url="https://test.com/hybrid",
            title="Hybrid Test",
            content="Testing hybrid search with keywords and semantics"
        )
        
        results, metrics = await search_service.search(
            query="hybrid search",
            top_k=5,
            search_strategy="hybrid"
        )
        
        assert len(results) > 0
        assert all(hasattr(r, 'similarity_score') for r in results)
        assert all(hasattr(r, 'keyword_score') for r in results)
    
    @pytest.mark.asyncio
    async def test_filtered_search(self, search_service):
        """Test search with filters"""
        # Index documents with categories
        await search_service.index_contents_batch([
            {
                'id': 30,
                'url': 'https://test.com/ai1',
                'title': 'AI Doc 1',
                'content': 'AI content',
                'metadata': {'category': 'AI'}
            },
            {
                'id': 31,
                'url': 'https://test.com/marketing1',
                'title': 'Marketing Doc 1',
                'content': 'Marketing content',
                'metadata': {'category': 'Marketing'}
            }
        ])
        
        # Search with filter
        results, metrics = await search_service.search(
            query="content",
            top_k=10,
            filters={'category': 'AI'}
        )
        
        # All results should have AI category
        assert all(r.metadata.get('category') == 'AI' for r in results)
    
    @pytest.mark.asyncio
    async def test_similar_documents(self, search_service):
        """Test finding similar documents"""
        # Index documents
        await search_service.index_contents_batch([
            {
                'id': 40,
                'url': 'https://test.com/ml1',
                'title': 'ML Tutorial',
                'content': 'Machine learning tutorial for beginners',
                'metadata': {}
            },
            {
                'id': 41,
                'url': 'https://test.com/ml2',
                'title': 'ML Advanced',
                'content': 'Advanced machine learning techniques',
                'metadata': {}
            }
        ])
        
        # Find similar to doc 40
        similar = await search_service.get_similar_documents(
            content_id=40,
            top_k=3
        )
        
        assert len(similar) > 0
        # Should not include source document
        assert all(s.content_id != 40 for s in similar)
    
    def test_get_stats(self, search_service):
        """Test statistics retrieval"""
        stats = search_service.get_search_stats()
        
        assert 'vector_store' in stats
        assert 'query_expansion_enabled' in stats
        assert 'hybrid_search_enabled' in stats
        assert 'total_indexed_documents' in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Semantic Search Service - Advanced search with vector embeddings

Integrates:
- Vector embeddings (OpenAI/Sentence Transformers)
- Query expansion
- Similarity scoring
- Relevance ranking
- Hybrid search (semantic + keyword)
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
import asyncio

from .vector_store import VectorStore, SearchResult, EmbeddingProvider
from .query_expansion import QueryExpander, ExpandedQuery, SemanticQueryRewriter
from ..storage.content_store import ContentStore

logger = logging.getLogger(__name__)


@dataclass
class SemanticSearchResult:
    """Enhanced search result with multiple scoring dimensions"""
    content_id: int
    url: str
    title: str
    content_preview: str
    similarity_score: float
    relevance_score: float
    keyword_score: float
    final_score: float
    rank: int
    matched_terms: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    explanation: str = ""


@dataclass
class SearchMetrics:
    """Search performance metrics"""
    query: str
    total_results: int
    search_time_ms: float
    vectorization_time_ms: float
    ranking_time_ms: float
    expansion_terms: List[str]
    filters_applied: Dict[str, Any]


class SemanticSearchService:
    """
    High-performance semantic search engine.
    
    Features:
    - Vector similarity search using embeddings
    - Query expansion for better recall
    - Hybrid search (semantic + keyword)
    - Multi-factor relevance ranking
    - Configurable search strategies
    """
    
    def __init__(
        self,
        embedding_provider: EmbeddingProvider = EmbeddingProvider.SENTENCE_TRANSFORMERS,
        model_name: Optional[str] = None,
        storage_path: str = "data/vectors",
        enable_query_expansion: bool = True,
        enable_hybrid_search: bool = True
    ):
        """
        Initialize semantic search service.
        
        Args:
            embedding_provider: Provider for embeddings
            model_name: Specific model to use
            storage_path: Path for vector storage
            enable_query_expansion: Enable query expansion
            enable_hybrid_search: Enable hybrid search (semantic + keyword)
        """
        # Initialize vector store
        self.vector_store = VectorStore(
            provider=embedding_provider,
            model_name=model_name,
            storage_path=storage_path
        )
        
        # Initialize query expansion
        self.enable_query_expansion = enable_query_expansion
        if enable_query_expansion:
            self.query_expander = QueryExpander(
                use_synonyms=True,
                use_concepts=True,
                max_expansions=10
            )
            self.query_rewriter = SemanticQueryRewriter()
        
        # Enable hybrid search
        self.enable_hybrid_search = enable_hybrid_search
        
        # Content store for keyword search
        self.content_store = ContentStore()
        
        logger.info(
            f"SemanticSearchService initialized with provider={embedding_provider}, "
            f"expansion={enable_query_expansion}, hybrid={enable_hybrid_search}"
        )
    
    async def index_content(
        self,
        content_id: int,
        url: str,
        title: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Index content for semantic search.
        
        Args:
            content_id: Unique content identifier
            url: Content URL
            title: Content title
            content: Full content text
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        try:
            # Prepare document
            doc_id = f"content_{content_id}"
            
            # Combine title and content for better embeddings
            full_text = f"{title}\n\n{content}"
            
            # Add metadata
            doc_metadata = metadata or {}
            doc_metadata.update({
                'content_id': content_id,
                'url': url,
                'title': title,
                'indexed_at': datetime.now().isoformat()
            })
            
            # Add to vector store
            await self.vector_store.add_document(
                doc_id=doc_id,
                content=full_text,
                metadata=doc_metadata
            )
            
            logger.info(f"Indexed content {content_id} for semantic search")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index content {content_id}: {e}")
            return False
    
    async def index_contents_batch(
        self,
        contents: List[Dict[str, Any]]
    ) -> Tuple[int, int]:
        """
        Index multiple contents in batch.
        
        Args:
            contents: List of content dicts with id, url, title, content, metadata
            
        Returns:
            Tuple of (success_count, failure_count)
        """
        documents = []
        
        for content in contents:
            doc_id = f"content_{content['id']}"
            full_text = f"{content['title']}\n\n{content['content']}"
            
            metadata = content.get('metadata', {})
            metadata.update({
                'content_id': content['id'],
                'url': content['url'],
                'title': content['title'],
                'indexed_at': datetime.now().isoformat()
            })
            
            documents.append({
                'id': doc_id,
                'content': full_text,
                'metadata': metadata
            })
        
        try:
            await self.vector_store.add_documents(documents)
            logger.info(f"Batch indexed {len(documents)} contents")
            return len(documents), 0
        except Exception as e:
            logger.error(f"Batch indexing failed: {e}")
            return 0, len(documents)
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        min_score: float = 0.3,
        search_strategy: str = "hybrid"
    ) -> Tuple[List[SemanticSearchResult], SearchMetrics]:
        """
        Perform semantic search.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filters: Optional metadata filters
            min_score: Minimum similarity score threshold
            search_strategy: 'semantic', 'keyword', or 'hybrid'
            
        Returns:
            Tuple of (results, metrics)
        """
        start_time = datetime.now()
        
        # Step 1: Query preprocessing
        processed_query = query
        expansion_terms = []
        
        if self.enable_query_expansion:
            # Rewrite query
            processed_query = self.query_rewriter.rewrite(query)
            
            # Expand query
            expanded = await self.query_expander.expand(processed_query)
            expansion_terms = expanded.get_all_terms()
            
            logger.debug(f"Expanded query: {expansion_terms}")
        
        expansion_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Step 2: Execute search based on strategy
        if search_strategy == "semantic":
            results = await self._semantic_search(
                processed_query,
                top_k=top_k * 2,  # Get more for re-ranking
                filters=filters,
                min_score=min_score
            )
        elif search_strategy == "keyword":
            results = await self._keyword_search(
                processed_query,
                expansion_terms,
                top_k=top_k * 2,
                filters=filters
            )
        else:  # hybrid
            results = await self._hybrid_search(
                processed_query,
                expansion_terms,
                top_k=top_k * 2,
                filters=filters,
                min_score=min_score
            )
        
        search_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Step 3: Re-rank results
        ranked_results = await self._rerank_results(
            query,
            results,
            top_k=top_k
        )
        
        total_time = (datetime.now() - start_time).total_seconds() * 1000
        ranking_time = total_time - search_time
        
        # Create metrics
        metrics = SearchMetrics(
            query=query,
            total_results=len(ranked_results),
            search_time_ms=total_time,
            vectorization_time_ms=expansion_time,
            ranking_time_ms=ranking_time,
            expansion_terms=expansion_terms,
            filters_applied=filters or {}
        )
        
        return ranked_results, metrics
    
    async def _semantic_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]],
        min_score: float
    ) -> List[SearchResult]:
        """Pure semantic search using vectors"""
        results = await self.vector_store.search(
            query=query,
            top_k=top_k,
            similarity_method="cosine",
            min_score=min_score,
            filters=filters
        )
        return results
    
    async def _keyword_search(
        self,
        query: str,
        expansion_terms: List[str],
        top_k: int,
        filters: Optional[Dict[str, Any]]
    ) -> List[SearchResult]:
        """Keyword-based search with expansion"""
        # Use expanded terms for better recall
        search_terms = [query] + expansion_terms[:5]
        combined_query = ' '.join(search_terms)
        
        # Search in content store
        keyword_results = self.content_store.search_content(
            combined_query,
            limit=top_k
        )
        
        # Convert to SearchResult format
        results = []
        for idx, result in enumerate(keyword_results):
            doc_id = f"content_{result['id']}"
            doc = self.vector_store.get_document(doc_id)
            
            if doc:
                # Calculate keyword score
                keyword_score = self._calculate_keyword_score(
                    query,
                    result.get('content', ''),
                    expansion_terms
                )
                
                search_result = SearchResult(
                    document=doc,
                    similarity_score=0.0,  # No vector similarity
                    relevance_score=keyword_score,
                    rank=idx + 1,
                    matched_keywords=expansion_terms[:3]
                )
                results.append(search_result)
        
        return results
    
    async def _hybrid_search(
        self,
        query: str,
        expansion_terms: List[str],
        top_k: int,
        filters: Optional[Dict[str, Any]],
        min_score: float
    ) -> List[SearchResult]:
        """Hybrid search combining semantic and keyword"""
        # Run both searches in parallel
        semantic_task = self._semantic_search(query, top_k, filters, min_score)
        keyword_task = self._keyword_search(query, expansion_terms, top_k, filters)
        
        semantic_results, keyword_results = await asyncio.gather(
            semantic_task,
            keyword_task
        )
        
        # Merge results using Reciprocal Rank Fusion (RRF)
        merged = self._merge_results_rrf(semantic_results, keyword_results)
        
        return merged[:top_k]
    
    def _merge_results_rrf(
        self,
        semantic_results: List[SearchResult],
        keyword_results: List[SearchResult],
        k: int = 60
    ) -> List[SearchResult]:
        """
        Merge results using Reciprocal Rank Fusion.
        
        RRF score = sum(1 / (k + rank))
        """
        scores = {}
        
        # Process semantic results
        for rank, result in enumerate(semantic_results, 1):
            doc_id = result.document.id
            rrf_score = 1.0 / (k + rank)
            scores[doc_id] = scores.get(doc_id, 0) + rrf_score * 0.6  # Weight semantic higher
        
        # Process keyword results
        for rank, result in enumerate(keyword_results, 1):
            doc_id = result.document.id
            rrf_score = 1.0 / (k + rank)
            scores[doc_id] = scores.get(doc_id, 0) + rrf_score * 0.4
        
        # Create merged results
        doc_map = {}
        for result in semantic_results + keyword_results:
            doc_map[result.document.id] = result
        
        merged = []
        for doc_id, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            if doc_id in doc_map:
                result = doc_map[doc_id]
                result.relevance_score = score
                merged.append(result)
        
        return merged
    
    def _calculate_keyword_score(
        self,
        query: str,
        content: str,
        expansion_terms: List[str]
    ) -> float:
        """Calculate keyword matching score"""
        query_terms = set(query.lower().split())
        expansion_set = set(expansion_terms)
        content_lower = content.lower()
        
        # Count matches
        direct_matches = sum(1 for term in query_terms if term in content_lower)
        expansion_matches = sum(1 for term in expansion_set if term in content_lower)
        
        # Calculate score
        direct_score = direct_matches / max(len(query_terms), 1)
        expansion_score = expansion_matches / max(len(expansion_set), 1)
        
        return 0.7 * direct_score + 0.3 * expansion_score
    
    async def _rerank_results(
        self,
        query: str,
        results: List[SearchResult],
        top_k: int
    ) -> List[SemanticSearchResult]:
        """
        Advanced re-ranking with multiple signals.
        
        Combines:
        - Semantic similarity
        - Keyword relevance
        - Document quality signals
        - Freshness
        """
        reranked = []
        query_terms = set(query.lower().split())
        
        for result in results:
            doc = result.document
            metadata = doc.metadata
            
            # Get scores
            similarity_score = result.similarity_score
            relevance_score = result.relevance_score
            
            # Keyword score
            content_lower = doc.content.lower()
            keyword_matches = sum(1 for term in query_terms if term in content_lower)
            keyword_score = keyword_matches / max(len(query_terms), 1)
            
            # Quality signals
            quality_score = self._calculate_quality_score(metadata)
            
            # Freshness score
            freshness_score = self._calculate_freshness_score(metadata)
            
            # Combined final score
            final_score = (
                0.4 * similarity_score +
                0.3 * relevance_score +
                0.15 * keyword_score +
                0.1 * quality_score +
                0.05 * freshness_score
            )
            
            # Create semantic search result
            content_preview = doc.content[:300] + "..." if len(doc.content) > 300 else doc.content
            
            semantic_result = SemanticSearchResult(
                content_id=metadata.get('content_id', 0),
                url=metadata.get('url', ''),
                title=metadata.get('title', ''),
                content_preview=content_preview,
                similarity_score=similarity_score,
                relevance_score=relevance_score,
                keyword_score=keyword_score,
                final_score=final_score,
                rank=0,  # Will be set after sorting
                matched_terms=result.matched_keywords,
                metadata=metadata,
                explanation=result.explanation or ""
            )
            
            reranked.append(semantic_result)
        
        # Sort by final score
        reranked.sort(key=lambda x: x.final_score, reverse=True)
        
        # Update ranks and limit
        for rank, result in enumerate(reranked[:top_k], 1):
            result.rank = rank
        
        return reranked[:top_k]
    
    def _calculate_quality_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate document quality score from metadata"""
        score = 0.5  # Base score
        
        # Longer content is generally better
        if 'content_length' in metadata:
            length = metadata['content_length']
            if length > 1000:
                score += 0.2
            elif length > 500:
                score += 0.1
        
        # Has images
        if metadata.get('has_images', False):
            score += 0.1
        
        # Has structured data
        if metadata.get('has_structured_data', False):
            score += 0.1
        
        # Domain authority (if available)
        if 'domain_authority' in metadata:
            score += metadata['domain_authority'] * 0.1
        
        return min(score, 1.0)
    
    def _calculate_freshness_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate freshness score based on content age"""
        if 'created_at' not in metadata and 'indexed_at' not in metadata:
            return 0.5
        
        try:
            date_str = metadata.get('created_at') or metadata.get('indexed_at')
            content_date = datetime.fromisoformat(date_str)
            age_days = (datetime.now() - content_date).days
            
            # Exponential decay
            import math
            freshness = math.exp(-age_days / 365.0)
            return freshness
        except:
            return 0.5
    
    async def get_similar_documents(
        self,
        content_id: int,
        top_k: int = 5
    ) -> List[SemanticSearchResult]:
        """
        Find similar documents to a given document.
        
        Args:
            content_id: Source content ID
            top_k: Number of similar documents to return
            
        Returns:
            List of similar documents
        """
        doc_id = f"content_{content_id}"
        source_doc = self.vector_store.get_document(doc_id)
        
        if not source_doc:
            logger.warning(f"Document {content_id} not found in vector store")
            return []
        
        # Use document content as query
        results, _ = await self.search(
            query=source_doc.content[:500],  # Use first 500 chars
            top_k=top_k + 1,  # +1 to exclude source
            search_strategy="semantic"
        )
        
        # Filter out the source document
        similar = [r for r in results if r.content_id != content_id]
        
        return similar[:top_k]
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search system statistics"""
        vector_stats = self.vector_store.get_stats()
        
        return {
            'vector_store': vector_stats,
            'query_expansion_enabled': self.enable_query_expansion,
            'hybrid_search_enabled': self.enable_hybrid_search,
            'total_indexed_documents': vector_stats['total_documents']
        }
    
    async def rebuild_index(self):
        """Rebuild the entire search index"""
        logger.info("Rebuilding search index...")
        
        # Get all content from store
        # This would need to be implemented based on your content store
        # For now, we'll just rebuild the vector index
        self.vector_store._rebuild_index()
        
        logger.info("Search index rebuilt successfully")
    
    def save_index(self):
        """Save vector index to disk"""
        self.vector_store.save()
        logger.info("Search index saved")

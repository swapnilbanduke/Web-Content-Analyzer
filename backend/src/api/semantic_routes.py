"""
Semantic Search API Routes

REST API endpoints for vector embedding and semantic search functionality.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from ..knowledge.semantic_search import SemanticSearchService, SemanticSearchResult, SearchMetrics
from ..knowledge.vector_store import EmbeddingProvider
from ..knowledge.query_expansion import QueryExpander

# Initialize router
router = APIRouter(prefix="/api/v1/semantic", tags=["Semantic Search"])

# Global service instance (can be dependency-injected)
_search_service: Optional[SemanticSearchService] = None


def get_search_service() -> SemanticSearchService:
    """Get or create semantic search service"""
    global _search_service
    if _search_service is None:
        _search_service = SemanticSearchService(
            embedding_provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
            enable_query_expansion=True,
            enable_hybrid_search=True
        )
    return _search_service


# ==================== Request/Response Models ====================

class IndexContentRequest(BaseModel):
    """Request to index content"""
    content_id: int = Field(..., description="Unique content identifier")
    url: str = Field(..., description="Content URL")
    title: str = Field(..., description="Content title")
    content: str = Field(..., description="Full content text")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class BatchIndexRequest(BaseModel):
    """Request to index multiple contents"""
    contents: List[IndexContentRequest] = Field(..., description="List of contents to index")


class SearchRequest(BaseModel):
    """Semantic search request"""
    query: str = Field(..., description="Search query", min_length=1)
    top_k: int = Field(default=10, description="Number of results", ge=1, le=100)
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filters")
    min_score: float = Field(default=0.0, description="Minimum similarity score", ge=0.0, le=1.0)
    search_strategy: str = Field(
        default="hybrid",
        description="Search strategy",
        pattern="^(semantic|keyword|hybrid)$"
    )


class SearchResultResponse(BaseModel):
    """Search result response"""
    content_id: int
    url: str
    title: str
    content_preview: str
    similarity_score: float
    relevance_score: float
    keyword_score: float
    final_score: float
    rank: int
    matched_terms: List[str]
    metadata: Dict[str, Any]
    explanation: str


class SearchResponse(BaseModel):
    """Search response with results and metrics"""
    results: List[SearchResultResponse]
    metrics: Dict[str, Any]
    query: str
    total_results: int
    search_time_ms: float


class QueryExpansionResponse(BaseModel):
    """Query expansion response"""
    original: str
    expanded_terms: List[str]
    synonyms: List[str]
    related_concepts: List[str]
    weighted_terms: Dict[str, float]


class SimilarDocumentsRequest(BaseModel):
    """Request for similar documents"""
    content_id: int = Field(..., description="Source content ID")
    top_k: int = Field(default=5, description="Number of similar documents", ge=1, le=50)


class StatsResponse(BaseModel):
    """Search system statistics"""
    total_indexed_documents: int
    vector_store_provider: str
    embedding_model: str
    embedding_dimension: int
    query_expansion_enabled: bool
    hybrid_search_enabled: bool


# ==================== API Endpoints ====================

@router.post("/index", summary="Index content for semantic search")
async def index_content(
    request: IndexContentRequest,
    service: SemanticSearchService = Depends(get_search_service)
) -> Dict[str, Any]:
    """
    Index a single content for semantic search.
    
    This creates vector embeddings and stores them for efficient similarity search.
    """
    try:
        success = await service.index_content(
            content_id=request.content_id,
            url=request.url,
            title=request.title,
            content=request.content,
            metadata=request.metadata
        )
        
        if success:
            return {
                "success": True,
                "message": f"Content {request.content_id} indexed successfully",
                "content_id": request.content_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to index content")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@router.post("/index/batch", summary="Batch index multiple contents")
async def index_batch(
    request: BatchIndexRequest,
    service: SemanticSearchService = Depends(get_search_service)
) -> Dict[str, Any]:
    """
    Index multiple contents in a single batch operation.
    
    More efficient than indexing one at a time.
    """
    try:
        contents = [
            {
                'id': c.content_id,
                'url': c.url,
                'title': c.title,
                'content': c.content,
                'metadata': c.metadata or {}
            }
            for c in request.contents
        ]
        
        success_count, failed_count = await service.index_contents_batch(contents)
        
        return {
            "success": True,
            "total": len(contents),
            "indexed": success_count,
            "failed": failed_count,
            "message": f"Indexed {success_count}/{len(contents)} contents successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch indexing failed: {str(e)}")


@router.post("/search", response_model=SearchResponse, summary="Semantic search")
async def search(
    request: SearchRequest,
    service: SemanticSearchService = Depends(get_search_service)
) -> SearchResponse:
    """
    Perform semantic search across indexed content.
    
    Supports multiple search strategies:
    - **semantic**: Pure vector similarity search
    - **keyword**: Traditional keyword matching with expansion
    - **hybrid**: Combines semantic and keyword (recommended)
    
    Results are ranked by relevance using multiple signals including:
    - Vector similarity
    - Keyword matching
    - Content quality
    - Freshness
    """
    try:
        results, metrics = await service.search(
            query=request.query,
            top_k=request.top_k,
            filters=request.filters,
            min_score=request.min_score,
            search_strategy=request.search_strategy
        )
        
        # Convert to response format
        result_responses = [
            SearchResultResponse(
                content_id=r.content_id,
                url=r.url,
                title=r.title,
                content_preview=r.content_preview,
                similarity_score=r.similarity_score,
                relevance_score=r.relevance_score,
                keyword_score=r.keyword_score,
                final_score=r.final_score,
                rank=r.rank,
                matched_terms=r.matched_terms,
                metadata=r.metadata,
                explanation=r.explanation
            )
            for r in results
        ]
        
        return SearchResponse(
            results=result_responses,
            metrics={
                'search_time_ms': metrics.search_time_ms,
                'vectorization_time_ms': metrics.vectorization_time_ms,
                'ranking_time_ms': metrics.ranking_time_ms,
                'expansion_terms': metrics.expansion_terms,
                'filters_applied': metrics.filters_applied
            },
            query=request.query,
            total_results=len(results),
            search_time_ms=metrics.search_time_ms
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/expand", response_model=QueryExpansionResponse, summary="Expand search query")
async def expand_query(
    query: str = Query(..., description="Query to expand", min_length=1)
) -> QueryExpansionResponse:
    """
    Expand a search query with synonyms, related concepts, and variations.
    
    Useful for understanding how the system will interpret and enhance queries.
    """
    try:
        expander = QueryExpander(use_synonyms=True, use_concepts=True)
        expanded = await expander.expand(query)
        
        return QueryExpansionResponse(
            original=expanded.original,
            expanded_terms=expanded.expanded_terms,
            synonyms=expanded.synonyms,
            related_concepts=expanded.related_concepts,
            weighted_terms=expanded.get_weighted_terms()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query expansion failed: {str(e)}")


@router.post("/similar", summary="Find similar documents")
async def find_similar(
    request: SimilarDocumentsRequest,
    service: SemanticSearchService = Depends(get_search_service)
) -> List[SearchResultResponse]:
    """
    Find documents similar to a given document.
    
    Uses vector similarity to find content that's semantically related.
    """
    try:
        similar = await service.get_similar_documents(
            content_id=request.content_id,
            top_k=request.top_k
        )
        
        return [
            SearchResultResponse(
                content_id=r.content_id,
                url=r.url,
                title=r.title,
                content_preview=r.content_preview,
                similarity_score=r.similarity_score,
                relevance_score=r.relevance_score,
                keyword_score=r.keyword_score,
                final_score=r.final_score,
                rank=r.rank,
                matched_terms=r.matched_terms,
                metadata=r.metadata,
                explanation=r.explanation
            )
            for r in similar
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similar search failed: {str(e)}")


@router.get("/stats", response_model=StatsResponse, summary="Get search system statistics")
async def get_stats(
    service: SemanticSearchService = Depends(get_search_service)
) -> StatsResponse:
    """
    Get statistics and configuration of the semantic search system.
    """
    try:
        stats = service.get_search_stats()
        
        return StatsResponse(
            total_indexed_documents=stats['total_indexed_documents'],
            vector_store_provider=stats['vector_store']['provider'],
            embedding_model=stats['vector_store']['model_name'],
            embedding_dimension=stats['vector_store']['dimension'],
            query_expansion_enabled=stats['query_expansion_enabled'],
            hybrid_search_enabled=stats['hybrid_search_enabled']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")


@router.post("/rebuild", summary="Rebuild search index")
async def rebuild_index(
    service: SemanticSearchService = Depends(get_search_service)
) -> Dict[str, Any]:
    """
    Rebuild the entire search index.
    
    Use this if the index becomes corrupted or needs to be regenerated.
    """
    try:
        await service.rebuild_index()
        
        return {
            "success": True,
            "message": "Search index rebuilt successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Index rebuild failed: {str(e)}")


@router.post("/save", summary="Save search index to disk")
async def save_index(
    service: SemanticSearchService = Depends(get_search_service)
) -> Dict[str, Any]:
    """
    Save the current search index to disk for persistence.
    """
    try:
        service.save_index()
        
        return {
            "success": True,
            "message": "Search index saved to disk"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Index save failed: {str(e)}")


@router.delete("/index/{content_id}", summary="Remove content from index")
async def delete_from_index(
    content_id: int,
    service: SemanticSearchService = Depends(get_search_service)
) -> Dict[str, Any]:
    """
    Remove a specific content from the search index.
    """
    try:
        doc_id = f"content_{content_id}"
        success = service.vector_store.delete_document(doc_id)
        
        if success:
            return {
                "success": True,
                "message": f"Content {content_id} removed from index"
            }
        else:
            raise HTTPException(status_code=404, detail=f"Content {content_id} not found in index")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

"""
Vector Store - Manages embeddings and vector operations for semantic search

This module provides a comprehensive vector embedding system with:
- Content vectorization using OpenAI or Sentence Transformers
- Similarity computation and scoring
- Relevance ranking mechanisms
- Query expansion techniques
- Efficient vector storage and retrieval
"""

from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
import logging
import numpy as np
from enum import Enum
import asyncio
import pickle
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class EmbeddingProvider(str, Enum):
    """Supported embedding providers"""
    OPENAI = "openai"
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    HUGGINGFACE = "huggingface"


@dataclass
class VectorDocument:
    """Document with vector embedding"""
    id: str
    content: str
    embedding: np.ndarray
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'id': self.id,
            'content': self.content,
            'embedding': self.embedding.tolist(),
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VectorDocument':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            content=data['content'],
            embedding=np.array(data['embedding']),
            metadata=data.get('metadata', {}),
            created_at=datetime.fromisoformat(data['created_at'])
        )


@dataclass
class SearchResult:
    """Search result with similarity score"""
    document: VectorDocument
    similarity_score: float
    relevance_score: float
    rank: int
    matched_keywords: List[str] = field(default_factory=list)
    explanation: Optional[str] = None


class VectorStore:
    """
    High-performance vector store for semantic search.
    
    Features:
    - Multiple embedding providers (OpenAI, Sentence Transformers)
    - Efficient similarity computation (cosine, dot product, euclidean)
    - Advanced relevance ranking
    - Query expansion
    - Persistent storage
    """
    
    def __init__(
        self,
        provider: EmbeddingProvider = EmbeddingProvider.SENTENCE_TRANSFORMERS,
        model_name: Optional[str] = None,
        storage_path: str = "data/vectors",
        dimension: Optional[int] = None
    ):
        """
        Initialize vector store.
        
        Args:
            provider: Embedding provider to use
            model_name: Specific model name (provider-dependent)
            storage_path: Path for persistent storage
            dimension: Expected embedding dimension
        """
        self.provider = provider
        self.model_name = model_name or self._get_default_model(provider)
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.dimension = dimension
        
        # In-memory vector index
        self.documents: Dict[str, VectorDocument] = {}
        self.embeddings_matrix: Optional[np.ndarray] = None
        self.document_ids: List[str] = []
        
        # Initialize embedding model
        self._init_embedding_model()
        
        # Load existing vectors if available
        self._load_vectors()
        
        logger.info(f"VectorStore initialized with provider={provider}, model={self.model_name}")
    
    def _get_default_model(self, provider: EmbeddingProvider) -> str:
        """Get default model for provider"""
        defaults = {
            EmbeddingProvider.OPENAI: "text-embedding-3-small",
            EmbeddingProvider.SENTENCE_TRANSFORMERS: "all-MiniLM-L6-v2",
            EmbeddingProvider.HUGGINGFACE: "sentence-transformers/all-mpnet-base-v2"
        }
        return defaults.get(provider, "all-MiniLM-L6-v2")
    
    def _init_embedding_model(self):
        """Initialize the embedding model based on provider"""
        try:
            if self.provider == EmbeddingProvider.OPENAI:
                from openai import OpenAI
                self.client = OpenAI()
                self.dimension = self.dimension or 1536  # Default for text-embedding-3-small
                logger.info(f"Initialized OpenAI embeddings with model {self.model_name}")
                
            elif self.provider == EmbeddingProvider.SENTENCE_TRANSFORMERS:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_name)
                self.dimension = self.dimension or self.model.get_sentence_embedding_dimension()
                logger.info(f"Initialized Sentence Transformers with model {self.model_name}")
                
            elif self.provider == EmbeddingProvider.HUGGINGFACE:
                from transformers import AutoTokenizer, AutoModel
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModel.from_pretrained(self.model_name)
                self.dimension = self.dimension or 768  # Common dimension
                logger.info(f"Initialized HuggingFace model {self.model_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise
    
    async def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as numpy array
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            if self.provider == EmbeddingProvider.OPENAI:
                response = await asyncio.to_thread(
                    self.client.embeddings.create,
                    input=text,
                    model=self.model_name
                )
                embedding = np.array(response.data[0].embedding)
                
            elif self.provider == EmbeddingProvider.SENTENCE_TRANSFORMERS:
                embedding = await asyncio.to_thread(
                    self.model.encode,
                    text,
                    convert_to_numpy=True
                )
                
            elif self.provider == EmbeddingProvider.HUGGINGFACE:
                import torch
                inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
                with torch.no_grad():
                    outputs = self.model(**inputs)
                embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        try:
            if self.provider == EmbeddingProvider.OPENAI:
                # OpenAI supports batch embeddings
                response = await asyncio.to_thread(
                    self.client.embeddings.create,
                    input=texts,
                    model=self.model_name
                )
                embeddings = [np.array(item.embedding) for item in response.data]
                
            elif self.provider == EmbeddingProvider.SENTENCE_TRANSFORMERS:
                embeddings = await asyncio.to_thread(
                    self.model.encode,
                    texts,
                    convert_to_numpy=True,
                    show_progress_bar=len(texts) > 100
                )
                embeddings = [emb for emb in embeddings]
                
            else:
                # Fallback to sequential processing
                embeddings = [await self.embed_text(text) for text in texts]
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise
    
    async def add_document(
        self,
        doc_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[np.ndarray] = None
    ) -> VectorDocument:
        """
        Add a document to the vector store.
        
        Args:
            doc_id: Unique document identifier
            content: Document content
            metadata: Optional metadata
            embedding: Pre-computed embedding (optional)
            
        Returns:
            Created VectorDocument
        """
        # Generate embedding if not provided
        if embedding is None:
            embedding = await self.embed_text(content)
        
        # Create document
        doc = VectorDocument(
            id=doc_id,
            content=content,
            embedding=embedding,
            metadata=metadata or {}
        )
        
        # Store document
        self.documents[doc_id] = doc
        
        # Rebuild index
        self._rebuild_index()
        
        logger.info(f"Added document {doc_id} to vector store")
        return doc
    
    async def add_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[VectorDocument]:
        """
        Add multiple documents in batch.
        
        Args:
            documents: List of dicts with 'id', 'content', 'metadata'
            
        Returns:
            List of created VectorDocuments
        """
        # Extract texts for batch embedding
        texts = [doc['content'] for doc in documents]
        embeddings = await self.embed_batch(texts)
        
        # Create vector documents
        vector_docs = []
        for doc_data, embedding in zip(documents, embeddings):
            doc = VectorDocument(
                id=doc_data['id'],
                content=doc_data['content'],
                embedding=embedding,
                metadata=doc_data.get('metadata', {})
            )
            self.documents[doc.id] = doc
            vector_docs.append(doc)
        
        # Rebuild index
        self._rebuild_index()
        
        logger.info(f"Added {len(vector_docs)} documents to vector store")
        return vector_docs
    
    def _rebuild_index(self):
        """Rebuild the embeddings matrix for efficient search"""
        if not self.documents:
            self.embeddings_matrix = None
            self.document_ids = []
            return
        
        self.document_ids = list(self.documents.keys())
        embeddings = [self.documents[doc_id].embedding for doc_id in self.document_ids]
        self.embeddings_matrix = np.vstack(embeddings)
        logger.debug(f"Rebuilt index with {len(self.document_ids)} documents")
    
    def compute_similarity(
        self,
        query_embedding: np.ndarray,
        method: str = "cosine"
    ) -> np.ndarray:
        """
        Compute similarity scores between query and all documents.
        
        Args:
            query_embedding: Query vector
            method: Similarity method ('cosine', 'dot_product', 'euclidean')
            
        Returns:
            Array of similarity scores
        """
        if self.embeddings_matrix is None or len(self.embeddings_matrix) == 0:
            return np.array([])
        
        if method == "cosine":
            # Cosine similarity
            query_norm = query_embedding / np.linalg.norm(query_embedding)
            doc_norms = self.embeddings_matrix / np.linalg.norm(
                self.embeddings_matrix, axis=1, keepdims=True
            )
            similarities = np.dot(doc_norms, query_norm)
            
        elif method == "dot_product":
            # Dot product similarity
            similarities = np.dot(self.embeddings_matrix, query_embedding)
            
        elif method == "euclidean":
            # Euclidean distance (converted to similarity)
            distances = np.linalg.norm(
                self.embeddings_matrix - query_embedding, axis=1
            )
            similarities = 1 / (1 + distances)  # Convert distance to similarity
            
        else:
            raise ValueError(f"Unknown similarity method: {method}")
        
        return similarities
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        similarity_method: str = "cosine",
        min_score: float = 0.0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            similarity_method: Similarity computation method
            min_score: Minimum similarity score threshold
            filters: Optional metadata filters
            
        Returns:
            List of SearchResult objects ranked by relevance
        """
        if not self.documents:
            logger.warning("Vector store is empty")
            return []
        
        # Generate query embedding
        query_embedding = await self.embed_text(query)
        
        # Compute similarities
        similarities = self.compute_similarity(query_embedding, similarity_method)
        
        # Apply filters if provided
        valid_indices = self._apply_filters(filters) if filters else range(len(self.document_ids))
        
        # Create results with similarity scores
        results = []
        for idx in valid_indices:
            if idx >= len(similarities):
                continue
            
            score = float(similarities[idx])
            if score < min_score:
                continue
            
            doc_id = self.document_ids[idx]
            doc = self.documents[doc_id]
            
            results.append((doc, score, idx))
        
        # Sort by similarity score
        results.sort(key=lambda x: x[1], reverse=True)
        results = results[:top_k]
        
        # Apply relevance ranking
        ranked_results = await self._rank_results(query, results)
        
        return ranked_results
    
    def _apply_filters(self, filters: Dict[str, Any]) -> List[int]:
        """Apply metadata filters to get valid document indices"""
        valid_indices = []
        
        for idx, doc_id in enumerate(self.document_ids):
            doc = self.documents[doc_id]
            
            # Check each filter condition
            match = True
            for key, value in filters.items():
                if key not in doc.metadata:
                    match = False
                    break
                
                if isinstance(value, list):
                    if doc.metadata[key] not in value:
                        match = False
                        break
                else:
                    if doc.metadata[key] != value:
                        match = False
                        break
            
            if match:
                valid_indices.append(idx)
        
        return valid_indices
    
    async def _rank_results(
        self,
        query: str,
        results: List[Tuple[VectorDocument, float, int]]
    ) -> List[SearchResult]:
        """
        Apply advanced relevance ranking.
        
        Combines:
        - Similarity score (from embeddings)
        - Keyword matching
        - Document metadata
        - Freshness
        
        Args:
            query: Original query
            results: List of (document, similarity_score, index) tuples
            
        Returns:
            Ranked SearchResult objects
        """
        query_keywords = set(query.lower().split())
        ranked_results = []
        
        for rank, (doc, sim_score, idx) in enumerate(results, 1):
            # Keyword matching boost
            doc_words = set(doc.content.lower().split())
            matched_keywords = list(query_keywords & doc_words)
            keyword_score = len(matched_keywords) / max(len(query_keywords), 1)
            
            # Freshness boost (optional)
            freshness_score = self._compute_freshness_score(doc)
            
            # Metadata boost (optional)
            metadata_score = self._compute_metadata_score(doc, query)
            
            # Combined relevance score
            relevance_score = (
                0.6 * sim_score +
                0.2 * keyword_score +
                0.1 * freshness_score +
                0.1 * metadata_score
            )
            
            search_result = SearchResult(
                document=doc,
                similarity_score=sim_score,
                relevance_score=relevance_score,
                rank=rank,
                matched_keywords=matched_keywords,
                explanation=f"Similarity: {sim_score:.3f}, Keywords: {len(matched_keywords)}"
            )
            ranked_results.append(search_result)
        
        # Re-sort by relevance score
        ranked_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Update ranks
        for rank, result in enumerate(ranked_results, 1):
            result.rank = rank
        
        return ranked_results
    
    def _compute_freshness_score(self, doc: VectorDocument) -> float:
        """Compute freshness score based on document age"""
        if 'created_at' in doc.metadata:
            try:
                created = datetime.fromisoformat(doc.metadata['created_at'])
                age_days = (datetime.now() - created).days
                # Exponential decay: score decreases over time
                return np.exp(-age_days / 365.0)  # Half-life of 1 year
            except:
                pass
        return 0.5  # Default neutral score
    
    def _compute_metadata_score(self, doc: VectorDocument, query: str) -> float:
        """Compute score based on metadata relevance"""
        score = 0.0
        
        # Check if title/tags match query keywords
        query_lower = query.lower()
        
        if 'title' in doc.metadata:
            title = doc.metadata['title'].lower()
            if any(word in title for word in query_lower.split()):
                score += 0.5
        
        if 'tags' in doc.metadata:
            tags = [tag.lower() for tag in doc.metadata.get('tags', [])]
            if any(word in tags for word in query_lower.split()):
                score += 0.3
        
        if 'category' in doc.metadata:
            category = doc.metadata['category'].lower()
            if any(word in category for word in query_lower.split()):
                score += 0.2
        
        return min(score, 1.0)
    
    def get_document(self, doc_id: str) -> Optional[VectorDocument]:
        """Get document by ID"""
        return self.documents.get(doc_id)
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document from store"""
        if doc_id in self.documents:
            del self.documents[doc_id]
            self._rebuild_index()
            logger.info(f"Deleted document {doc_id}")
            return True
        return False
    
    def clear(self):
        """Clear all documents from store"""
        self.documents.clear()
        self.embeddings_matrix = None
        self.document_ids = []
        logger.info("Cleared vector store")
    
    def save(self, filename: str = "vector_store.pkl"):
        """Save vector store to disk"""
        filepath = self.storage_path / filename
        
        data = {
            'documents': {doc_id: doc.to_dict() for doc_id, doc in self.documents.items()},
            'provider': self.provider.value,
            'model_name': self.model_name,
            'dimension': self.dimension
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        
        logger.info(f"Saved vector store to {filepath}")
    
    def _load_vectors(self):
        """Load vectors from disk if available"""
        filepath = self.storage_path / "vector_store.pkl"
        
        if not filepath.exists():
            logger.info("No existing vector store found")
            return
        
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            # Restore documents
            self.documents = {
                doc_id: VectorDocument.from_dict(doc_data)
                for doc_id, doc_data in data['documents'].items()
            }
            
            # Rebuild index
            self._rebuild_index()
            
            logger.info(f"Loaded {len(self.documents)} documents from disk")
            
        except Exception as e:
            logger.error(f"Failed to load vector store: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            'total_documents': len(self.documents),
            'provider': self.provider.value,
            'model_name': self.model_name,
            'dimension': self.dimension,
            'index_size': self.embeddings_matrix.shape if self.embeddings_matrix is not None else None
        }

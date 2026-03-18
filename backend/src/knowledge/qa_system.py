"""
Question-Answering System

Scope-limited Q&A system that answers questions only from stored knowledge base.
Uses RAG (Retrieval-Augmented Generation) approach.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

from ..storage.content_store import ContentStore
from ..ai.llm_service import LLMService
from .knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)


@dataclass
class QAResult:
    """Question-answering result"""
    question: str
    answer: str
    confidence: float  # 0.0 to 1.0
    sources: List[Dict[str, Any]]  # Source content used
    in_scope: bool  # Whether answer is from knowledge base
    processing_time_ms: float
    token_count: int = 0


class QASystem:
    """
    Intelligent Q&A system with scope limitation.
    
    Features:
    - Scope-limited responses (only from stored content)
    - Context retrieval from knowledge base
    - Citation and source tracking
    - Confidence scoring
    - "I don't know" for out-of-scope questions
    """
    
    def __init__(self, llm_service: LLMService):
        """
        Initialize Q&A system.
        
        Args:
            llm_service: LLM service for generation
        """
        self.llm = llm_service
        self.kb = KnowledgeBase()
        self.store = ContentStore()
    
    async def ask(
        self,
        question: str,
        top_k: int = 3,
        min_confidence: float = 0.5
    ) -> QAResult:
        """
        Answer a question using knowledge base.
        
        Args:
            question: User's question
            top_k: Number of relevant documents to retrieve
            min_confidence: Minimum confidence threshold
            
        Returns:
            QAResult with answer and sources
        """
        start_time = datetime.now()
        
        # Step 1: Retrieve relevant context from knowledge base
        relevant_content = await self._retrieve_context(question, top_k)
        
        if not relevant_content:
            # No relevant content found
            return QAResult(
                question=question,
                answer="I don't have any information in my knowledge base to answer this question. Please try asking about content that has been analyzed.",
                confidence=0.0,
                sources=[],
                in_scope=False,
                processing_time_ms=self._get_elapsed_ms(start_time)
            )
        
        # Step 2: Check if question is answerable from context
        is_answerable, confidence = await self._check_answerability(
            question,
            relevant_content
        )
        
        if not is_answerable or confidence < min_confidence:
            return QAResult(
                question=question,
                answer=f"I found some related content, but I'm not confident I can accurately answer this question from my knowledge base. Try rephrasing or asking about: {self._suggest_topics(relevant_content)}",
                confidence=confidence,
                sources=relevant_content,
                in_scope=False,
                processing_time_ms=self._get_elapsed_ms(start_time)
            )
        
        # Step 3: Generate answer from context
        answer = await self._generate_answer(question, relevant_content)
        
        # Step 4: Add citations
        answer_with_citations = self._add_citations(answer, relevant_content)
        
        return QAResult(
            question=question,
            answer=answer_with_citations,
            confidence=confidence,
            sources=relevant_content,
            in_scope=True,
            processing_time_ms=self._get_elapsed_ms(start_time)
        )
    
    async def _retrieve_context(
        self,
        question: str,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from knowledge base.
        
        Args:
            question: User's question
            top_k: Number of results to retrieve
            
        Returns:
            List of relevant content chunks
        """
        # Extract keywords from question
        keywords = await self._extract_keywords(question)
        
        # Search knowledge base
        search_query = ' '.join(keywords)
        results = self.kb.search(search_query, limit=top_k * 2)
        
        # Score and rank results
        scored_results = []
        for result in results:
            score = self._calculate_relevance_score(
                question,
                result,
                keywords
            )
            result['relevance_score'] = score
            scored_results.append(result)
        
        # Sort by relevance and take top K
        scored_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored_results[:top_k]
    
    async def _extract_keywords(self, question: str) -> List[str]:
        """Extract keywords from question using LLM"""
        prompt = f"""Extract the 3-5 most important keywords from this question for searching.
Return only the keywords, comma-separated.

Question: {question}

Keywords:"""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are a keyword extraction expert.",
            temperature=0.3,
            max_tokens=50
        )
        
        keywords = [k.strip() for k in response.content.split(',')]
        return keywords[:5]
    
    def _calculate_relevance_score(
        self,
        question: str,
        content: Dict[str, Any],
        keywords: List[str]
    ) -> float:
        """
        Calculate relevance score for content.
        
        Simple scoring based on keyword matches and recency.
        """
        score = 0.0
        question_lower = question.lower()
        content_text = f"{content.get('title', '')} {content.get('content', '')}".lower()
        
        # Keyword matches (0-50 points)
        for keyword in keywords:
            if keyword.lower() in content_text:
                score += 10.0
        score = min(score, 50.0)
        
        # Title match (0-30 points)
        title = content.get('title', '').lower()
        title_words = set(title.split())
        question_words = set(question_lower.split())
        title_overlap = len(title_words & question_words)
        score += min(title_overlap * 10, 30.0)
        
        # Recency bonus (0-20 points)
        # More recent content gets higher score
        scraped_at = content.get('scraped_at', '')
        if scraped_at:
            # Simplified: assume recent content is better
            score += 10.0
        
        return min(score, 100.0)
    
    async def _check_answerability(
        self,
        question: str,
        content: List[Dict[str, Any]]
    ) -> Tuple[bool, float]:
        """
        Check if question can be answered from content.
        
        Returns:
            (is_answerable, confidence_score)
        """
        # Create context summary
        context_summary = "\n\n".join([
            f"Document {i+1}: {c.get('title', 'Untitled')}\n{c.get('content', '')[:500]}..."
            for i, c in enumerate(content)
        ])
        
        prompt = f"""Can this question be answered from the provided documents? 
Respond with only: YES <confidence> or NO <confidence>
Where confidence is 0.0 to 1.0

Question: {question}

Documents:
{context_summary}

Answer (YES/NO + confidence):"""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are an expert at determining if questions can be answered from given context.",
            temperature=0.2,
            max_tokens=20
        )
        
        # Parse response
        answer_text = response.content.strip().upper()
        
        if 'YES' in answer_text:
            # Extract confidence
            parts = answer_text.split()
            try:
                confidence = float(parts[1]) if len(parts) > 1 else 0.7
            except:
                confidence = 0.7
            return True, confidence
        else:
            return False, 0.3
    
    async def _generate_answer(
        self,
        question: str,
        content: List[Dict[str, Any]]
    ) -> str:
        """
        Generate answer from retrieved context.
        
        Args:
            question: User's question
            content: Retrieved relevant content
            
        Returns:
            Generated answer
        """
        # Create context window
        context = "\n\n".join([
            f"Source {i+1} - {c.get('title', 'Untitled')}:\n{c.get('content', '')[:1000]}"
            for i, c in enumerate(content)
        ])
        
        prompt = f"""Answer the question based ONLY on the provided sources. 
Do not use any external knowledge. Be specific and cite information from the sources.
If the sources don't contain enough information, say so.

Question: {question}

Sources:
{context}

Answer:"""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are a helpful assistant that answers questions strictly based on provided sources.",
            temperature=0.3,
            max_tokens=300
        )
        
        return response.content.strip()
    
    def _add_citations(
        self,
        answer: str,
        sources: List[Dict[str, Any]]
    ) -> str:
        """Add source citations to answer"""
        citations = "\n\n**Sources:**\n"
        for i, source in enumerate(sources, 1):
            title = source.get('title', 'Untitled')
            url = source.get('url', '#')
            scraped_at = source.get('scraped_at', '')[:10]
            citations += f"{i}. [{title}]({url}) (scraped: {scraped_at})\n"
        
        return answer + citations
    
    def _suggest_topics(self, content: List[Dict[str, Any]]) -> str:
        """Suggest topics from retrieved content"""
        titles = [c.get('title', 'Untitled') for c in content[:3]]
        return ', '.join(titles)
    
    def _get_elapsed_ms(self, start_time: datetime) -> float:
        """Calculate elapsed time in milliseconds"""
        elapsed = datetime.now() - start_time
        return elapsed.total_seconds() * 1000
    
    async def suggest_questions(
        self,
        content_id: Optional[int] = None,
        count: int = 5
    ) -> List[str]:
        """
        Suggest questions that can be asked.
        
        Args:
            content_id: Specific content to generate questions for (optional)
            count: Number of questions to suggest
            
        Returns:
            List of suggested questions
        """
        if content_id:
            # Get specific content
            content = self.store.get_content(content_id)
            context = f"Title: {content.get('title')}\nContent: {content.get('content', '')[:1000]}"
        else:
            # Get recent content
            recent = self.kb.get_recent_content(limit=5)
            context = "\n\n".join([
                f"{c.get('title')}: {c.get('content', '')[:200]}"
                for c in recent
            ])
        
        prompt = f"""Based on this content, suggest {count} interesting questions that can be answered.
Make questions specific and diverse.

Content:
{context}

Questions (one per line):"""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are an expert at generating insightful questions.",
            temperature=0.7,
            max_tokens=200
        )
        
        # Parse questions
        questions = [
            q.strip().lstrip('1234567890.-) ')
            for q in response.content.split('\n')
            if q.strip() and '?' in q
        ]
        
        return questions[:count]

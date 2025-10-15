"""
Content Summarization Analyzer

Provides multiple types of summarization:
- Extractive summarization (key sentences)
- Abstractive summarization (generated summaries)
- Key points extraction
- Multi-length summaries (short, medium, long)
- Executive summaries
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import re
from datetime import datetime

from .llm_service import LLMService, LLMResponse


class SummaryLength(str, Enum):
    """Summary length options"""
    SHORT = "short"  # 1-2 sentences
    MEDIUM = "medium"  # 3-5 sentences
    LONG = "long"  # 1-2 paragraphs
    EXECUTIVE = "executive"  # Structured executive summary


@dataclass
class KeyPoint:
    """Represents a key point from the content"""
    point: str
    importance: float  # 0.0 to 1.0
    category: Optional[str] = None
    supporting_quote: Optional[str] = None


@dataclass
class Summary:
    """Content summary with metadata"""
    text: str
    length: SummaryLength
    word_count: int
    key_points: List[KeyPoint] = field(default_factory=list)
    extractive_sentences: List[str] = field(default_factory=list)
    reading_time_seconds: int = 0
    confidence: float = 0.0
    generated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SummarizationResult:
    """Complete summarization analysis result"""
    short_summary: Summary
    medium_summary: Optional[Summary] = None
    long_summary: Optional[Summary] = None
    executive_summary: Optional[Summary] = None
    key_points: List[KeyPoint] = field(default_factory=list)
    main_takeaway: Optional[str] = None
    target_audience: Optional[str] = None
    content_type: Optional[str] = None
    processing_time_ms: float = 0.0
    llm_cost: float = 0.0


class ContentSummarizer:
    """
    AI-powered content summarization service.
    
    Features:
    - Multiple summary lengths
    - Key points extraction
    - Extractive and abstractive summarization
    - Audience-aware summaries
    """
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
    
    async def summarize(
        self,
        content: str,
        title: Optional[str] = None,
        lengths: Optional[List[SummaryLength]] = None,
        extract_key_points: bool = True,
        target_audience: Optional[str] = None
    ) -> SummarizationResult:
        """
        Generate comprehensive summarization analysis.
        
        Args:
            content: Text content to summarize
            title: Optional content title
            lengths: Summary lengths to generate (default: all)
            extract_key_points: Whether to extract key points
            target_audience: Target audience for summaries
            
        Returns:
            SummarizationResult with all requested summaries
        """
        start_time = datetime.now()
        
        # Default to all lengths
        if lengths is None:
            lengths = [SummaryLength.SHORT, SummaryLength.MEDIUM, SummaryLength.LONG]
        
        # Extract key points first (helps with other summaries)
        key_points = []
        if extract_key_points:
            key_points = await self._extract_key_points(content, title)
        
        # Generate summaries
        summaries = {}
        for length in lengths:
            summary = await self._generate_summary(
                content=content,
                title=title,
                length=length,
                key_points=key_points,
                target_audience=target_audience
            )
            summaries[length] = summary
        
        # Generate executive summary if requested
        executive_summary = None
        if SummaryLength.EXECUTIVE in lengths:
            executive_summary = await self._generate_executive_summary(
                content=content,
                title=title,
                key_points=key_points
            )
        
        # Extract main takeaway
        main_takeaway = await self._extract_main_takeaway(content, title)
        
        # Identify target audience if not provided
        if target_audience is None:
            target_audience = await self._identify_audience(content)
        
        # Identify content type
        content_type = await self._identify_content_type(content, title)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds() * 1000
        
        return SummarizationResult(
            short_summary=summaries.get(SummaryLength.SHORT),
            medium_summary=summaries.get(SummaryLength.MEDIUM),
            long_summary=summaries.get(SummaryLength.LONG),
            executive_summary=executive_summary,
            key_points=key_points,
            main_takeaway=main_takeaway,
            target_audience=target_audience,
            content_type=content_type,
            processing_time_ms=processing_time,
            llm_cost=self.llm.get_total_cost()
        )
    
    async def _generate_summary(
        self,
        content: str,
        title: Optional[str],
        length: SummaryLength,
        key_points: List[KeyPoint],
        target_audience: Optional[str]
    ) -> Summary:
        """Generate a single summary of specified length"""
        
        # Prepare prompt based on length
        length_instructions = {
            SummaryLength.SHORT: "1-2 concise sentences that capture the essence",
            SummaryLength.MEDIUM: "3-5 sentences providing a balanced overview",
            SummaryLength.LONG: "1-2 detailed paragraphs with comprehensive coverage"
        }
        
        system_prompt = """You are an expert content summarizer. Create clear, accurate summaries 
that capture the key information while being engaging and easy to understand."""
        
        prompt = f"""Summarize the following content in {length_instructions[length]}.

{f'Title: {title}' if title else ''}

Content:
{content[:4000]}  # Limit content length

Requirements:
- Focus on the most important information
- Be concise and clear
- Maintain factual accuracy
- Use active voice
{f'- Target audience: {target_audience}' if target_audience else ''}

Provide only the summary, no additional commentary."""
        
        response = await self.llm.complete(prompt, system_prompt=system_prompt)
        
        summary_text = response.content.strip()
        word_count = len(summary_text.split())
        reading_time = int(word_count / 200 * 60)  # 200 words per minute
        
        return Summary(
            text=summary_text,
            length=length,
            word_count=word_count,
            key_points=key_points,
            reading_time_seconds=reading_time,
            confidence=0.9,  # High confidence for LLM-generated summaries
            metadata={
                'model': response.model,
                'tokens': response.usage.get('total_tokens', 0)
            }
        )
    
    async def _extract_key_points(
        self,
        content: str,
        title: Optional[str]
    ) -> List[KeyPoint]:
        """Extract key points from content"""
        
        system_prompt = """You are an expert at identifying key points in content. 
Extract the most important points that readers should know."""
        
        prompt = f"""Extract the 5-7 most important key points from this content.

{f'Title: {title}' if title else ''}

Content:
{content[:4000]}

For each key point:
1. State it clearly in one sentence
2. Rate its importance (0.0 to 1.0)
3. Categorize it (e.g., main_idea, supporting_fact, conclusion, recommendation)
4. Include a brief supporting quote if relevant

Format as JSON array:
[
  {{
    "point": "Key point statement",
    "importance": 0.95,
    "category": "main_idea",
    "supporting_quote": "Relevant quote from content"
  }}
]

Provide only the JSON array, no additional text."""
        
        response = await self.llm.complete(prompt, system_prompt=system_prompt)
        
        # Parse JSON response
        try:
            import json
            # Extract JSON from response (handle markdown code blocks)
            content = response.content.strip()
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            
            points_data = json.loads(content)
            
            key_points = [
                KeyPoint(
                    point=p['point'],
                    importance=p.get('importance', 0.5),
                    category=p.get('category'),
                    supporting_quote=p.get('supporting_quote')
                )
                for p in points_data[:7]  # Limit to 7 points
            ]
            
            return key_points
            
        except Exception as e:
            print(f"Error parsing key points: {e}")
            # Fallback: extract from plain text
            return self._extract_key_points_fallback(response.content)
    
    def _extract_key_points_fallback(self, text: str) -> List[KeyPoint]:
        """Fallback method to extract key points from plain text"""
        # Split by lines and find bullet points or numbered items
        lines = text.strip().split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            # Match bullet points or numbered items
            if re.match(r'^[-*•]\s+', line) or re.match(r'^\d+\.\s+', line):
                # Clean the line
                point = re.sub(r'^[-*•\d.]\s+', '', line)
                if point and len(point) > 10:
                    key_points.append(KeyPoint(
                        point=point,
                        importance=0.7,
                        category="general"
                    ))
        
        return key_points[:7]
    
    async def _generate_executive_summary(
        self,
        content: str,
        title: Optional[str],
        key_points: List[KeyPoint]
    ) -> Summary:
        """Generate structured executive summary"""
        
        system_prompt = """You are an executive summary specialist. Create structured, 
actionable summaries for business and technical audiences."""
        
        prompt = f"""Create an executive summary with the following structure:

{f'Title: {title}' if title else ''}

Content:
{content[:4000]}

Structure:
1. Overview (2-3 sentences)
2. Key Findings (3-5 bullet points)
3. Implications (2-3 sentences)
4. Recommendations (2-4 bullet points)

Keep it professional, concise, and actionable."""
        
        response = await self.llm.complete(prompt, system_prompt=system_prompt)
        
        summary_text = response.content.strip()
        word_count = len(summary_text.split())
        
        return Summary(
            text=summary_text,
            length=SummaryLength.EXECUTIVE,
            word_count=word_count,
            key_points=key_points,
            reading_time_seconds=int(word_count / 200 * 60),
            confidence=0.9,
            metadata={
                'structure': 'executive',
                'model': response.model
            }
        )
    
    async def _extract_main_takeaway(
        self,
        content: str,
        title: Optional[str]
    ) -> str:
        """Extract the single most important takeaway"""
        
        prompt = f"""What is the single most important takeaway from this content? 
Answer in one clear, compelling sentence.

{f'Title: {title}' if title else ''}

Content:
{content[:3000]}

Provide only the takeaway sentence, nothing else."""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are an expert at distilling content to its essence."
        )
        
        return response.content.strip()
    
    async def _identify_audience(self, content: str) -> str:
        """Identify target audience"""
        
        prompt = f"""Who is the target audience for this content? 
Answer in 2-4 words (e.g., "software developers", "business executives", "general public").

Content:
{content[:2000]}

Provide only the audience description, nothing else."""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are an audience analysis expert."
        )
        
        return response.content.strip()
    
    async def _identify_content_type(
        self,
        content: str,
        title: Optional[str]
    ) -> str:
        """Identify content type"""
        
        prompt = f"""What type of content is this? Choose one: blog post, news article, 
technical documentation, academic paper, product description, tutorial, opinion piece, 
research report, case study, or other.

{f'Title: {title}' if title else ''}

Content:
{content[:1500]}

Provide only the content type (2-3 words), nothing else."""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are a content classification expert.",
            temperature=0.3  # Lower temperature for classification
        )
        
        return response.content.strip().lower()
    
    async def generate_tldr(self, content: str, max_words: int = 50) -> str:
        """
        Generate TL;DR (Too Long; Didn't Read) summary.
        
        Args:
            content: Content to summarize
            max_words: Maximum words in TL;DR
            
        Returns:
            TL;DR summary string
        """
        prompt = f"""Create a TL;DR summary in {max_words} words or less.

Content:
{content[:3000]}

TL;DR:"""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="Create ultra-concise TL;DR summaries.",
            max_tokens=max_words * 2
        )
        
        return response.content.strip()
    
    async def summarize_for_audience(
        self,
        content: str,
        audience: str,
        length: SummaryLength = SummaryLength.MEDIUM
    ) -> str:
        """
        Generate audience-specific summary.
        
        Args:
            content: Content to summarize
            audience: Target audience (e.g., "executives", "technical team")
            length: Summary length
            
        Returns:
            Audience-specific summary
        """
        length_map = {
            SummaryLength.SHORT: "2-3 sentences",
            SummaryLength.MEDIUM: "4-6 sentences",
            SummaryLength.LONG: "2-3 paragraphs"
        }
        
        prompt = f"""Summarize this content for {audience} in {length_map[length]}.

Use language and terminology appropriate for {audience}.
Focus on what matters most to them.

Content:
{content[:4000]}

Summary:"""
        
        response = await self.llm.complete(
            prompt,
            system_prompt=f"You are writing for {audience}. Adapt your language and focus accordingly."
        )
        
        return response.content.strip()

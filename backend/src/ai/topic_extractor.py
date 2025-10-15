"""
Topic and Theme Extraction

Advanced topic modeling and theme identification:
- Main topics and subtopics
- Named entity recognition (people, places, organizations)
- Keywords and key phrases
- Theme clustering
- Topic relevance scoring
- Semantic relationships
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from collections import Counter

from .llm_service import LLMService


class EntityType(str, Enum):
    """Named entity types"""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    PRODUCT = "product"
    TECHNOLOGY = "technology"
    CONCEPT = "concept"
    EVENT = "event"


@dataclass
class Topic:
    """Represents a topic with metadata"""
    name: str
    description: str
    relevance_score: float  # 0.0 to 1.0
    category: Optional[str] = None
    subtopics: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    mentions_count: int = 0


@dataclass
class NamedEntity:
    """Named entity with type and context"""
    text: str
    entity_type: EntityType
    confidence: float  # 0.0 to 1.0
    mentions: int = 1
    context: List[str] = field(default_factory=list)
    related_entities: List[str] = field(default_factory=list)


@dataclass
class KeyPhrase:
    """Key phrase with metadata"""
    phrase: str
    score: float  # 0.0 to 1.0
    frequency: int = 1
    positions: List[int] = field(default_factory=list)
    semantic_type: Optional[str] = None


@dataclass
class Theme:
    """Broad theme or subject area"""
    name: str
    description: str
    topics: List[Topic] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class TopicExtractionResult:
    """Complete topic extraction results"""
    main_topics: List[Topic] = field(default_factory=list)
    themes: List[Theme] = field(default_factory=list)
    named_entities: List[NamedEntity] = field(default_factory=list)
    keywords: List[KeyPhrase] = field(default_factory=list)
    key_phrases: List[KeyPhrase] = field(default_factory=list)
    semantic_clusters: Dict[str, List[str]] = field(default_factory=dict)
    content_category: Optional[str] = None
    domain: Optional[str] = None
    processing_time_ms: float = 0.0
    llm_cost: float = 0.0


class TopicExtractor:
    """
    AI-powered topic and theme extraction service.
    
    Features:
    - Hierarchical topic extraction
    - Named entity recognition
    - Keyword and key phrase extraction
    - Theme identification
    - Semantic clustering
    """
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
    
    async def extract(
        self,
        content: str,
        title: Optional[str] = None,
        extract_entities: bool = True,
        extract_themes: bool = True,
        max_topics: int = 10,
        max_keywords: int = 20
    ) -> TopicExtractionResult:
        """
        Extract topics, themes, and entities from content.
        
        Args:
            content: Text content to analyze
            title: Optional content title
            extract_entities: Whether to extract named entities
            extract_themes: Whether to identify themes
            max_topics: Maximum number of topics to extract
            max_keywords: Maximum number of keywords to extract
            
        Returns:
            TopicExtractionResult with extracted information
        """
        start_time = datetime.now()
        
        # Extract main topics
        main_topics = await self._extract_topics(content, title, max_topics)
        
        # Extract keywords and key phrases
        keywords, key_phrases = await self._extract_keywords_and_phrases(
            content, max_keywords
        )
        
        # Extract named entities
        named_entities = []
        if extract_entities:
            named_entities = await self._extract_named_entities(content)
        
        # Identify themes
        themes = []
        if extract_themes:
            themes = await self._identify_themes(content, main_topics)
        
        # Create semantic clusters
        semantic_clusters = await self._create_semantic_clusters(
            main_topics, keywords
        )
        
        # Identify content category and domain
        content_category = await self._identify_category(content, title)
        domain = await self._identify_domain(content, main_topics)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds() * 1000
        
        return TopicExtractionResult(
            main_topics=main_topics,
            themes=themes,
            named_entities=named_entities,
            keywords=keywords,
            key_phrases=key_phrases,
            semantic_clusters=semantic_clusters,
            content_category=content_category,
            domain=domain,
            processing_time_ms=processing_time,
            llm_cost=self.llm.get_total_cost()
        )
    
    async def _extract_topics(
        self,
        content: str,
        title: Optional[str],
        max_topics: int
    ) -> List[Topic]:
        """Extract main topics from content"""
        
        system_prompt = """You are a topic extraction expert. Identify the main topics 
discussed in content with hierarchical relationships."""
        
        prompt = f"""Extract the main topics from this content. Identify up to {max_topics} topics.

{f'Title: {title}' if title else ''}

Content:
{content[:5000]}

For each topic, provide:
1. Name (2-4 words)
2. Description (1 sentence)
3. Relevance score (0.0 to 1.0 - how central is this topic?)
4. Category (e.g., technology, business, science, etc.)
5. Subtopics (list of 2-4 related subtopics)
6. Keywords (3-5 key terms)

Format as JSON array:
[
  {{
    "name": "Machine Learning",
    "description": "Application of AI algorithms for data analysis",
    "relevance_score": 0.95,
    "category": "technology",
    "subtopics": ["neural networks", "supervised learning", "model training"],
    "keywords": ["algorithm", "training", "prediction", "model"]
  }}
]

Sort by relevance_score (highest first). Provide only valid JSON."""
        
        response = await self.llm.complete(
            prompt,
            system_prompt=system_prompt,
            temperature=0.3
        )
        
        # Parse JSON response
        try:
            import json
            content_str = response.content.strip()
            if content_str.startswith('```'):
                content_str = content_str.split('```')[1]
                if content_str.startswith('json'):
                    content_str = content_str[4:]
            
            data = json.loads(content_str)
            
            topics = []
            for item in data[:max_topics]:
                topics.append(Topic(
                    name=item.get('name', 'Unknown Topic'),
                    description=item.get('description', ''),
                    relevance_score=float(item.get('relevance_score', 0.5)),
                    category=item.get('category'),
                    subtopics=item.get('subtopics', []),
                    keywords=item.get('keywords', [])
                ))
            
            return topics
            
        except Exception as e:
            print(f"Error parsing topics: {e}")
            return []
    
    async def _extract_keywords_and_phrases(
        self,
        content: str,
        max_keywords: int
    ) -> tuple[List[KeyPhrase], List[KeyPhrase]]:
        """Extract keywords and key phrases"""
        
        system_prompt = """You are a keyword extraction expert. Identify the most important 
keywords and phrases that capture the content's meaning."""
        
        prompt = f"""Extract keywords and key phrases from this content.

Content:
{content[:4000]}

Provide two lists:
1. Keywords: Single important words (nouns, verbs, adjectives)
2. Key Phrases: Important multi-word phrases (2-4 words)

For each, include:
- text: the keyword/phrase
- score: importance score (0.0 to 1.0)
- semantic_type: what it represents (concept, action, descriptor, entity, etc.)

Format as JSON:
{{
  "keywords": [
    {{"text": "innovation", "score": 0.9, "semantic_type": "concept"}}
  ],
  "key_phrases": [
    {{"text": "digital transformation", "score": 0.85, "semantic_type": "concept"}}
  ]
}}

Limit to top {max_keywords} of each. Provide only valid JSON."""
        
        response = await self.llm.complete(
            prompt,
            system_prompt=system_prompt,
            temperature=0.2
        )
        
        # Parse response
        try:
            import json
            content_str = response.content.strip()
            if content_str.startswith('```'):
                content_str = content_str.split('```')[1]
                if content_str.startswith('json'):
                    content_str = content_str[4:]
            
            data = json.loads(content_str)
            
            keywords = [
                KeyPhrase(
                    phrase=kw.get('text', ''),
                    score=float(kw.get('score', 0.5)),
                    semantic_type=kw.get('semantic_type')
                )
                for kw in data.get('keywords', [])[:max_keywords]
            ]
            
            key_phrases = [
                KeyPhrase(
                    phrase=kp.get('text', ''),
                    score=float(kp.get('score', 0.5)),
                    semantic_type=kp.get('semantic_type')
                )
                for kp in data.get('key_phrases', [])[:max_keywords]
            ]
            
            return keywords, key_phrases
            
        except Exception as e:
            print(f"Error parsing keywords: {e}")
            return [], []
    
    async def _extract_named_entities(self, content: str) -> List[NamedEntity]:
        """Extract named entities"""
        
        system_prompt = """You are a named entity recognition expert. Identify people, 
organizations, locations, products, and other named entities."""
        
        prompt = f"""Extract named entities from this content.

Content:
{content[:4000]}

Identify entities of these types:
- person: People's names
- organization: Companies, institutions, groups
- location: Cities, countries, places
- product: Products, services, brands
- technology: Technologies, frameworks, tools
- event: Events, conferences, happenings
- concept: Important concepts or ideas

Format as JSON array:
[
  {{
    "text": "OpenAI",
    "entity_type": "organization",
    "confidence": 0.95,
    "context": "develops AI models"
  }}
]

Include only entities with confidence > 0.6. Provide only valid JSON."""
        
        response = await self.llm.complete(
            prompt,
            system_prompt=system_prompt,
            temperature=0.2
        )
        
        # Parse response
        try:
            import json
            content_str = response.content.strip()
            if content_str.startswith('```'):
                content_str = content_str.split('```')[1]
                if content_str.startswith('json'):
                    content_str = content_str[4:]
            
            data = json.loads(content_str)
            
            entity_type_map = {e.value: e for e in EntityType}
            entities = []
            
            for item in data:
                entity_type_str = item.get('entity_type', 'concept').lower()
                if entity_type_str in entity_type_map:
                    entities.append(NamedEntity(
                        text=item.get('text', ''),
                        entity_type=entity_type_map[entity_type_str],
                        confidence=float(item.get('confidence', 0.7)),
                        context=[item.get('context', '')]
                    ))
            
            return entities[:20]  # Limit to 20 entities
            
        except Exception as e:
            print(f"Error parsing entities: {e}")
            return []
    
    async def _identify_themes(
        self,
        content: str,
        topics: List[Topic]
    ) -> List[Theme]:
        """Identify broader themes"""
        
        # Create topic summary for context
        topic_summary = ", ".join([t.name for t in topics[:5]])
        
        system_prompt = """You are a theme identification expert. Identify the broader themes 
and subject areas that encompass multiple related topics."""
        
        prompt = f"""Identify 2-4 broad themes from this content.

Main topics found: {topic_summary}

Content:
{content[:3000]}

A theme is a broad subject area that encompasses multiple related topics.
For example, "Digital Innovation" might encompass topics like AI, cloud computing, and automation.

Format as JSON array:
[
  {{
    "name": "Digital Transformation",
    "description": "The integration of digital technology into business operations",
    "topics": ["AI", "automation", "cloud computing"],
    "keywords": ["digital", "innovation", "technology"],
    "confidence": 0.9
  }}
]

Provide 2-4 themes. Provide only valid JSON."""
        
        response = await self.llm.complete(
            prompt,
            system_prompt=system_prompt,
            temperature=0.4
        )
        
        # Parse response
        try:
            import json
            content_str = response.content.strip()
            if content_str.startswith('```'):
                content_str = content_str.split('```')[1]
                if content_str.startswith('json'):
                    content_str = content_str[4:]
            
            data = json.loads(content_str)
            
            themes = []
            for item in data[:4]:
                # Match topics to actual Topic objects
                theme_topic_names = item.get('topics', [])
                theme_topics = [
                    t for t in topics
                    if any(name.lower() in t.name.lower() for name in theme_topic_names)
                ]
                
                themes.append(Theme(
                    name=item.get('name', ''),
                    description=item.get('description', ''),
                    topics=theme_topics,
                    keywords=item.get('keywords', []),
                    confidence=float(item.get('confidence', 0.7))
                ))
            
            return themes
            
        except Exception as e:
            print(f"Error parsing themes: {e}")
            return []
    
    async def _create_semantic_clusters(
        self,
        topics: List[Topic],
        keywords: List[KeyPhrase]
    ) -> Dict[str, List[str]]:
        """Group related topics and keywords into semantic clusters"""
        
        if not topics:
            return {}
        
        # Create clusters based on topic categories
        clusters = {}
        
        for topic in topics:
            category = topic.category or "general"
            if category not in clusters:
                clusters[category] = []
            
            clusters[category].append(topic.name)
            clusters[category].extend(topic.subtopics[:2])  # Add top subtopics
        
        # Add high-scoring keywords to relevant clusters
        for keyword in keywords[:10]:
            # Find best matching cluster
            best_cluster = max(
                clusters.keys(),
                key=lambda c: sum(1 for item in clusters[c] if keyword.phrase.lower() in item.lower()),
                default=None
            )
            
            if best_cluster and keyword.phrase not in clusters[best_cluster]:
                clusters[best_cluster].append(keyword.phrase)
        
        # Limit cluster sizes
        for cluster in clusters:
            clusters[cluster] = list(set(clusters[cluster]))[:10]
        
        return clusters
    
    async def _identify_category(
        self,
        content: str,
        title: Optional[str]
    ) -> str:
        """Identify content category"""
        
        prompt = f"""Categorize this content into ONE of these categories:
Technology, Business, Science, Health, Education, Entertainment, Politics, 
Sports, Finance, Lifestyle, News, Opinion, Tutorial, Research

{f'Title: {title}' if title else ''}

Content:
{content[:2000]}

Provide only the category name (one word), nothing else."""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are a content categorization expert.",
            temperature=0.1,
            max_tokens=10
        )
        
        return response.content.strip()
    
    async def _identify_domain(
        self,
        content: str,
        topics: List[Topic]
    ) -> str:
        """Identify knowledge domain"""
        
        if not topics:
            return "general"
        
        # Use top topics to identify domain
        top_topics = ", ".join([t.name for t in topics[:3]])
        
        prompt = f"""Based on these main topics, identify the knowledge domain or field.

Main topics: {top_topics}

Examples: software engineering, healthcare, finance, marketing, education, 
data science, manufacturing, etc.

Provide only the domain name (2-3 words max), nothing else."""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are a domain classification expert.",
            temperature=0.1,
            max_tokens=15
        )
        
        return response.content.strip().lower()
    
    async def extract_quick_keywords(
        self,
        content: str,
        num_keywords: int = 10
    ) -> List[str]:
        """
        Quick keyword extraction (simple list).
        
        Args:
            content: Text content
            num_keywords: Number of keywords to extract
            
        Returns:
            List of keyword strings
        """
        prompt = f"""Extract the {num_keywords} most important keywords from this text.

Text: {content[:3000]}

Provide only a comma-separated list of keywords, nothing else."""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="Extract keywords accurately.",
            temperature=0.2,
            max_tokens=100
        )
        
        # Parse comma-separated list
        keywords = [kw.strip() for kw in response.content.split(',')]
        return keywords[:num_keywords]

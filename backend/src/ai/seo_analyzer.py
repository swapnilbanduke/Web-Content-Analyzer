"""
SEO Analysis Service

Comprehensive SEO analysis including:
- Keyword optimization
- Meta tags evaluation
- Content structure analysis
- Internal/external linking
- Readability for SEO
- Mobile-friendliness indicators
- SEO scoring and recommendations
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re

from .llm_service import LLMService


class SEOPriority(str, Enum):
    """SEO issue priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class KeywordAnalysis:
    """Keyword usage and optimization analysis"""
    keyword: str
    frequency: int
    density: float  # Percentage
    prominence: float  # 0.0 to 1.0 (position weight)
    in_title: bool = False
    in_headings: bool = False
    in_meta_description: bool = False
    in_url: bool = False
    optimal_density_range: Tuple[float, float] = (1.0, 3.0)
    is_optimal: bool = False


@dataclass
class MetaTagsAnalysis:
    """Meta tags evaluation"""
    title_length: int
    title_optimal: bool
    description_length: int
    description_optimal: bool
    has_keywords: bool
    keywords_in_title: List[str] = field(default_factory=list)
    keywords_in_description: List[str] = field(default_factory=list)
    missing_tags: List[str] = field(default_factory=list)
    og_tags_present: bool = False
    twitter_tags_present: bool = False


@dataclass
class ContentStructureScore:
    """Content structure for SEO"""
    has_h1: bool
    h1_count: int
    h2_count: int = 0
    h3_count: int = 0
    total_headings: int = 0
    paragraph_count: int = 0
    heading_hierarchy_correct: bool = True
    proper_hierarchy: bool = True
    paragraph_length_optimal: bool = False
    content_length: int = 0
    content_length_score: float = 0.0  # 0.0 to 1.0
    internal_links_count: int = 0
    external_links_count: int = 0
    image_count: int = 0
    images_have_alt: float = 0.0  # Percentage
    use_of_lists: bool = False
    use_of_bold_italic: bool = False


@dataclass
class SEOIssue:
    """SEO issue or recommendation"""
    category: str
    priority: SEOPriority
    issue: str
    recommendation: str
    impact: str  # Expected impact of fixing
    

@dataclass
class SEOScore:
    """Overall SEO scoring"""
    overall_score: float  # 0 to 100
    content_score: float
    technical_score: float
    keyword_score: float
    metadata_score: float
    structure_score: float
    link_score: float


@dataclass
class SEOAnalysisResult:
    """Complete SEO analysis results"""
    score: SEOScore
    primary_keywords: List[KeywordAnalysis] = field(default_factory=list)
    meta_tags: Optional[MetaTagsAnalysis] = None
    content_structure: Optional[ContentStructureScore] = None
    issues: List[SEOIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    target_keywords_suggested: List[str] = field(default_factory=list)
    search_intent: Optional[str] = None
    competitive_keywords: List[str] = field(default_factory=list)
    processing_time_ms: float = 0.0
    llm_cost: float = 0.0


class SEOAnalyzer:
    """
    AI-powered SEO analysis service.
    
    Features:
    - Comprehensive keyword analysis
    - Meta tags optimization
    - Content structure evaluation
    - Link analysis
    - SEO scoring with actionable recommendations
    """
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
    
    async def analyze(
        self,
        content: str,
        title: Optional[str] = None,
        meta_description: Optional[str] = None,
        url: Optional[str] = None,
        headings: Optional[List[str]] = None,
        target_keywords: Optional[List[str]] = None
    ) -> SEOAnalysisResult:
        """
        Perform comprehensive SEO analysis.
        
        Args:
            content: Main content text
            title: Page title
            meta_description: Meta description
            url: Page URL
            headings: List of headings (H1, H2, etc.)
            target_keywords: Target keywords to analyze
            
        Returns:
            SEOAnalysisResult with complete analysis
        """
        start_time = datetime.now()
        
        # Identify primary keywords (if not provided)
        if not target_keywords:
            target_keywords = await self._identify_target_keywords(content, title)
        
        # Analyze keywords
        primary_keywords = await self._analyze_keywords(
            content, title, meta_description, url, headings, target_keywords
        )
        
        # Analyze meta tags
        meta_tags = await self._analyze_meta_tags(
            title, meta_description, target_keywords
        )
        
        # Analyze content structure
        content_structure = await self._analyze_content_structure(
            content, headings or []
        )
        
        # Identify search intent
        search_intent = await self._identify_search_intent(content, title)
        
        # Get competitive keywords
        competitive_keywords = await self._get_competitive_keywords(
            content, target_keywords
        )
        
        # Calculate scores
        score = await self._calculate_seo_score(
            primary_keywords, meta_tags, content_structure
        )
        
        # Generate issues and recommendations
        issues = await self._identify_issues(
            primary_keywords, meta_tags, content_structure, score
        )
        
        recommendations = await self._generate_recommendations(
            content, issues, score
        )
        
        opportunities = await self._identify_opportunities(
            content, primary_keywords, competitive_keywords
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds() * 1000
        
        return SEOAnalysisResult(
            score=score,
            primary_keywords=primary_keywords,
            meta_tags=meta_tags,
            content_structure=content_structure,
            issues=issues,
            recommendations=recommendations,
            opportunities=opportunities,
            target_keywords_suggested=target_keywords,
            search_intent=search_intent,
            competitive_keywords=competitive_keywords,
            processing_time_ms=processing_time,
            llm_cost=self.llm.get_total_cost()
        )
    
    async def _identify_target_keywords(
        self,
        content: str,
        title: Optional[str]
    ) -> List[str]:
        """Identify target keywords using advanced LLM analysis"""
        
        prompt = f"""As an expert SEO keyword researcher, analyze this content and identify the 5-7 primary target keywords for SEO optimization.

{f'Title: {title}' if title else ''}

Content:
{content[:3000]}

Consider:
1. Main topics and themes (primary keywords)
2. Search terms users would actually use (search intent)
3. Commercial and informational intent keywords
4. Long-tail keyword variations (3-4 words)
5. Semantic relevance and topic authority
6. Search volume potential (common search phrases)

IMPORTANT: Focus on keywords that:
- Are actually present or implied in the content
- Have clear search intent
- Are specific enough to rank for
- Include both head terms and long-tail variations

Format: Return ONLY comma-separated keywords, nothing else.
Example: web design, responsive web design, mobile friendly websites, professional website development, custom web design services"""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are an expert SEO strategist specializing in keyword research and search intent analysis.",
            temperature=0.3,
            max_tokens=150
        )
        
        keywords = [kw.strip() for kw in response.content.split(',') if kw.strip()]
        return keywords[:7]
    
    async def _get_lsi_keywords(
        self,
        content: str,
        primary_keywords: List[str]
    ) -> List[str]:
        """Get LSI (Latent Semantic Indexing) keywords for better SEO"""
        
        prompt = f"""Identify 10 LSI (Latent Semantic Indexing) keywords and related terms for SEO optimization.

Primary Keywords: {', '.join(primary_keywords)}

Content Sample:
{content[:2000]}

LSI keywords are semantically related terms that:
- Support the main keywords
- Appear naturally in well-optimized content
- Help search engines understand context
- Include synonyms, related concepts, and supporting terms

Example for "coffee maker":
LSI: brewing, espresso machine, automatic coffee, drip coffee, coffee beans, barista, french press, coffee grinder, caffeine, morning coffee

Format: Return ONLY comma-separated LSI keywords."""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are an SEO expert specializing in semantic search and LSI keyword research.",
            temperature=0.4,
            max_tokens=200
        )
        
        lsi_keywords = [kw.strip() for kw in response.content.split(',') if kw.strip()]
        return lsi_keywords[:10]
    
    async def _analyze_keywords(
        self,
        content: str,
        title: Optional[str],
        meta_description: Optional[str],
        url: Optional[str],
        headings: List[str],
        target_keywords: List[str]
    ) -> List[KeywordAnalysis]:
        """Analyze keyword usage and optimization"""
        
        content_lower = content.lower()
        word_count = len(content.split())
        
        keyword_analyses = []
        
        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            
            # Count occurrences
            frequency = content_lower.count(keyword_lower)
            
            # Calculate density
            density = (frequency / word_count * 100) if word_count > 0 else 0
            
            # Check prominence (early in content = higher score)
            first_occurrence = content_lower.find(keyword_lower)
            prominence = 1.0 if first_occurrence < 200 else (
                0.7 if first_occurrence < 500 else 0.4
            )
            
            # Check presence in key locations
            in_title = keyword_lower in (title or "").lower() if title else False
            # Handle both Heading objects and strings
            if headings:
                heading_texts = [h.text if hasattr(h, 'text') else str(h) for h in headings]
                in_headings = any(keyword_lower in h.lower() for h in heading_texts)
            else:
                in_headings = False
            in_meta = keyword_lower in (meta_description or "").lower() if meta_description else False
            in_url = keyword_lower in (url or "").lower() if url else False
            
            # Check if density is optimal (1-3% is generally good)
            is_optimal = 1.0 <= density <= 3.0
            
            keyword_analyses.append(KeywordAnalysis(
                keyword=keyword,
                frequency=frequency,
                density=density,
                prominence=prominence,
                in_title=in_title,
                in_headings=in_headings,
                in_meta_description=in_meta,
                in_url=in_url,
                is_optimal=is_optimal
            ))
        
        return keyword_analyses
    
    async def _analyze_meta_tags(
        self,
        title: Optional[str],
        meta_description: Optional[str],
        target_keywords: List[str]
    ) -> MetaTagsAnalysis:
        """Analyze meta tags for SEO"""
        
        title_length = len(title) if title else 0
        desc_length = len(meta_description) if meta_description else 0
        
        # Optimal ranges
        title_optimal = 50 <= title_length <= 60
        desc_optimal = 150 <= desc_length <= 160
        
        # Check keyword presence
        keywords_in_title = []
        keywords_in_desc = []
        
        if title and target_keywords:
            title_lower = title.lower()
            keywords_in_title = [
                kw for kw in target_keywords if kw.lower() in title_lower
            ]
        
        if meta_description and target_keywords:
            desc_lower = meta_description.lower()
            keywords_in_desc = [
                kw for kw in target_keywords if kw.lower() in desc_lower
            ]
        
        has_keywords = len(keywords_in_title) > 0 or len(keywords_in_desc) > 0
        
        # Missing tags
        missing_tags = []
        if not title:
            missing_tags.append("title")
        if not meta_description:
            missing_tags.append("meta_description")
        
        return MetaTagsAnalysis(
            title_length=title_length,
            title_optimal=title_optimal,
            description_length=desc_length,
            description_optimal=desc_optimal,
            has_keywords=has_keywords,
            keywords_in_title=keywords_in_title,
            keywords_in_description=keywords_in_desc,
            missing_tags=missing_tags
        )
    
    async def _analyze_content_structure(
        self,
        content: str,
        headings: List
    ) -> ContentStructureScore:
        """Analyze content structure for SEO with enhanced metrics"""
        
        content_length = len(content)
        word_count = len(content.split())
        
        # Handle both Heading objects and strings
        if headings and hasattr(headings[0], 'level'):
            # Heading objects with .level attribute
            h1_count = sum(1 for h in headings if h.level == 1)
            h2_count = sum(1 for h in headings if h.level == 2)
            h3_count = sum(1 for h in headings if h.level == 3)
            total_headings = len(headings)
            
            # Check proper hierarchy (H1 before H2, H2 before H3, etc.)
            levels = [h.level for h in headings]
            proper_hierarchy = True
            if levels:
                for i in range(len(levels) - 1):
                    # Skip if difference is more than 1 level (e.g., H1 to H3)
                    if levels[i+1] - levels[i] > 1:
                        proper_hierarchy = False
                        break
        else:
            # String headings (legacy format like "h1: text")
            h1_count = sum(1 for h in headings if str(h).lower().startswith('h1:'))
            h2_count = sum(1 for h in headings if str(h).lower().startswith('h2:'))
            h3_count = sum(1 for h in headings if str(h).lower().startswith('h3:'))
            total_headings = len(headings)
            proper_hierarchy = True  # Can't check without knowing order
        
        has_h1 = h1_count >= 1
        
        # Content length score (300-2000 words is typically good)
        if word_count < 300:
            content_length_score = word_count / 300 * 0.5
        elif word_count <= 2000:
            content_length_score = 0.5 + (word_count - 300) / 1700 * 0.5
        else:
            content_length_score = 1.0
        
        # Check for lists
        use_of_lists = bool(re.search(r'[-*•]\s+\w+|^\d+\.\s+\w+', content, re.MULTILINE))
        
        # Check for formatting
        use_of_bold_italic = bool(re.search(r'\*\*\w+\*\*|\*\w+\*|__\w+__|_\w+_', content))
        
        # Estimate paragraph count and length
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)
        avg_para_words = sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        paragraph_length_optimal = 50 <= avg_para_words <= 150
        
        return ContentStructureScore(
            has_h1=has_h1,
            h1_count=h1_count,
            h2_count=h2_count,
            h3_count=h3_count,
            total_headings=total_headings,
            paragraph_count=paragraph_count,
            proper_hierarchy=proper_hierarchy,
            heading_hierarchy_correct=proper_hierarchy,
            paragraph_length_optimal=paragraph_length_optimal,
            content_length=content_length,
            content_length_score=content_length_score,
            internal_links_count=0,  # Would need full HTML
            external_links_count=0,  # Would need full HTML
            image_count=0,  # Would need full HTML
            images_have_alt=0.0,  # Would need full HTML
            use_of_lists=use_of_lists,
            use_of_bold_italic=use_of_bold_italic
        )
    
    async def _identify_search_intent(
        self,
        content: str,
        title: Optional[str]
    ) -> str:
        """Identify search intent (informational, transactional, navigational)"""
        
        prompt = f"""Identify the search intent for this content. Choose ONE:
- informational (user wants to learn)
- transactional (user wants to buy/do something)
- navigational (user wants to find a specific page)
- commercial (user is researching before buying)

{f'Title: {title}' if title else ''}

Content:
{content[:2000]}

Provide only the intent type (one word), nothing else."""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are a search intent analysis expert.",
            temperature=0.1,
            max_tokens=10
        )
        
        return response.content.strip().lower()
    
    async def _get_competitive_keywords(
        self,
        content: str,
        target_keywords: List[str]
    ) -> List[str]:
        """Identify competitive/related keywords"""
        
        prompt = f"""Suggest 5-7 related keywords that competitors might target for similar content.

Current target keywords: {', '.join(target_keywords)}

Content:
{content[:2000]}

Focus on:
- Related search terms
- Long-tail variations
- LSI (Latent Semantic Indexing) keywords
- Question-based keywords

Provide as comma-separated list."""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are an SEO keyword strategist.",
            temperature=0.4
        )
        
        keywords = [kw.strip() for kw in response.content.split(',')]
        return keywords[:7]
    
    async def _calculate_seo_score(
        self,
        keywords: List[KeywordAnalysis],
        meta_tags: MetaTagsAnalysis,
        structure: ContentStructureScore
    ) -> SEOScore:
        """Calculate overall SEO scores"""
        
        # Keyword score (0-100)
        keyword_score = 0.0
        if keywords:
            optimal_count = sum(1 for kw in keywords if kw.is_optimal)
            placement_score = sum(
                (kw.in_title * 0.3 + kw.in_headings * 0.3 + kw.in_meta_description * 0.2 + kw.in_url * 0.2)
                for kw in keywords
            ) / len(keywords) * 100
            
            keyword_score = (optimal_count / len(keywords) * 50) + (placement_score * 0.5)
        
        # Metadata score (0-100)
        metadata_score = 0.0
        if meta_tags:
            title_score = 100 if meta_tags.title_optimal else (meta_tags.title_length / 60 * 100 if meta_tags.title_length > 0 else 0)
            desc_score = 100 if meta_tags.description_optimal else (meta_tags.description_length / 160 * 100 if meta_tags.description_length > 0 else 0)
            keyword_score_meta = 100 if meta_tags.has_keywords else 0
            
            metadata_score = (title_score * 0.4 + desc_score * 0.4 + keyword_score_meta * 0.2)
        
        # Structure score (0-100)
        structure_score = 0.0
        if structure:
            h1_score = 100 if structure.has_h1 and structure.h1_count == 1 else 50
            length_score = structure.content_length_score * 100
            formatting_score = (structure.use_of_lists * 50) + (structure.use_of_bold_italic * 50)
            
            structure_score = (h1_score * 0.3 + length_score * 0.4 + formatting_score * 0.3)
        
        # Content score (average of keyword and structure)
        content_score = (keyword_score + structure_score) / 2
        
        # Technical score (metadata)
        technical_score = metadata_score
        
        # Link score (placeholder - would need actual link data)
        link_score = 50.0
        
        # Overall score (weighted average)
        overall_score = (
            content_score * 0.3 +
            technical_score * 0.25 +
            keyword_score * 0.25 +
            structure_score * 0.15 +
            link_score * 0.05
        )
        
        return SEOScore(
            overall_score=min(100.0, max(0.0, overall_score)),
            content_score=content_score,
            technical_score=technical_score,
            keyword_score=keyword_score,
            metadata_score=metadata_score,
            structure_score=structure_score,
            link_score=link_score
        )
    
    async def _identify_issues(
        self,
        keywords: List[KeywordAnalysis],
        meta_tags: MetaTagsAnalysis,
        structure: ContentStructureScore,
        score: SEOScore
    ) -> List[SEOIssue]:
        """Identify SEO issues"""
        
        issues = []
        
        # Keyword issues
        for kw in keywords:
            if not kw.is_optimal:
                priority = SEOPriority.HIGH if not kw.in_title else SEOPriority.MEDIUM
                issues.append(SEOIssue(
                    category="keywords",
                    priority=priority,
                    issue=f"Keyword '{kw.keyword}' density is {kw.density:.1f}% (optimal: 1-3%)",
                    recommendation=f"{'Increase' if kw.density < 1 else 'Decrease'} usage of '{kw.keyword}'",
                    impact="Improved keyword relevance and ranking potential"
                ))
            
            if not kw.in_title:
                issues.append(SEOIssue(
                    category="keywords",
                    priority=SEOPriority.HIGH,
                    issue=f"Target keyword '{kw.keyword}' not in title",
                    recommendation=f"Include '{kw.keyword}' in the page title",
                    impact="Better title relevance and click-through rate"
                ))
        
        # Meta tag issues
        if meta_tags.missing_tags:
            for tag in meta_tags.missing_tags:
                issues.append(SEOIssue(
                    category="metadata",
                    priority=SEOPriority.CRITICAL,
                    issue=f"Missing {tag} tag",
                    recommendation=f"Add {tag} tag with relevant keywords",
                    impact="Essential for search engine visibility"
                ))
        
        if not meta_tags.title_optimal and meta_tags.title_length > 0:
            issues.append(SEOIssue(
                category="metadata",
                priority=SEOPriority.HIGH,
                issue=f"Title length is {meta_tags.title_length} chars (optimal: 50-60)",
                recommendation="Adjust title length to 50-60 characters",
                impact="Better display in search results"
            ))
        
        # Structure issues
        if not structure.has_h1:
            issues.append(SEOIssue(
                category="structure",
                priority=SEOPriority.CRITICAL,
                issue="Missing H1 heading",
                recommendation="Add a clear H1 heading with primary keyword",
                impact="Critical for content structure and SEO"
            ))
        
        if structure.content_length_score < 0.5:
            issues.append(SEOIssue(
                category="content",
                priority=SEOPriority.MEDIUM,
                issue="Content too short for optimal SEO",
                recommendation="Expand content to at least 300-500 words",
                impact="Better depth and ranking potential"
            ))
        
        return sorted(issues, key=lambda x: {
            SEOPriority.CRITICAL: 0,
            SEOPriority.HIGH: 1,
            SEOPriority.MEDIUM: 2,
            SEOPriority.LOW: 3
        }[x.priority])
    
    async def _generate_recommendations(
        self,
        content: str,
        issues: List[SEOIssue],
        score: SEOScore
    ) -> List[str]:
        """Generate actionable SEO recommendations using AI"""
        
        recommendations = []
        
        # If there are critical/high priority issues, create specific recommendations
        critical_issues = [i for i in issues if i.priority in [SEOPriority.CRITICAL, SEOPriority.HIGH]]
        
        if critical_issues:
            for issue in critical_issues[:5]:  # Top 5 critical issues
                recommendations.append(f"🔴 {issue.recommendation} - {issue.impact}")
        
        # Use LLM for advanced recommendations based on score
        prompt = f"""As an SEO expert, provide 5 specific, actionable SEO recommendations for this content.

Current SEO Scores:
- Overall: {score.overall_score:.1f}%
- Content: {score.content_score:.1f}%
- Keywords: {score.keyword_score:.1f}%
- Technical: {score.technical_score:.1f}%
- Structure: {score.structure_score:.1f}%

Content Preview:
{content[:1500]}

Provide recommendations that:
1. Are specific and actionable (not generic advice)
2. Focus on quick wins and high-impact changes
3. Consider the current content context
4. Include keyword optimization, content structure, and technical SEO
5. Are prioritized by potential impact

Format: Return each recommendation on a new line, starting with a priority emoji (🔴 high, 🟡 medium, 🟢 nice-to-have)

Example:
🔴 Add target keyword "web design" to the first 100 words for better relevance
🟡 Include 2-3 more subheadings (H2) to break up long paragraphs
🟢 Add internal links to related pages to improve site structure"""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are an expert SEO consultant providing specific, actionable optimization recommendations.",
            temperature=0.5,
            max_tokens=400
        )
        
        # Parse LLM recommendations
        llm_recs = [r.strip() for r in response.content.split('\n') if r.strip() and any(emoji in r for emoji in ['🔴', '🟡', '🟢'])]
        recommendations.extend(llm_recs[:5])
        
        return recommendations[:10]  # Max 10 recommendations        # Convert top issues to recommendations
        for issue in issues[:5]:
            recommendations.append(issue.recommendation)
        
        # Add general recommendations based on score
        if score.overall_score < 60:
            recommendations.append("Focus on fundamental SEO improvements (meta tags, keywords, structure)")
        
        if score.keyword_score < 50:
            recommendations.append("Improve keyword optimization and placement")
        
        if score.structure_score < 50:
            recommendations.append("Enhance content structure with proper headings and formatting")
        
        return recommendations[:10]
    
    async def _identify_opportunities(
        self,
        content: str,
        keywords: List[KeywordAnalysis],
        competitive_keywords: List[str]
    ) -> List[str]:
        """Identify SEO opportunities"""
        
        opportunities = []
        
        # Low competition keywords
        opportunities.append("Consider targeting long-tail keyword variations for easier ranking")
        
        # Content expansion
        if len(content.split()) < 1000:
            opportunities.append("Expand content with related topics to target more keywords")
        
        # Featured snippets
        opportunities.append("Structure content with Q&A format for featured snippet opportunities")
        
        # Multimedia
        opportunities.append("Add images, videos, or infographics to improve engagement")
        
        # Internal linking
        opportunities.append("Create internal links to related content on your site")
        
        return opportunities[:7]

"""
Competitive Analysis Service

Analyzes content against competitors to identify:
- Content gaps and opportunities
- Unique positioning and differentiation
- Competitive advantages
- Market positioning insights
- Content depth comparison
- Tone and style differentiation
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from .llm_service import LLMService


class CompetitiveStrength(str, Enum):
    """Competitive positioning strength"""
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"


class ContentGapPriority(str, Enum):
    """Priority level for content gaps"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ContentGap:
    """Identified content gap"""
    topic: str
    description: str
    priority: ContentGapPriority
    potential_impact: str
    suggested_action: str
    keywords: List[str] = field(default_factory=list)


@dataclass
class UniqueValueProposition:
    """Unique value proposition element"""
    aspect: str
    description: str
    strength: CompetitiveStrength
    supporting_points: List[str] = field(default_factory=list)


@dataclass
class CompetitiveAdvantage:
    """Competitive advantage analysis"""
    category: str  # 'content_depth', 'expertise', 'clarity', etc.
    advantage: str
    strength: CompetitiveStrength
    evidence: List[str] = field(default_factory=list)
    how_to_leverage: str = ""


@dataclass
class MarketPosition:
    """Market positioning insights"""
    positioning_statement: str
    target_audience_alignment: str
    differentiation_factors: List[str] = field(default_factory=list)
    competitive_moat: str = ""
    market_segment: str = ""


@dataclass
class ContentDepthComparison:
    """Content depth vs competitors"""
    depth_score: float  # 0.0 to 10.0
    comprehensiveness: str  # 'shallow', 'moderate', 'comprehensive'
    topic_coverage: float  # Percentage
    detail_level: str  # 'surface', 'intermediate', 'expert'
    areas_of_strength: List[str] = field(default_factory=list)
    areas_needing_expansion: List[str] = field(default_factory=list)


@dataclass
class StyleDifferentiation:
    """Style and tone differentiation"""
    tone_uniqueness: float  # 0.0 to 1.0
    voice_distinctiveness: str
    style_advantages: List[str] = field(default_factory=list)
    style_weaknesses: List[str] = field(default_factory=list)
    recommended_adjustments: List[str] = field(default_factory=list)


@dataclass
class CompetitiveAnalysisResult:
    """Complete competitive analysis results"""
    content_gaps: List[ContentGap] = field(default_factory=list)
    unique_value_propositions: List[UniqueValueProposition] = field(default_factory=list)
    competitive_advantages: List[CompetitiveAdvantage] = field(default_factory=list)
    market_position: Optional[MarketPosition] = None
    content_depth: Optional[ContentDepthComparison] = None
    style_differentiation: Optional[StyleDifferentiation] = None
    overall_competitive_score: float = 0.0  # 0 to 100
    opportunities: List[str] = field(default_factory=list)
    threats: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    processing_time_ms: float = 0.0
    llm_cost: float = 0.0


class CompetitiveAnalyzer:
    """
    AI-powered competitive content analysis service.
    
    Features:
    - Content gap identification
    - Unique value proposition extraction
    - Competitive advantage analysis
    - Market positioning insights
    - Content depth comparison
    - Style differentiation analysis
    """
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
    
    async def analyze(
        self,
        content: str,
        title: Optional[str] = None,
        competitor_context: Optional[str] = None,
        industry: Optional[str] = None,
        target_audience: Optional[str] = None
    ) -> CompetitiveAnalysisResult:
        """
        Perform competitive content analysis.
        
        Args:
            content: Content to analyze
            title: Content title
            competitor_context: Information about competitor content
            industry: Industry/domain context
            target_audience: Target audience description
            
        Returns:
            CompetitiveAnalysisResult with complete analysis
        """
        start_time = datetime.now()
        
        # Identify content gaps
        content_gaps = await self._identify_content_gaps(
            content, title, competitor_context, industry
        )
        
        # Extract unique value propositions
        uvps = await self._extract_value_propositions(content, title)
        
        # Identify competitive advantages
        advantages = await self._identify_competitive_advantages(
            content, competitor_context
        )
        
        # Analyze market positioning
        market_position = await self._analyze_market_positioning(
            content, title, industry, target_audience
        )
        
        # Compare content depth
        content_depth = await self._compare_content_depth(
            content, competitor_context
        )
        
        # Analyze style differentiation
        style_diff = await self._analyze_style_differentiation(content)
        
        # Calculate competitive score
        competitive_score = self._calculate_competitive_score(
            content_gaps, uvps, advantages, content_depth
        )
        
        # Identify opportunities and threats
        opportunities = await self._identify_opportunities(
            content_gaps, advantages
        )
        
        threats = await self._identify_threats(
            content_gaps, content_depth
        )
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(
            content_gaps, advantages, opportunities
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds() * 1000
        
        return CompetitiveAnalysisResult(
            content_gaps=content_gaps,
            unique_value_propositions=uvps,
            competitive_advantages=advantages,
            market_position=market_position,
            content_depth=content_depth,
            style_differentiation=style_diff,
            overall_competitive_score=competitive_score,
            opportunities=opportunities,
            threats=threats,
            recommendations=recommendations,
            processing_time_ms=processing_time,
            llm_cost=self.llm.get_total_cost()
        )
    
    async def _identify_content_gaps(
        self,
        content: str,
        title: Optional[str],
        competitor_context: Optional[str],
        industry: Optional[str]
    ) -> List[ContentGap]:
        """Identify content gaps using LLM"""
        
        prompt = f"""Analyze this content and identify 3-5 content gaps - topics or aspects that are missing or underexplored.

{f'Title: {title}' if title else ''}
{f'Industry: {industry}' if industry else ''}
{f'Competitor Context: {competitor_context}' if competitor_context else 'No competitor data provided - identify gaps based on topic comprehensiveness'}

Content:
{content[:2500]}

For each gap, provide:
1. Topic/aspect name
2. Description of what's missing
3. Priority (high/medium/low)
4. Potential impact of filling this gap
5. Suggested action
6. Related keywords

Provide JSON:
{{
    "gaps": [
        {{
            "topic": "gap name",
            "description": "what's missing",
            "priority": "high|medium|low",
            "potential_impact": "impact description",
            "suggested_action": "action to take",
            "keywords": ["keyword1", "keyword2"]
        }}
    ]
}}"""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are a competitive content strategist.",
            temperature=0.4
        )
        
        gaps = []
        try:
            import json
            content_str = response.content.strip()
            if content_str.startswith('```'):
                content_str = content_str.split('```')[1]
                if content_str.startswith('json'):
                    content_str = content_str[4:]
                content_str = content_str.rsplit('```', 1)[0]
            
            data = json.loads(content_str)
            priority_map = {
                'high': ContentGapPriority.HIGH,
                'medium': ContentGapPriority.MEDIUM,
                'low': ContentGapPriority.LOW
            }
            
            for gap_data in data.get('gaps', [])[:5]:
                gaps.append(ContentGap(
                    topic=gap_data.get('topic', ''),
                    description=gap_data.get('description', ''),
                    priority=priority_map.get(gap_data.get('priority', 'medium'), ContentGapPriority.MEDIUM),
                    potential_impact=gap_data.get('potential_impact', ''),
                    suggested_action=gap_data.get('suggested_action', ''),
                    keywords=gap_data.get('keywords', [])[:5]
                ))
        except:
            pass
        
        return gaps
    
    async def _extract_value_propositions(
        self,
        content: str,
        title: Optional[str]
    ) -> List[UniqueValueProposition]:
        """Extract unique value propositions"""
        
        prompt = f"""Identify 3-5 unique value propositions in this content - what makes it special or different.

{f'Title: {title}' if title else ''}

Content:
{content[:2500]}

For each UVP:
1. Aspect/area of uniqueness
2. Description of what makes it unique
3. Strength (strong/moderate/weak)
4. Supporting points (2-3)

Provide JSON:
{{
    "uvps": [
        {{
            "aspect": "aspect name",
            "description": "what makes it unique",
            "strength": "strong|moderate|weak",
            "supporting_points": ["point1", "point2"]
        }}
    ]
}}"""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are a value proposition expert.",
            temperature=0.3
        )
        
        uvps = []
        try:
            import json
            content_str = response.content.strip()
            if content_str.startswith('```'):
                content_str = content_str.split('```')[1]
                if content_str.startswith('json'):
                    content_str = content_str[4:]
                content_str = content_str.rsplit('```', 1)[0]
            
            data = json.loads(content_str)
            strength_map = {
                'strong': CompetitiveStrength.STRONG,
                'moderate': CompetitiveStrength.MODERATE,
                'weak': CompetitiveStrength.WEAK
            }
            
            for uvp_data in data.get('uvps', [])[:5]:
                uvps.append(UniqueValueProposition(
                    aspect=uvp_data.get('aspect', ''),
                    description=uvp_data.get('description', ''),
                    strength=strength_map.get(uvp_data.get('strength', 'moderate'), CompetitiveStrength.MODERATE),
                    supporting_points=uvp_data.get('supporting_points', [])[:3]
                ))
        except:
            pass
        
        return uvps
    
    async def _identify_competitive_advantages(
        self,
        content: str,
        competitor_context: Optional[str]
    ) -> List[CompetitiveAdvantage]:
        """Identify competitive advantages"""
        
        prompt = f"""Identify 3-5 competitive advantages in this content.

{f'Competitor Context: {competitor_context}' if competitor_context else 'Analyze based on content quality, depth, clarity, and uniqueness'}

Content:
{content[:2500]}

Categories: content_depth, expertise_level, clarity, practical_value, innovation, credibility

For each advantage:
1. Category
2. Specific advantage
3. Strength (strong/moderate/weak)
4. Evidence (2-3 examples)
5. How to leverage it

Provide JSON:
{{
    "advantages": [
        {{
            "category": "category",
            "advantage": "advantage description",
            "strength": "strong|moderate|weak",
            "evidence": ["example1", "example2"],
            "how_to_leverage": "leverage strategy"
        }}
    ]
}}"""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are a competitive strategy analyst.",
            temperature=0.3
        )
        
        advantages = []
        try:
            import json
            content_str = response.content.strip()
            if content_str.startswith('```'):
                content_str = content_str.split('```')[1]
                if content_str.startswith('json'):
                    content_str = content_str[4:]
                content_str = content_str.rsplit('```', 1)[0]
            
            data = json.loads(content_str)
            strength_map = {
                'strong': CompetitiveStrength.STRONG,
                'moderate': CompetitiveStrength.MODERATE,
                'weak': CompetitiveStrength.WEAK
            }
            
            for adv_data in data.get('advantages', [])[:5]:
                advantages.append(CompetitiveAdvantage(
                    category=adv_data.get('category', ''),
                    advantage=adv_data.get('advantage', ''),
                    strength=strength_map.get(adv_data.get('strength', 'moderate'), CompetitiveStrength.MODERATE),
                    evidence=adv_data.get('evidence', [])[:3],
                    how_to_leverage=adv_data.get('how_to_leverage', '')
                ))
        except:
            pass
        
        return advantages
    
    async def _analyze_market_positioning(
        self,
        content: str,
        title: Optional[str],
        industry: Optional[str],
        target_audience: Optional[str]
    ) -> MarketPosition:
        """Analyze market positioning"""
        
        prompt = f"""Analyze the market positioning of this content.

{f'Title: {title}' if title else ''}
{f'Industry: {industry}' if industry else ''}
{f'Target Audience: {target_audience}' if target_audience else ''}

Content:
{content[:2000]}

Provide:
1. Positioning statement (1 sentence)
2. Target audience alignment (how well it matches)
3. Differentiation factors (3-5)
4. Competitive moat (1 sentence)
5. Market segment

Provide JSON:
{{
    "positioning_statement": "statement",
    "target_audience_alignment": "alignment description",
    "differentiation_factors": ["factor1", "factor2"],
    "competitive_moat": "moat description",
    "market_segment": "segment"
}}"""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are a market positioning strategist.",
            temperature=0.3
        )
        
        try:
            import json
            content_str = response.content.strip()
            if content_str.startswith('```'):
                content_str = content_str.split('```')[1]
                if content_str.startswith('json'):
                    content_str = content_str[4:]
                content_str = content_str.rsplit('```', 1)[0]
            
            data = json.loads(content_str)
            return MarketPosition(
                positioning_statement=data.get('positioning_statement', ''),
                target_audience_alignment=data.get('target_audience_alignment', ''),
                differentiation_factors=data.get('differentiation_factors', [])[:5],
                competitive_moat=data.get('competitive_moat', ''),
                market_segment=data.get('market_segment', '')
            )
        except:
            return MarketPosition(
                positioning_statement="Unable to determine positioning",
                target_audience_alignment="Unknown",
                differentiation_factors=[],
                competitive_moat="",
                market_segment=""
            )
    
    async def _compare_content_depth(
        self,
        content: str,
        competitor_context: Optional[str]
    ) -> ContentDepthComparison:
        """Compare content depth against competitors"""
        
        word_count = len(content.split())
        
        # Basic depth scoring
        if word_count < 300:
            depth_score = 3.0
            comprehensiveness = "shallow"
        elif word_count < 1000:
            depth_score = 5.0
            comprehensiveness = "moderate"
        else:
            depth_score = 8.0
            comprehensiveness = "comprehensive"
        
        # Use LLM for deeper analysis
        prompt = f"""Analyze the depth and comprehensiveness of this content.

{f'Competitor Context: {competitor_context}' if competitor_context else ''}

Content ({word_count} words):
{content[:2500]}

Provide:
1. Topic coverage percentage (0-100)
2. Detail level (surface/intermediate/expert)
3. Areas of strength (2-3)
4. Areas needing expansion (2-3)

Provide JSON:
{{
    "topic_coverage": 75,
    "detail_level": "intermediate",
    "areas_of_strength": ["area1", "area2"],
    "areas_needing_expansion": ["area1", "area2"]
}}"""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are a content depth analyst.",
            temperature=0.2
        )
        
        try:
            import json
            content_str = response.content.strip()
            if content_str.startswith('```'):
                content_str = content_str.split('```')[1]
                if content_str.startswith('json'):
                    content_str = content_str[4:]
                content_str = content_str.rsplit('```', 1)[0]
            
            data = json.loads(content_str)
            topic_coverage = data.get('topic_coverage', 50) / 100
            detail_level = data.get('detail_level', 'intermediate')
            areas_of_strength = data.get('areas_of_strength', [])[:3]
            areas_needing_expansion = data.get('areas_needing_expansion', [])[:3]
        except:
            topic_coverage = 0.5
            detail_level = 'intermediate'
            areas_of_strength = []
            areas_needing_expansion = []
        
        return ContentDepthComparison(
            depth_score=depth_score,
            comprehensiveness=comprehensiveness,
            topic_coverage=topic_coverage,
            detail_level=detail_level,
            areas_of_strength=areas_of_strength,
            areas_needing_expansion=areas_needing_expansion
        )
    
    async def _analyze_style_differentiation(
        self,
        content: str
    ) -> StyleDifferentiation:
        """Analyze style and tone differentiation"""
        
        prompt = f"""Analyze the writing style and tone of this content for differentiation.

Content:
{content[:2000]}

Provide:
1. Tone uniqueness (0.0-1.0 scale)
2. Voice distinctiveness description
3. Style advantages (2-3)
4. Style weaknesses (1-2)
5. Recommended adjustments (2-3)

Provide JSON:
{{
    "tone_uniqueness": 0.7,
    "voice_distinctiveness": "description",
    "style_advantages": ["adv1", "adv2"],
    "style_weaknesses": ["weak1"],
    "recommended_adjustments": ["adj1", "adj2"]
}}"""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are a writing style analyst.",
            temperature=0.3
        )
        
        try:
            import json
            content_str = response.content.strip()
            if content_str.startswith('```'):
                content_str = content_str.split('```')[1]
                if content_str.startswith('json'):
                    content_str = content_str[4:]
                content_str = content_str.rsplit('```', 1)[0]
            
            data = json.loads(content_str)
            return StyleDifferentiation(
                tone_uniqueness=data.get('tone_uniqueness', 0.5),
                voice_distinctiveness=data.get('voice_distinctiveness', ''),
                style_advantages=data.get('style_advantages', [])[:3],
                style_weaknesses=data.get('style_weaknesses', [])[:2],
                recommended_adjustments=data.get('recommended_adjustments', [])[:3]
            )
        except:
            return StyleDifferentiation(
                tone_uniqueness=0.5,
                voice_distinctiveness="Standard",
                style_advantages=[],
                style_weaknesses=[],
                recommended_adjustments=[]
            )
    
    def _calculate_competitive_score(
        self,
        gaps: List[ContentGap],
        uvps: List[UniqueValueProposition],
        advantages: List[CompetitiveAdvantage],
        depth: ContentDepthComparison
    ) -> float:
        """Calculate overall competitive score (0-100)"""
        
        # Gap score (fewer gaps = better, high priority gaps = worse)
        high_priority_gaps = sum(1 for g in gaps if g.priority == ContentGapPriority.HIGH)
        gap_score = max(0, 100 - (len(gaps) * 10) - (high_priority_gaps * 10))
        
        # UVP score (more strong UVPs = better)
        strong_uvps = sum(1 for u in uvps if u.strength == CompetitiveStrength.STRONG)
        uvp_score = min(100, len(uvps) * 15 + strong_uvps * 10)
        
        # Advantage score (more strong advantages = better)
        strong_advantages = sum(1 for a in advantages if a.strength == CompetitiveStrength.STRONG)
        adv_score = min(100, len(advantages) * 15 + strong_advantages * 10)
        
        # Depth score (0-10 scale to 0-100)
        depth_score = depth.depth_score * 10 if depth else 50
        
        # Weighted average
        overall = (
            gap_score * 0.25 +
            uvp_score * 0.25 +
            adv_score * 0.3 +
            depth_score * 0.2
        )
        
        return min(100.0, max(0.0, overall))
    
    async def _identify_opportunities(
        self,
        gaps: List[ContentGap],
        advantages: List[CompetitiveAdvantage]
    ) -> List[str]:
        """Identify strategic opportunities"""
        
        opportunities = []
        
        # High priority gaps are opportunities
        for gap in gaps:
            if gap.priority == ContentGapPriority.HIGH:
                opportunities.append(f"Fill gap: {gap.topic} - {gap.suggested_action}")
        
        # Leverage strong advantages
        for adv in advantages:
            if adv.strength == CompetitiveStrength.STRONG:
                opportunities.append(f"Leverage: {adv.how_to_leverage}")
        
        return opportunities[:7]
    
    async def _identify_threats(
        self,
        gaps: List[ContentGap],
        depth: ContentDepthComparison
    ) -> List[str]:
        """Identify competitive threats"""
        
        threats = []
        
        # High priority gaps are threats
        high_priority_count = sum(1 for g in gaps if g.priority == ContentGapPriority.HIGH)
        if high_priority_count > 2:
            threats.append(f"Multiple high-priority content gaps ({high_priority_count}) may weaken competitive position")
        
        # Shallow content is a threat
        if depth.comprehensiveness == "shallow":
            threats.append("Content depth insufficient compared to comprehensive competitor content")
        
        # Areas needing expansion
        if depth.areas_needing_expansion:
            threats.append(f"Competitors may have stronger coverage in: {', '.join(depth.areas_needing_expansion[:2])}")
        
        return threats[:5]
    
    async def _generate_recommendations(
        self,
        gaps: List[ContentGap],
        advantages: List[CompetitiveAdvantage],
        opportunities: List[str]
    ) -> List[str]:
        """Generate competitive recommendations"""
        
        recommendations = []
        
        # Address high priority gaps first
        high_priority_gaps = [g for g in gaps if g.priority == ContentGapPriority.HIGH]
        for gap in high_priority_gaps[:2]:
            recommendations.append(f"Priority: {gap.suggested_action}")
        
        # Leverage strong advantages
        strong_advs = [a for a in advantages if a.strength == CompetitiveStrength.STRONG]
        for adv in strong_advs[:2]:
            if adv.how_to_leverage:
                recommendations.append(adv.how_to_leverage)
        
        # General recommendations
        if len(gaps) > 3:
            recommendations.append("Expand content to cover identified gaps and improve comprehensiveness")
        
        if advantages:
            recommendations.append("Highlight unique value propositions in marketing and content distribution")
        
        return recommendations[:7]

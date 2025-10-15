"""
Sentiment and Tone Analyzer

Provides comprehensive sentiment and emotional analysis:
- Sentiment scoring (-1 to +1)
- Tone detection (professional, casual, formal, etc.)
- Emotion analysis
- Subjectivity vs objectivity
- Confidence metrics
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from .llm_service import LLMService


class SentimentPolarity(str, Enum):
    """Overall sentiment classification"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"
    MIXED = "mixed"


class ToneType(str, Enum):
    """Content tone classifications"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FORMAL = "formal"
    INFORMAL = "informal"
    CONVERSATIONAL = "conversational"
    AUTHORITATIVE = "authoritative"
    FRIENDLY = "friendly"
    ACADEMIC = "academic"
    PERSUASIVE = "persuasive"
    INSPIRATIONAL = "inspirational"
    HUMOROUS = "humorous"
    SERIOUS = "serious"


class EmotionType(str, Enum):
    """Emotion classifications"""
    JOY = "joy"
    TRUST = "trust"
    FEAR = "fear"
    SURPRISE = "surprise"
    SADNESS = "sadness"
    DISGUST = "disgust"
    ANGER = "anger"
    ANTICIPATION = "anticipation"


@dataclass
class EmotionScore:
    """Individual emotion with intensity"""
    emotion: EmotionType
    intensity: float  # 0.0 to 1.0
    keywords: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)


@dataclass
class SentimentScore:
    """Detailed sentiment analysis"""
    polarity: SentimentPolarity
    score: float  # -1.0 (very negative) to +1.0 (very positive)
    confidence: float  # 0.0 to 1.0
    subjectivity: float  # 0.0 (objective) to 1.0 (subjective)
    positive_ratio: float  # Ratio of positive content
    negative_ratio: float  # Ratio of negative content
    neutral_ratio: float  # Ratio of neutral content


@dataclass
class ToneAnalysis:
    """Tone analysis results"""
    primary_tone: ToneType
    secondary_tones: List[ToneType] = field(default_factory=list)
    tone_consistency: float = 0.0  # 0.0 to 1.0
    formality_level: float = 0.0  # 0.0 (informal) to 1.0 (formal)
    professionalism_score: float = 0.0  # 0.0 to 1.0
    tone_shifts: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SentimentAnalysisResult:
    """Complete sentiment and tone analysis"""
    sentiment: SentimentScore
    tone: ToneAnalysis
    emotions: List[EmotionScore] = field(default_factory=list)
    dominant_emotion: Optional[EmotionType] = None
    overall_mood: Optional[str] = None
    audience_perception: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)
    processing_time_ms: float = 0.0
    llm_cost: float = 0.0


class SentimentAnalyzer:
    """
    AI-powered sentiment and tone analysis service.
    
    Features:
    - Multi-dimensional sentiment scoring
    - Tone detection and classification
    - Emotion analysis with Plutchik's wheel
    - Subjectivity analysis
    - Audience perception insights
    """
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
    
    async def analyze(
        self,
        content: str,
        title: Optional[str] = None,
        analyze_emotions: bool = True,
        analyze_tone_shifts: bool = False
    ) -> SentimentAnalysisResult:
        """
        Perform comprehensive sentiment and tone analysis.
        
        Args:
            content: Text content to analyze
            title: Optional content title
            analyze_emotions: Whether to perform emotion analysis
            analyze_tone_shifts: Whether to detect tone shifts
            
        Returns:
            SentimentAnalysisResult with complete analysis
        """
        start_time = datetime.now()
        
        # Analyze sentiment
        sentiment = await self._analyze_sentiment(content, title)
        
        # Analyze tone
        tone = await self._analyze_tone(content, title, analyze_tone_shifts)
        
        # Analyze emotions
        emotions = []
        dominant_emotion = None
        if analyze_emotions:
            emotions = await self._analyze_emotions(content)
            if emotions:
                dominant_emotion = max(emotions, key=lambda e: e.intensity).emotion
        
        # Determine overall mood
        overall_mood = await self._determine_mood(content, sentiment, emotions)
        
        # Analyze audience perception
        audience_perception = await self._analyze_audience_perception(
            content, sentiment, tone
        )
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(
            content, sentiment, tone, emotions
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds() * 1000
        
        return SentimentAnalysisResult(
            sentiment=sentiment,
            tone=tone,
            emotions=emotions,
            dominant_emotion=dominant_emotion,
            overall_mood=overall_mood,
            audience_perception=audience_perception,
            recommendations=recommendations,
            processing_time_ms=processing_time,
            llm_cost=self.llm.get_total_cost()
        )
    
    async def _analyze_sentiment(
        self,
        content: str,
        title: Optional[str]
    ) -> SentimentScore:
        """Analyze sentiment polarity and subjectivity"""
        
        system_prompt = """You are an expert sentiment analyst. Analyze sentiment accurately 
using nuanced understanding of language, context, and emotional tone."""
        
        prompt = f"""Analyze the sentiment of this content. Provide detailed scores.

{f'Title: {title}' if title else ''}

Content:
{content[:4000]}

Provide analysis in JSON format:
{{
  "polarity": "positive|negative|neutral|mixed",
  "score": 0.75,  // -1.0 to +1.0
  "confidence": 0.9,  // 0.0 to 1.0
  "subjectivity": 0.6,  // 0.0 (objective) to 1.0 (subjective)
  "positive_ratio": 0.6,
  "negative_ratio": 0.1,
  "neutral_ratio": 0.3,
  "explanation": "Brief explanation of the sentiment"
}}

Guidelines:
- score: -1.0 = very negative, 0.0 = neutral, +1.0 = very positive
- confidence: how certain you are about the analysis
- subjectivity: 0.0 = purely factual, 1.0 = highly opinionated
- Ratios should sum to approximately 1.0

Provide only valid JSON, no additional text."""
        
        response = await self.llm.complete(
            prompt,
            system_prompt=system_prompt,
            temperature=0.3  # Lower temperature for consistent analysis
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
            
            # Map polarity string to enum
            polarity_map = {
                "very_positive": SentimentPolarity.VERY_POSITIVE,
                "positive": SentimentPolarity.POSITIVE,
                "neutral": SentimentPolarity.NEUTRAL,
                "negative": SentimentPolarity.NEGATIVE,
                "very_negative": SentimentPolarity.VERY_NEGATIVE,
                "mixed": SentimentPolarity.MIXED
            }
            
            polarity_str = data.get('polarity', 'neutral').lower()
            if polarity_str not in polarity_map:
                # Infer from score
                score = data.get('score', 0.0)
                if score > 0.6:
                    polarity = SentimentPolarity.VERY_POSITIVE
                elif score > 0.2:
                    polarity = SentimentPolarity.POSITIVE
                elif score < -0.6:
                    polarity = SentimentPolarity.VERY_NEGATIVE
                elif score < -0.2:
                    polarity = SentimentPolarity.NEGATIVE
                else:
                    polarity = SentimentPolarity.NEUTRAL
            else:
                polarity = polarity_map[polarity_str]
            
            return SentimentScore(
                polarity=polarity,
                score=float(data.get('score', 0.0)),
                confidence=float(data.get('confidence', 0.7)),
                subjectivity=float(data.get('subjectivity', 0.5)),
                positive_ratio=float(data.get('positive_ratio', 0.33)),
                negative_ratio=float(data.get('negative_ratio', 0.33)),
                neutral_ratio=float(data.get('neutral_ratio', 0.34))
            )
            
        except Exception as e:
            print(f"Error parsing sentiment: {e}")
            # Fallback to neutral sentiment
            return SentimentScore(
                polarity=SentimentPolarity.NEUTRAL,
                score=0.0,
                confidence=0.5,
                subjectivity=0.5,
                positive_ratio=0.33,
                negative_ratio=0.33,
                neutral_ratio=0.34
            )
    
    async def _analyze_tone(
        self,
        content: str,
        title: Optional[str],
        analyze_shifts: bool
    ) -> ToneAnalysis:
        """Analyze content tone"""
        
        system_prompt = """You are a communication tone expert. Identify the tone, 
formality level, and professionalism of written content."""
        
        prompt = f"""Analyze the tone of this content.

{f'Title: {title}' if title else ''}

Content:
{content[:4000]}

Provide analysis in JSON format:
{{
  "primary_tone": "professional|casual|formal|conversational|etc",
  "secondary_tones": ["authoritative", "friendly"],
  "formality_level": 0.7,  // 0.0 (informal) to 1.0 (formal)
  "professionalism_score": 0.8,  // 0.0 to 1.0
  "tone_consistency": 0.9,  // 0.0 to 1.0
  "explanation": "Brief explanation"
}}

Tone options: professional, casual, formal, informal, conversational, authoritative, 
friendly, academic, persuasive, inspirational, humorous, serious

Provide only valid JSON."""
        
        response = await self.llm.complete(
            prompt,
            system_prompt=system_prompt,
            temperature=0.3
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
            
            # Map tone string to enum
            tone_map = {t.value: t for t in ToneType}
            primary_tone_str = data.get('primary_tone', 'professional').lower()
            primary_tone = tone_map.get(primary_tone_str, ToneType.PROFESSIONAL)
            
            secondary_tones = [
                tone_map.get(t.lower(), ToneType.PROFESSIONAL)
                for t in data.get('secondary_tones', [])
                if t.lower() in tone_map
            ]
            
            return ToneAnalysis(
                primary_tone=primary_tone,
                secondary_tones=secondary_tones,
                tone_consistency=float(data.get('tone_consistency', 0.8)),
                formality_level=float(data.get('formality_level', 0.5)),
                professionalism_score=float(data.get('professionalism_score', 0.7))
            )
            
        except Exception as e:
            print(f"Error parsing tone: {e}")
            return ToneAnalysis(
                primary_tone=ToneType.PROFESSIONAL,
                tone_consistency=0.7,
                formality_level=0.5,
                professionalism_score=0.7
            )
    
    async def _analyze_emotions(self, content: str) -> List[EmotionScore]:
        """Analyze emotions using Plutchik's wheel"""
        
        system_prompt = """You are an emotion analysis expert using Plutchik's wheel of emotions. 
Identify emotions and their intensity in text."""
        
        prompt = f"""Identify the emotions present in this content and rate their intensity.

Content:
{content[:4000]}

Use Plutchik's 8 basic emotions: joy, trust, fear, surprise, sadness, disgust, anger, anticipation

Provide analysis in JSON format:
[
  {{
    "emotion": "joy",
    "intensity": 0.8,  // 0.0 to 1.0
    "keywords": ["happy", "excited", "wonderful"],
    "examples": ["specific phrase showing this emotion"]
  }}
]

Only include emotions with intensity > 0.2. Provide only valid JSON."""
        
        response = await self.llm.complete(
            prompt,
            system_prompt=system_prompt,
            temperature=0.3
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
            
            emotion_map = {e.value: e for e in EmotionType}
            emotions = []
            
            for item in data:
                emotion_str = item.get('emotion', '').lower()
                if emotion_str in emotion_map:
                    emotions.append(EmotionScore(
                        emotion=emotion_map[emotion_str],
                        intensity=float(item.get('intensity', 0.5)),
                        keywords=item.get('keywords', []),
                        examples=item.get('examples', [])
                    ))
            
            # Sort by intensity
            emotions.sort(key=lambda e: e.intensity, reverse=True)
            return emotions[:5]  # Top 5 emotions
            
        except Exception as e:
            print(f"Error parsing emotions: {e}")
            return []
    
    async def _determine_mood(
        self,
        content: str,
        sentiment: SentimentScore,
        emotions: List[EmotionScore]
    ) -> str:
        """Determine overall mood/atmosphere"""
        
        # Quick determination based on sentiment and emotions
        if sentiment.score > 0.5 and any(e.emotion == EmotionType.JOY for e in emotions):
            return "optimistic and uplifting"
        elif sentiment.score < -0.5:
            return "critical or concerned"
        elif sentiment.subjectivity < 0.3:
            return "objective and informative"
        elif sentiment.score > 0.2:
            return "positive and engaging"
        else:
            return "balanced and neutral"
    
    async def _analyze_audience_perception(
        self,
        content: str,
        sentiment: SentimentScore,
        tone: ToneAnalysis
    ) -> str:
        """Analyze how audience might perceive the content"""
        
        prompt = f"""Based on this analysis, how would readers likely perceive this content?

Sentiment: {sentiment.polarity.value} (score: {sentiment.score:.2f})
Tone: {tone.primary_tone.value}
Formality: {tone.formality_level:.2f}
Subjectivity: {sentiment.subjectivity:.2f}

Provide a brief 1-2 sentence description of likely audience perception."""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are an audience psychology expert.",
            max_tokens=100
        )
        
        return response.content.strip()
    
    async def _generate_recommendations(
        self,
        content: str,
        sentiment: SentimentScore,
        tone: ToneAnalysis,
        emotions: List[EmotionScore]
    ) -> List[str]:
        """Generate recommendations for improving sentiment/tone"""
        
        recommendations = []
        
        # Sentiment recommendations
        if sentiment.score < -0.3:
            recommendations.append("Consider balancing negative sentiment with constructive elements")
        
        if sentiment.subjectivity > 0.7:
            recommendations.append("Add more objective facts to balance subjective opinions")
        
        # Tone recommendations
        if tone.tone_consistency < 0.6:
            recommendations.append("Maintain more consistent tone throughout the content")
        
        if tone.formality_level < 0.3 and tone.professionalism_score > 0.7:
            recommendations.append("Consider increasing formality to match professional context")
        
        # Emotion recommendations
        negative_emotions = [e for e in emotions if e.emotion in [
            EmotionType.FEAR, EmotionType.ANGER, EmotionType.SADNESS, EmotionType.DISGUST
        ]]
        
        if len(negative_emotions) > 2:
            recommendations.append("High negative emotion detected - consider balancing with positive elements")
        
        return recommendations[:5]  # Top 5 recommendations
    
    async def quick_sentiment_score(self, content: str) -> float:
        """
        Quick sentiment score without full analysis.
        
        Args:
            content: Text to analyze
            
        Returns:
            Sentiment score (-1.0 to +1.0)
        """
        prompt = f"""Rate the sentiment of this text on a scale from -1.0 (very negative) 
to +1.0 (very positive). Provide only the number.

Text: {content[:2000]}

Score:"""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are a sentiment scoring expert.",
            max_tokens=10,
            temperature=0.1
        )
        
        try:
            score = float(response.content.strip())
            return max(-1.0, min(1.0, score))
        except:
            return 0.0

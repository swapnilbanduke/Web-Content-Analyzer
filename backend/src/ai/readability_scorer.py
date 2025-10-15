"""
Readability and Accessibility Scoring Service

Comprehensive readability analysis including:
- Flesch-Kincaid Grade Level and Reading Ease
- SMOG Index
- Gunning Fog Index
- Coleman-Liau Index
- Automated Readability Index (ARI)
- WCAG accessibility checks
- Sentence and vocabulary complexity
- Grade level recommendations
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import math

from .llm_service import LLMService


class ReadingLevel(str, Enum):
    """Reading difficulty levels"""
    VERY_EASY = "very_easy"  # Grade 5 or below
    EASY = "easy"  # Grade 6-8
    MODERATE = "moderate"  # Grade 9-10
    DIFFICULT = "difficult"  # Grade 11-12
    VERY_DIFFICULT = "very_difficult"  # College level+


class AccessibilityLevel(str, Enum):
    """WCAG accessibility levels"""
    AAA = "AAA"  # Highest
    AA = "AA"  # Standard
    A = "A"  # Basic
    FAIL = "fail"  # Does not meet standards


@dataclass
class ReadabilityMetrics:
    """Core readability scores"""
    flesch_reading_ease: float  # 0-100 (higher = easier)
    flesch_kincaid_grade: float  # Grade level
    smog_index: float  # Grade level
    gunning_fog_index: float  # Grade level
    coleman_liau_index: float  # Grade level
    automated_readability_index: float  # Grade level
    average_grade_level: float
    reading_level: ReadingLevel


@dataclass
class TextComplexity:
    """Text complexity metrics"""
    word_count: int
    sentence_count: int
    paragraph_count: int
    avg_words_per_sentence: float
    avg_sentences_per_paragraph: float
    avg_syllables_per_word: float
    complex_words_count: int  # 3+ syllables
    complex_words_percentage: float
    long_sentences_count: int  # 25+ words
    long_sentences_percentage: float


@dataclass
class VocabularyAnalysis:
    """Vocabulary complexity analysis"""
    unique_words: int
    lexical_diversity: float  # 0.0 to 1.0
    difficult_words: List[str] = field(default_factory=list)
    difficult_words_count: int = 0
    jargon_terms: List[str] = field(default_factory=list)
    passive_voice_count: int = 0
    passive_voice_percentage: float = 0.0
    adverb_count: int = 0
    adverb_percentage: float = 0.0


@dataclass
class AccessibilityScore:
    """WCAG accessibility assessment"""
    level: AccessibilityLevel
    score: float  # 0 to 100
    plain_language_score: float  # 0 to 100
    heading_structure_score: float  # 0 to 100
    list_usage_score: float  # 0 to 100
    sentence_clarity_score: float  # 0 to 100
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ImprovementSuggestion:
    """Specific improvement suggestion"""
    type: str  # 'sentence', 'word', 'structure'
    issue: str
    example: str
    suggestion: str
    priority: str  # 'high', 'medium', 'low'


@dataclass
class ReadabilityAnalysisResult:
    """Complete readability analysis"""
    readability_metrics: ReadabilityMetrics
    text_complexity: TextComplexity
    vocabulary: VocabularyAnalysis
    accessibility: AccessibilityScore
    target_audience_grade: str
    estimated_reading_time_minutes: float
    improvements: List[ImprovementSuggestion] = field(default_factory=list)
    summary: str = ""
    overall_score: float = 0.0  # 0 to 100
    processing_time_ms: float = 0.0
    llm_cost: float = 0.0


class ReadabilityScorer:
    """
    Comprehensive readability and accessibility scoring service.
    
    Features:
    - Multiple readability formulas (Flesch-Kincaid, SMOG, Gunning Fog, etc.)
    - Text complexity analysis
    - Vocabulary difficulty assessment
    - WCAG accessibility scoring
    - Actionable improvement suggestions
    """
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
    
    async def analyze(
        self,
        content: str,
        title: Optional[str] = None,
        check_accessibility: bool = True,
        generate_improvements: bool = True
    ) -> ReadabilityAnalysisResult:
        """
        Perform comprehensive readability analysis.
        
        Args:
            content: Text content to analyze
            title: Optional title
            check_accessibility: Whether to perform accessibility checks
            generate_improvements: Whether to generate improvement suggestions
            
        Returns:
            ReadabilityAnalysisResult with complete analysis
        """
        from datetime import datetime
        start_time = datetime.now()
        
        # Calculate text complexity
        text_complexity = self._calculate_text_complexity(content)
        
        # Calculate readability metrics
        readability_metrics = self._calculate_readability_metrics(
            content, text_complexity
        )
        
        # Analyze vocabulary
        vocabulary = await self._analyze_vocabulary(content)
        
        # Check accessibility
        accessibility = await self._check_accessibility(
            content, text_complexity
        ) if check_accessibility else AccessibilityScore(
            level=AccessibilityLevel.AA,
            score=75.0,
            plain_language_score=75.0,
            heading_structure_score=75.0,
            list_usage_score=75.0,
            sentence_clarity_score=75.0
        )
        
        # Determine target audience
        target_audience = self._determine_target_audience(readability_metrics)
        
        # Calculate reading time
        reading_time = text_complexity.word_count / 200  # 200 WPM average
        
        # Generate improvements
        improvements = await self._generate_improvements(
            content, readability_metrics, text_complexity, vocabulary
        ) if generate_improvements else []
        
        # Generate summary
        summary = await self._generate_summary(
            readability_metrics, text_complexity, accessibility
        )
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            readability_metrics, accessibility
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds() * 1000
        
        return ReadabilityAnalysisResult(
            readability_metrics=readability_metrics,
            text_complexity=text_complexity,
            vocabulary=vocabulary,
            accessibility=accessibility,
            target_audience_grade=target_audience,
            estimated_reading_time_minutes=reading_time,
            improvements=improvements,
            summary=summary,
            overall_score=overall_score,
            processing_time_ms=processing_time,
            llm_cost=self.llm.get_total_cost()
        )
    
    def _calculate_text_complexity(self, content: str) -> TextComplexity:
        """Calculate text complexity metrics"""
        
        # Clean content
        content = content.strip()
        
        # Count words
        words = re.findall(r'\b\w+\b', content.lower())
        word_count = len(words)
        
        # Count sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)
        
        # Count paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)
        
        # Average words per sentence
        avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0
        
        # Average sentences per paragraph
        avg_sentences_per_paragraph = sentence_count / paragraph_count if paragraph_count > 0 else 0
        
        # Count syllables
        total_syllables = sum(self._count_syllables(word) for word in words)
        avg_syllables_per_word = total_syllables / word_count if word_count > 0 else 0
        
        # Complex words (3+ syllables)
        complex_words = [w for w in words if self._count_syllables(w) >= 3]
        complex_words_count = len(complex_words)
        complex_words_percentage = (complex_words_count / word_count * 100) if word_count > 0 else 0
        
        # Long sentences (25+ words)
        long_sentences = [s for s in sentences if len(s.split()) >= 25]
        long_sentences_count = len(long_sentences)
        long_sentences_percentage = (long_sentences_count / sentence_count * 100) if sentence_count > 0 else 0
        
        return TextComplexity(
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            avg_words_per_sentence=avg_words_per_sentence,
            avg_sentences_per_paragraph=avg_sentences_per_paragraph,
            avg_syllables_per_word=avg_syllables_per_word,
            complex_words_count=complex_words_count,
            complex_words_percentage=complex_words_percentage,
            long_sentences_count=long_sentences_count,
            long_sentences_percentage=long_sentences_percentage
        )
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simple approximation)"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent 'e'
        if word.endswith('e'):
            syllable_count -= 1
        
        # Ensure at least one syllable
        if syllable_count == 0:
            syllable_count = 1
        
        return syllable_count
    
    def _calculate_readability_metrics(
        self,
        content: str,
        complexity: TextComplexity
    ) -> ReadabilityMetrics:
        """Calculate various readability scores"""
        
        # Flesch Reading Ease (0-100, higher = easier)
        flesch_ease = 206.835 - (1.015 * complexity.avg_words_per_sentence) - \
                     (84.6 * complexity.avg_syllables_per_word)
        flesch_ease = max(0, min(100, flesch_ease))  # Clamp to 0-100
        
        # Flesch-Kincaid Grade Level
        fk_grade = (0.39 * complexity.avg_words_per_sentence) + \
                   (11.8 * complexity.avg_syllables_per_word) - 15.59
        fk_grade = max(0, fk_grade)
        
        # SMOG Index (requires 30+ sentences)
        if complexity.sentence_count >= 30:
            smog = 1.0430 * math.sqrt(complexity.complex_words_count * (30 / complexity.sentence_count)) + 3.1291
        else:
            smog = fk_grade  # Fallback to FK grade
        
        # Gunning Fog Index
        fog = 0.4 * (complexity.avg_words_per_sentence + complexity.complex_words_percentage)
        
        # Coleman-Liau Index
        # L = average letters per 100 words, S = average sentences per 100 words
        letters_per_100 = (sum(len(w) for w in re.findall(r'\b\w+\b', content)) / complexity.word_count * 100) if complexity.word_count > 0 else 0
        sentences_per_100 = (complexity.sentence_count / complexity.word_count * 100) if complexity.word_count > 0 else 0
        coleman_liau = (0.0588 * letters_per_100) - (0.296 * sentences_per_100) - 15.8
        coleman_liau = max(0, coleman_liau)
        
        # Automated Readability Index (ARI)
        chars_per_word = sum(len(w) for w in re.findall(r'\b\w+\b', content)) / complexity.word_count if complexity.word_count > 0 else 0
        ari = (4.71 * chars_per_word) + (0.5 * complexity.avg_words_per_sentence) - 21.43
        ari = max(0, ari)
        
        # Average grade level
        avg_grade = (fk_grade + smog + fog + coleman_liau + ari) / 5
        
        # Determine reading level
        if avg_grade <= 5:
            reading_level = ReadingLevel.VERY_EASY
        elif avg_grade <= 8:
            reading_level = ReadingLevel.EASY
        elif avg_grade <= 10:
            reading_level = ReadingLevel.MODERATE
        elif avg_grade <= 12:
            reading_level = ReadingLevel.DIFFICULT
        else:
            reading_level = ReadingLevel.VERY_DIFFICULT
        
        return ReadabilityMetrics(
            flesch_reading_ease=flesch_ease,
            flesch_kincaid_grade=fk_grade,
            smog_index=smog,
            gunning_fog_index=fog,
            coleman_liau_index=coleman_liau,
            automated_readability_index=ari,
            average_grade_level=avg_grade,
            reading_level=reading_level
        )
    
    async def _analyze_vocabulary(self, content: str) -> VocabularyAnalysis:
        """Analyze vocabulary complexity using LLM"""
        
        words = re.findall(r'\b\w+\b', content.lower())
        word_count = len(words)
        unique_words = len(set(words))
        
        # Lexical diversity (type-token ratio)
        lexical_diversity = unique_words / word_count if word_count > 0 else 0
        
        # Use LLM to identify difficult words and jargon
        prompt = f"""Analyze this text and identify:
1. Difficult words (uncommon, technical, or complex words)
2. Jargon or specialized terminology
3. Count of passive voice sentences
4. Count of unnecessary adverbs

Text:
{content[:2000]}

Provide JSON:
{{
    "difficult_words": ["word1", "word2", ...],
    "jargon_terms": ["term1", "term2", ...],
    "passive_voice_count": 0,
    "adverb_count": 0
}}"""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are a writing clarity expert.",
            temperature=0.2
        )
        
        try:
            import json
            # Handle markdown code blocks
            content_str = response.content.strip()
            if content_str.startswith('```'):
                content_str = content_str.split('```')[1]
                if content_str.startswith('json'):
                    content_str = content_str[4:]
                content_str = content_str.rsplit('```', 1)[0]
            
            data = json.loads(content_str)
            difficult_words = data.get('difficult_words', [])[:20]
            jargon_terms = data.get('jargon_terms', [])[:15]
            passive_count = data.get('passive_voice_count', 0)
            adverb_count = data.get('adverb_count', 0)
        except:
            difficult_words = []
            jargon_terms = []
            passive_count = 0
            adverb_count = 0
        
        # Calculate percentages
        sentence_count = len(re.split(r'[.!?]+', content))
        passive_percentage = (passive_count / sentence_count * 100) if sentence_count > 0 else 0
        adverb_percentage = (adverb_count / word_count * 100) if word_count > 0 else 0
        
        return VocabularyAnalysis(
            unique_words=unique_words,
            lexical_diversity=lexical_diversity,
            difficult_words=difficult_words,
            difficult_words_count=len(difficult_words),
            jargon_terms=jargon_terms,
            passive_voice_count=passive_count,
            passive_voice_percentage=passive_percentage,
            adverb_count=adverb_count,
            adverb_percentage=adverb_percentage
        )
    
    async def _check_accessibility(
        self,
        content: str,
        complexity: TextComplexity
    ) -> AccessibilityScore:
        """Check WCAG accessibility compliance"""
        
        # Plain language score (based on readability)
        plain_language_score = 100 - (complexity.avg_words_per_sentence - 15) * 3
        plain_language_score = max(0, min(100, plain_language_score))
        
        # Heading structure (would need actual headings)
        has_structure = bool(re.search(r'^#+\s+\w+', content, re.MULTILINE))
        heading_structure_score = 80 if has_structure else 40
        
        # List usage (improves scannability)
        has_lists = bool(re.search(r'[-*•]\s+\w+|^\d+\.\s+\w+', content, re.MULTILINE))
        list_usage_score = 80 if has_lists else 50
        
        # Sentence clarity (based on complexity)
        sentence_clarity_score = 100 - complexity.long_sentences_percentage
        sentence_clarity_score = max(0, min(100, sentence_clarity_score))
        
        # Overall accessibility score
        overall_score = (
            plain_language_score * 0.3 +
            heading_structure_score * 0.25 +
            list_usage_score * 0.2 +
            sentence_clarity_score * 0.25
        )
        
        # Determine WCAG level
        if overall_score >= 85:
            level = AccessibilityLevel.AAA
        elif overall_score >= 70:
            level = AccessibilityLevel.AA
        elif overall_score >= 55:
            level = AccessibilityLevel.A
        else:
            level = AccessibilityLevel.FAIL
        
        # Identify issues
        issues = []
        if plain_language_score < 70:
            issues.append("Complex language may be difficult for some readers")
        if not has_structure:
            issues.append("Missing clear heading structure")
        if not has_lists:
            issues.append("Limited use of lists for better scannability")
        if complexity.long_sentences_percentage > 20:
            issues.append("Too many long sentences (25+ words)")
        
        # Recommendations
        recommendations = []
        if plain_language_score < 70:
            recommendations.append("Use simpler, more common words")
        if complexity.avg_words_per_sentence > 20:
            recommendations.append("Break long sentences into shorter ones")
        if not has_lists:
            recommendations.append("Use bullet points or numbered lists")
        if not has_structure:
            recommendations.append("Add clear headings and subheadings")
        
        return AccessibilityScore(
            level=level,
            score=overall_score,
            plain_language_score=plain_language_score,
            heading_structure_score=heading_structure_score,
            list_usage_score=list_usage_score,
            sentence_clarity_score=sentence_clarity_score,
            issues=issues,
            recommendations=recommendations
        )
    
    def _determine_target_audience(self, metrics: ReadabilityMetrics) -> str:
        """Determine target audience based on grade level"""
        
        grade = metrics.average_grade_level
        
        if grade <= 6:
            return "Elementary school (ages 6-12)"
        elif grade <= 8:
            return "Middle school (ages 12-14)"
        elif grade <= 10:
            return "High school (ages 14-16)"
        elif grade <= 12:
            return "High school seniors (ages 16-18)"
        elif grade <= 14:
            return "College undergraduates"
        else:
            return "College graduates / Professionals"
    
    async def _generate_improvements(
        self,
        content: str,
        metrics: ReadabilityMetrics,
        complexity: TextComplexity,
        vocabulary: VocabularyAnalysis
    ) -> List[ImprovementSuggestion]:
        """Generate specific improvement suggestions using LLM"""
        
        improvements = []
        
        # Identify issues
        issues_to_fix = []
        
        if complexity.avg_words_per_sentence > 20:
            issues_to_fix.append("long sentences")
        if complexity.complex_words_percentage > 15:
            issues_to_fix.append("complex words")
        if vocabulary.passive_voice_percentage > 10:
            issues_to_fix.append("passive voice")
        if vocabulary.adverb_percentage > 5:
            issues_to_fix.append("excessive adverbs")
        
        if not issues_to_fix:
            return improvements
        
        # Get specific examples from LLM
        prompt = f"""Find 3-5 specific examples from this text that need improvement for readability.

Focus on: {', '.join(issues_to_fix)}

Text:
{content[:2000]}

For each example provide:
1. The problematic sentence or phrase
2. Why it's problematic
3. A better alternative

Provide JSON:
{{
    "improvements": [
        {{
            "type": "sentence|word|structure",
            "issue": "description",
            "example": "original text",
            "suggestion": "improved version",
            "priority": "high|medium|low"
        }}
    ]
}}"""
        
        response = await self.llm.complete(
            prompt,
            system_prompt="You are a professional editor focused on clarity and readability.",
            temperature=0.3
        )
        
        try:
            import json
            # Handle markdown code blocks
            content_str = response.content.strip()
            if content_str.startswith('```'):
                content_str = content_str.split('```')[1]
                if content_str.startswith('json'):
                    content_str = content_str[4:]
                content_str = content_str.rsplit('```', 1)[0]
            
            data = json.loads(content_str)
            for item in data.get('improvements', [])[:10]:
                improvements.append(ImprovementSuggestion(
                    type=item.get('type', 'sentence'),
                    issue=item.get('issue', ''),
                    example=item.get('example', ''),
                    suggestion=item.get('suggestion', ''),
                    priority=item.get('priority', 'medium')
                ))
        except:
            pass
        
        return improvements
    
    async def _generate_summary(
        self,
        metrics: ReadabilityMetrics,
        complexity: TextComplexity,
        accessibility: AccessibilityScore
    ) -> str:
        """Generate readability analysis summary"""
        
        level_desc = {
            ReadingLevel.VERY_EASY: "very easy to read (elementary level)",
            ReadingLevel.EASY: "easy to read (middle school level)",
            ReadingLevel.MODERATE: "moderately difficult (high school level)",
            ReadingLevel.DIFFICULT: "difficult (college level)",
            ReadingLevel.VERY_DIFFICULT: "very difficult (graduate level)"
        }
        
        summary = f"This content is {level_desc[metrics.reading_level]} with an average grade level of {metrics.average_grade_level:.1f}. "
        
        if metrics.flesch_reading_ease >= 70:
            summary += "It is easily understood by most readers. "
        elif metrics.flesch_reading_ease >= 50:
            summary += "It requires moderate reading skill. "
        else:
            summary += "It may be challenging for average readers. "
        
        summary += f"Accessibility: {accessibility.level.value.upper()} (score: {accessibility.score:.0f}/100)."
        
        return summary
    
    def _calculate_overall_score(
        self,
        metrics: ReadabilityMetrics,
        accessibility: AccessibilityScore
    ) -> float:
        """Calculate overall readability score (0-100)"""
        
        # Flesch Reading Ease is already 0-100
        readability_score = metrics.flesch_reading_ease
        
        # Accessibility score is 0-100
        accessibility_score = accessibility.score
        
        # Weighted average (60% readability, 40% accessibility)
        overall = (readability_score * 0.6) + (accessibility_score * 0.4)
        
        return overall
    
    async def quick_grade_level(self, content: str) -> float:
        """Quick grade level assessment without full analysis"""
        
        complexity = self._calculate_text_complexity(content)
        metrics = self._calculate_readability_metrics(content, complexity)
        
        return metrics.average_grade_level

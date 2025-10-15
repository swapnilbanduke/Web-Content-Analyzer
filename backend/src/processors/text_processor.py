"""
Text Processing Pipeline

Comprehensive text processing for cleaning HTML content, normalizing text,
handling special characters, detecting language, and preparing content for AI analysis.

Features:
- HTML tag removal and text extraction
- Whitespace normalization
- Special character handling
- Language detection
- Content summarization preparation
- Readability metrics
- Key sentence extraction
"""

import logging
import re
import html
import unicodedata
from typing import Dict, Any, List, Optional, Tuple
from collections import Counter
from bs4 import BeautifulSoup, NavigableString, Tag

logger = logging.getLogger(__name__)


# ============================================================================
# HTML Cleaning and Text Extraction
# ============================================================================

class HTMLCleaner:
    """
    Clean HTML content and extract text
    
    Features:
    - Remove scripts, styles, and unwanted tags
    - Preserve paragraph structure
    - Handle nested elements
    - Extract clean text
    """
    
    # Tags to remove completely (including content)
    REMOVE_TAGS = {
        'script', 'style', 'noscript', 'iframe', 'embed',
        'object', 'applet', 'canvas', 'svg', 'math'
    }
    
    # Tags that represent block elements (add newlines)
    BLOCK_TAGS = {
        'p', 'div', 'article', 'section', 'header', 'footer',
        'main', 'aside', 'nav', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'dl', 'dt', 'dd', 'table', 'tr', 'td', 'th',
        'blockquote', 'pre', 'form', 'fieldset', 'address', 'hr'
    }
    
    # Tags that should have space after (inline elements)
    INLINE_SPACE_TAGS = {'br', 'hr'}
    
    def __init__(
        self,
        preserve_structure: bool = True,
        remove_links: bool = False,
        remove_images: bool = False
    ):
        """
        Initialize HTML cleaner
        
        Args:
            preserve_structure: Preserve paragraph/block structure
            remove_links: Remove link tags (keep text)
            remove_images: Remove image tags
        """
        self.preserve_structure = preserve_structure
        self.remove_links = remove_links
        self.remove_images = remove_images
    
    def clean(self, html_content: str) -> str:
        """
        Clean HTML and extract text
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Cleaned text
        """
        if not html_content:
            return ""
        
        try:
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted tags
            self._remove_unwanted_tags(soup)
            
            # Remove links if requested
            if self.remove_links:
                for tag in soup.find_all('a'):
                    tag.unwrap()
            
            # Remove images if requested
            if self.remove_images:
                for tag in soup.find_all('img'):
                    tag.decompose()
            
            # Extract text
            if self.preserve_structure:
                text = self._extract_text_structured(soup)
            else:
                text = soup.get_text()
            
            return text
        except Exception as e:
            logger.error(f"HTML cleaning error: {e}")
            return html_content
    
    def _remove_unwanted_tags(self, soup: BeautifulSoup) -> None:
        """Remove unwanted tags from soup"""
        for tag_name in self.REMOVE_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()
    
    def _extract_text_structured(self, soup: BeautifulSoup) -> str:
        """
        Extract text while preserving structure
        
        Adds newlines for block elements
        """
        text_parts = []
        
        for element in soup.descendants:
            if isinstance(element, NavigableString):
                text = str(element).strip()
                if text:
                    text_parts.append(text)
            elif isinstance(element, Tag):
                if element.name in self.BLOCK_TAGS:
                    # Add newline after block elements
                    if text_parts and text_parts[-1] != '\n':
                        text_parts.append('\n')
                elif element.name in self.INLINE_SPACE_TAGS:
                    # Add space after inline space elements
                    text_parts.append(' ')
        
        return ''.join(text_parts)
    
    def remove_html_comments(self, html_content: str) -> str:
        """Remove HTML comments"""
        return re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    
    def remove_html_entities(self, text: str) -> str:
        """Convert HTML entities to characters"""
        return html.unescape(text)


# ============================================================================
# Text Normalization
# ============================================================================

class TextNormalizer:
    """
    Normalize text formatting
    
    Features:
    - Whitespace normalization
    - Line break handling
    - Quote normalization
    - Text cleanup
    """
    
    # Smart quotes mapping
    QUOTE_MAPPING = {
        '"': '"',  # Left double quote
        '"': '"',  # Right double quote
        ''': "'",  # Left single quote
        ''': "'",  # Right single quote
        '«': '"',  # Left double angle quote
        '»': '"',  # Right double angle quote
        '‹': "'",  # Left single angle quote
        '›': "'",  # Right single angle quote
    }
    
    # Dash mapping
    DASH_MAPPING = {
        '—': '-',  # Em dash
        '–': '-',  # En dash
        '−': '-',  # Minus sign
    }
    
    def __init__(
        self,
        normalize_whitespace: bool = True,
        normalize_quotes: bool = True,
        normalize_dashes: bool = True,
        max_consecutive_newlines: int = 2
    ):
        """
        Initialize text normalizer
        
        Args:
            normalize_whitespace: Normalize whitespace
            normalize_quotes: Convert smart quotes to straight quotes
            normalize_dashes: Convert various dashes to hyphens
            max_consecutive_newlines: Maximum consecutive newlines
        """
        self.normalize_whitespace = normalize_whitespace
        self.normalize_quotes = normalize_quotes
        self.normalize_dashes = normalize_dashes
        self.max_consecutive_newlines = max_consecutive_newlines
    
    def normalize(self, text: str) -> str:
        """
        Normalize text
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        try:
            # Normalize whitespace
            if self.normalize_whitespace:
                text = self._normalize_whitespace(text)
            
            # Normalize quotes
            if self.normalize_quotes:
                text = self._normalize_quotes(text)
            
            # Normalize dashes
            if self.normalize_dashes:
                text = self._normalize_dashes(text)
            
            # Limit consecutive newlines
            text = self._limit_newlines(text)
            
            # Remove leading/trailing whitespace
            text = text.strip()
            
            return text
        except Exception as e:
            logger.error(f"Text normalization error: {e}")
            return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace"""
        # Replace tabs with spaces
        text = text.replace('\t', ' ')
        
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Remove spaces at line start/end
        lines = text.split('\n')
        lines = [line.strip() for line in lines]
        text = '\n'.join(lines)
        
        return text
    
    def _normalize_quotes(self, text: str) -> str:
        """Normalize quotes"""
        for smart, straight in self.QUOTE_MAPPING.items():
            text = text.replace(smart, straight)
        return text
    
    def _normalize_dashes(self, text: str) -> str:
        """Normalize dashes"""
        for dash, hyphen in self.DASH_MAPPING.items():
            text = text.replace(dash, hyphen)
        return text
    
    def _limit_newlines(self, text: str) -> str:
        """Limit consecutive newlines"""
        pattern = r'\n{' + str(self.max_consecutive_newlines + 1) + r',}'
        replacement = '\n' * self.max_consecutive_newlines
        return re.sub(pattern, replacement, text)
    
    def remove_urls(self, text: str) -> str:
        """Remove URLs from text"""
        url_pattern = r'https?://\S+|www\.\S+'
        return re.sub(url_pattern, '', text)
    
    def remove_emails(self, text: str) -> str:
        """Remove email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.sub(email_pattern, '', text)


# ============================================================================
# Special Character Handling
# ============================================================================

class SpecialCharacterHandler:
    """
    Handle special characters and Unicode
    
    Features:
    - Unicode normalization
    - Emoji handling
    - Special character cleanup
    - Character encoding fixes
    """
    
    def __init__(
        self,
        unicode_form: str = 'NFKC',
        remove_emojis: bool = False,
        remove_control_chars: bool = True,
        ascii_only: bool = False
    ):
        """
        Initialize special character handler
        
        Args:
            unicode_form: Unicode normalization form (NFC, NFKC, NFD, NFKD)
            remove_emojis: Remove emoji characters
            remove_control_chars: Remove control characters
            ascii_only: Keep only ASCII characters
        """
        self.unicode_form = unicode_form
        self.remove_emojis = remove_emojis
        self.remove_control_chars = remove_control_chars
        self.ascii_only = ascii_only
    
    def handle(self, text: str) -> str:
        """
        Handle special characters
        
        Args:
            text: Input text
            
        Returns:
            Processed text
        """
        if not text:
            return ""
        
        try:
            # Unicode normalization
            text = unicodedata.normalize(self.unicode_form, text)
            
            # Remove control characters
            if self.remove_control_chars:
                text = self._remove_control_chars(text)
            
            # Remove emojis
            if self.remove_emojis:
                text = self._remove_emojis(text)
            
            # ASCII only
            if self.ascii_only:
                text = self._to_ascii(text)
            
            return text
        except Exception as e:
            logger.error(f"Special character handling error: {e}")
            return text
    
    def _remove_control_chars(self, text: str) -> str:
        """Remove control characters"""
        # Keep newline, tab, and carriage return
        return ''.join(
            char for char in text
            if unicodedata.category(char)[0] != 'C' or char in '\n\t\r'
        )
    
    def _remove_emojis(self, text: str) -> str:
        """Remove emoji characters"""
        # Emoji pattern (basic)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.sub('', text)
    
    def _to_ascii(self, text: str) -> str:
        """Convert to ASCII (remove non-ASCII characters)"""
        return text.encode('ascii', 'ignore').decode('ascii')
    
    def remove_zero_width_chars(self, text: str) -> str:
        """Remove zero-width characters"""
        zero_width = [
            '\u200b',  # Zero width space
            '\u200c',  # Zero width non-joiner
            '\u200d',  # Zero width joiner
            '\ufeff',  # Zero width no-break space
        ]
        for char in zero_width:
            text = text.replace(char, '')
        return text


# ============================================================================
# Language Detection
# ============================================================================

class LanguageDetector:
    """
    Detect text language
    
    Features:
    - Multiple detection methods
    - Confidence scoring
    - Common language patterns
    - Fallback detection
    """
    
    # Common words by language (for simple detection)
    COMMON_WORDS = {
        'en': {'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'as', 'are', 'was', 'were', 'be', 'been'},
        'es': {'el', 'la', 'de', 'que', 'y', 'es', 'en', 'un', 'por', 'con', 'para', 'una', 'los', 'las'},
        'fr': {'le', 'de', 'un', 'être', 'et', 'à', 'il', 'avoir', 'ne', 'je', 'son', 'que', 'se', 'la'},
        'de': {'der', 'die', 'das', 'und', 'in', 'von', 'zu', 'den', 'mit', 'ist', 'im', 'nicht', 'ein'},
        'it': {'il', 'di', 'e', 'la', 'che', 'per', 'un', 'in', 'è', 'a', 'con', 'del', 'si', 'non'},
        'pt': {'o', 'de', 'a', 'e', 'é', 'do', 'da', 'em', 'um', 'para', 'com', 'não', 'os', 'uma'},
    }
    
    def __init__(self, default_language: str = 'en'):
        """
        Initialize language detector
        
        Args:
            default_language: Default language code
        """
        self.default_language = default_language
    
    def detect(self, text: str) -> Dict[str, Any]:
        """
        Detect language
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with language code and confidence
        """
        if not text or len(text.strip()) < 10:
            return {
                'language': self.default_language,
                'confidence': 0.0,
                'method': 'default'
            }
        
        # Try word-based detection
        result = self._detect_by_common_words(text)
        
        return result
    
    def _detect_by_common_words(self, text: str) -> Dict[str, Any]:
        """Detect language by counting common words"""
        # Tokenize
        words = re.findall(r'\b\w+\b', text.lower())
        
        if not words:
            return {
                'language': self.default_language,
                'confidence': 0.0,
                'method': 'default'
            }
        
        # Count matches for each language
        scores = {}
        for lang, common_words in self.COMMON_WORDS.items():
            matches = sum(1 for word in words if word in common_words)
            scores[lang] = matches / len(words)
        
        # Get best match
        if scores:
            best_lang = max(scores, key=scores.get)
            confidence = scores[best_lang]
            
            # Require minimum confidence
            if confidence < 0.01:
                return {
                    'language': self.default_language,
                    'confidence': 0.0,
                    'method': 'default'
                }
            
            return {
                'language': best_lang,
                'confidence': confidence,
                'method': 'common_words',
                'scores': scores
            }
        
        return {
            'language': self.default_language,
            'confidence': 0.0,
            'method': 'default'
        }


# ============================================================================
# Content Summarization Preparation
# ============================================================================

class SummarizationPrep:
    """
    Prepare content for summarization and AI analysis
    
    Features:
    - Key sentence extraction
    - Important section identification
    - Readability metrics
    - Content structure analysis
    """
    
    def __init__(self):
        """Initialize summarization prep"""
        pass
    
    def prepare(self, text: str) -> Dict[str, Any]:
        """
        Prepare content for summarization
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with prepared content and metrics
        """
        if not text:
            return {
                'text': '',
                'sentences': [],
                'paragraphs': [],
                'key_sentences': [],
                'metrics': {}
            }
        
        try:
            # Split into sentences and paragraphs
            sentences = self._split_sentences(text)
            paragraphs = self._split_paragraphs(text)
            
            # Extract key sentences
            key_sentences = self._extract_key_sentences(sentences)
            
            # Calculate metrics
            metrics = self._calculate_metrics(text, sentences, paragraphs)
            
            return {
                'text': text,
                'sentences': sentences,
                'paragraphs': paragraphs,
                'key_sentences': key_sentences,
                'metrics': metrics
            }
        except Exception as e:
            logger.error(f"Summarization prep error: {e}")
            return {
                'text': text,
                'sentences': [],
                'paragraphs': [],
                'key_sentences': [],
                'metrics': {}
            }
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting (can be improved with NLTK)
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        paragraphs = re.split(r'\n\n+', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _extract_key_sentences(self, sentences: List[str], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Extract key sentences based on various metrics
        
        Args:
            sentences: List of sentences
            top_n: Number of top sentences to return
            
        Returns:
            List of key sentences with scores
        """
        if not sentences:
            return []
        
        scored_sentences = []
        
        for i, sentence in enumerate(sentences):
            score = self._score_sentence(sentence, i, len(sentences))
            scored_sentences.append({
                'text': sentence,
                'position': i,
                'score': score
            })
        
        # Sort by score and return top N
        scored_sentences.sort(key=lambda x: x['score'], reverse=True)
        return scored_sentences[:top_n]
    
    def _score_sentence(self, sentence: str, position: int, total: int) -> float:
        """
        Score sentence importance
        
        Factors:
        - Position (first and last sentences often important)
        - Length (very short or very long sentences less important)
        - Keywords (sentences with certain keywords more important)
        """
        score = 0.0
        
        # Position score (first and last sentences)
        if position == 0:
            score += 2.0
        elif position < total * 0.2:  # First 20%
            score += 1.0
        elif position > total * 0.8:  # Last 20%
            score += 0.5
        
        # Length score (prefer medium-length sentences)
        words = len(sentence.split())
        if 10 <= words <= 30:
            score += 1.0
        elif 5 <= words < 10 or 30 < words <= 50:
            score += 0.5
        
        # Keyword score (basic)
        keywords = ['important', 'significant', 'key', 'main', 'essential', 'critical', 'conclusion', 'summary']
        for keyword in keywords:
            if keyword in sentence.lower():
                score += 0.5
        
        return score
    
    def _calculate_metrics(
        self,
        text: str,
        sentences: List[str],
        paragraphs: List[str]
    ) -> Dict[str, Any]:
        """Calculate readability and content metrics"""
        words = text.split()
        
        metrics = {
            'character_count': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'paragraph_count': len(paragraphs),
            'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            'avg_paragraph_length': len(sentences) / len(paragraphs) if paragraphs else 0,
        }
        
        # Flesch Reading Ease (simplified)
        if sentences and words:
            syllables = sum(self._count_syllables(w) for w in words)
            metrics['flesch_reading_ease'] = round(
                206.835
                - 1.015 * (len(words) / len(sentences))
                - 84.6 * (syllables / len(words)),
                2
            )
        else:
            metrics['flesch_reading_ease'] = 0
        
        return metrics
    
    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count (simplified)"""
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
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        # Ensure at least 1 syllable
        if syllable_count == 0:
            syllable_count = 1
        
        return syllable_count


# ============================================================================
# Main Text Processor (Enhanced)
# ============================================================================

class TextProcessor:
    """
    Main text processing pipeline
    
    Orchestrates all text processing steps:
    1. HTML cleaning
    2. Text normalization
    3. Special character handling
    4. Language detection
    5. Summarization preparation
    6. Statistical analysis
    """
    
    def __init__(
        self,
        clean_html: bool = True,
        normalize_text: bool = True,
        handle_special_chars: bool = True,
        detect_language: bool = True,
        prepare_summary: bool = True,
        **kwargs
    ):
        """
        Initialize text processor
        
        Args:
            clean_html: Enable HTML cleaning
            normalize_text: Enable text normalization
            handle_special_chars: Enable special character handling
            detect_language: Enable language detection
            prepare_summary: Enable summarization preparation
            **kwargs: Additional configuration options
        """
        self.clean_html_enabled = clean_html
        self.normalize_text_enabled = normalize_text
        self.handle_special_chars_enabled = handle_special_chars
        self.detect_language_enabled = detect_language
        self.prepare_summary_enabled = prepare_summary
        
        # Initialize components
        self.html_cleaner = HTMLCleaner(**kwargs.get('html_cleaner', {}))
        self.text_normalizer = TextNormalizer(**kwargs.get('text_normalizer', {}))
        self.char_handler = SpecialCharacterHandler(**kwargs.get('char_handler', {}))
        self.lang_detector = LanguageDetector(**kwargs.get('lang_detector', {}))
        self.summary_prep = SummarizationPrep()
    
    def process(self, content: str, is_html: bool = True) -> Dict[str, Any]:
        """
        Process content through the comprehensive pipeline
        
        Args:
            content: Input content (HTML or plain text)
            is_html: Whether content is HTML
            
        Returns:
            Dictionary with processed content and metadata
        """
        if not content:
            return self._empty_result()
        
        try:
            result = {
                'original_length': len(content),
                'steps_applied': []
            }
            
            # Step 1: HTML cleaning
            if is_html and self.clean_html_enabled:
                content = self.html_cleaner.clean(content)
                result['steps_applied'].append('html_cleaning')
                logger.info(f"HTML cleaned: {len(content)} characters")
            
            # Step 2: Text normalization
            if self.normalize_text_enabled:
                content = self.text_normalizer.normalize(content)
                result['steps_applied'].append('text_normalization')
                logger.info(f"Text normalized: {len(content)} characters")
            
            # Step 3: Special character handling
            if self.handle_special_chars_enabled:
                content = self.char_handler.handle(content)
                result['steps_applied'].append('special_char_handling')
                logger.info(f"Special chars handled: {len(content)} characters")
            
            result['processed_text'] = content
            result['processed_length'] = len(content)
            
            # Step 4: Language detection
            if self.detect_language_enabled:
                lang_result = self.lang_detector.detect(content)
                result['language'] = lang_result
                result['steps_applied'].append('language_detection')
                logger.info(f"Language detected: {lang_result['language']}")
            
            # Step 5: Summarization preparation
            if self.prepare_summary_enabled:
                summary_data = self.summary_prep.prepare(content)
                result['summary_data'] = summary_data
                result['steps_applied'].append('summarization_prep')
                logger.info(f"Summary prepared")
            
            # Step 6: Enhanced statistics (legacy compatibility)
            result.update(self._calculate_statistics(content))
            
            return result
            
        except Exception as e:
            logger.error(f"Text processing error: {str(e)}")
            return self._empty_result()
    
    def process_batch(self, contents: List[str], is_html: bool = True) -> List[Dict[str, Any]]:
        """
        Process multiple contents
        
        Args:
            contents: List of content strings
            is_html: Whether contents are HTML
            
        Returns:
            List of processing results
        """
        return [self.process(content, is_html) for content in contents]
    
    def _calculate_statistics(self, text: str) -> Dict[str, Any]:
        """
        Calculate text statistics (legacy compatibility)
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with statistics
        """
        return {
            "word_count": self._count_words(text),
            "sentence_count": self._count_sentences(text),
            "paragraph_count": self._count_paragraphs(text),
            "character_count": len(text),
            "reading_time": self._estimate_reading_time(text),
            "readability_score": self._calculate_readability(text),
            "keywords": self._extract_keywords(text),
            "avg_word_length": self._avg_word_length(text),
            "avg_sentence_length": self._avg_sentence_length(text)
        }
    
    def _count_words(self, text: str) -> int:
        """Count words in text"""
        words = re.findall(r'\b\w+\b', text)
        return len(words)
    
    def _count_sentences(self, text: str) -> int:
        """Count sentences in text"""
        sentences = re.split(r'[.!?]+', text)
        return len([s for s in sentences if s.strip()])
    
    def _count_paragraphs(self, text: str) -> int:
        """Count paragraphs in text"""
        paragraphs = re.split(r'\n\n+', text)
        return len([p for p in paragraphs if p.strip()])
    
    def _estimate_reading_time(self, text: str) -> float:
        """
        Estimate reading time in minutes (assuming 200 words per minute)
        """
        words = self._count_words(text)
        return round(words / 200, 1)
    
    def _calculate_readability(self, text: str) -> float:
        """
        Calculate readability score (simplified Flesch Reading Ease)
        Score: 0-100, higher is easier to read
        """
        words = self._count_words(text)
        sentences = self._count_sentences(text)
        
        if sentences == 0 or words == 0:
            return 0.0
        
        # Count syllables (simplified: count vowel groups)
        syllables = len(re.findall(r'[aeiouAEIOU]+', text))
        
        # Flesch Reading Ease formula (simplified)
        avg_sentence_length = words / sentences
        avg_syllables_per_word = syllables / words
        
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Clamp between 0 and 100
        return max(0, min(100, round(score, 2)))
    
    def _extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract top keywords from text
        """
        # Simple keyword extraction based on word frequency
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out short words and common stopwords
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'is', 'was', 'are', 'be', 'been', 'being', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you',
            'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where',
            'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
            'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
            'so', 'than', 'too', 'very', 'just', 'from', 'by', 'about', 'into',
            'through', 'during', 'before', 'after', 'above', 'below', 'between'
        }
        
        filtered_words = [
            word for word in words 
            if len(word) > 3 and word not in stopwords
        ]
        
        # Get top N most common words
        word_freq = Counter(filtered_words)
        return [word for word, _ in word_freq.most_common(top_n)]
    
    def _avg_word_length(self, text: str) -> float:
        """Calculate average word length"""
        words = re.findall(r'\b\w+\b', text)
        if not words:
            return 0.0
        total_length = sum(len(word) for word in words)
        return round(total_length / len(words), 2)
    
    def _avg_sentence_length(self, text: str) -> float:
        """Calculate average sentence length in words"""
        words = self._count_words(text)
        sentences = self._count_sentences(text)
        if sentences == 0:
            return 0.0
        return round(words / sentences, 2)
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure"""
        return {
            "original_length": 0,
            "processed_length": 0,
            "processed_text": "",
            "steps_applied": [],
            "word_count": 0,
            "sentence_count": 0,
            "paragraph_count": 0,
            "character_count": 0,
            "reading_time": 0,
            "readability_score": 0,
            "keywords": [],
            "language": {
                "language": "unknown",
                "confidence": 0.0,
                "method": "default"
            },
            "avg_word_length": 0,
            "avg_sentence_length": 0,
            "summary_data": {
                "text": "",
                "sentences": [],
                "paragraphs": [],
                "key_sentences": [],
                "metrics": {}
            }
        }


__all__ = [
    'HTMLCleaner',
    'TextNormalizer',
    'SpecialCharacterHandler',
    'LanguageDetector',
    'SummarizationPrep',
    'TextProcessor',
]

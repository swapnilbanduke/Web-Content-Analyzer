"""
Test Services
"""
import pytest
from src.processors.text_processor import TextProcessor
from src.processors.content_cleaner import ContentCleaner
from src.utils.validators import URLValidator


def test_text_processor_word_count():
    """Test word count in text processor"""
    processor = TextProcessor()
    text = "This is a test sentence with seven words."
    result = processor.process(text)
    assert result["word_count"] == 8


def test_text_processor_empty_text():
    """Test text processor with empty text"""
    processor = TextProcessor()
    result = processor.process("")
    assert result["word_count"] == 0
    assert result["sentence_count"] == 0


def test_content_cleaner():
    """Test content cleaner"""
    cleaner = ContentCleaner()
    text = "This  has   extra    spaces"
    cleaned = cleaner.clean(text)
    assert "  " not in cleaned


def test_url_validator_valid():
    """Test URL validator with valid URL"""
    assert URLValidator.is_valid_url("https://example.com") == True
    assert URLValidator.is_valid_url("http://example.com") == True


def test_url_validator_invalid():
    """Test URL validator with invalid URLs"""
    assert URLValidator.is_valid_url("not-a-url") == False
    assert URLValidator.is_valid_url("javascript:alert(1)") == False
    assert URLValidator.is_valid_url("") == False

"""
tests/test_preprocessing.py
───────────────────────────
Unit tests for text cleaning and NLP preprocessing.
"""

from core.preprocessing import clean_text, preprocess_text


def test_clean_text_removes_punctuation():
    raw = "Hello, World! Great product... 100% recommended :)"
    cleaned = clean_text(raw)
    assert "!" not in cleaned
    assert "," not in cleaned
    assert "%" not in cleaned
    assert "hello world" in cleaned


def test_clean_text_empty_input():
    assert clean_text("") == ""
    assert clean_text(None) == ""


def test_preprocess_text_tokenizes_and_lemmatizes():
    text = "The batteries were lasting very long and were fantastic!"
    tokens = preprocess_text(text)

    # Stop words like 'the', 'were', 'very', 'and' should be removed
    assert "the" not in tokens
    assert "were" not in tokens
    assert "and" not in tokens

    # 'batteries' should be lemmatized to base form 'battery'
    assert "battery" in tokens

    # 'fantastic' should be retained as an informative keyword
    assert "fantastic" in tokens


def test_preprocess_text_empty():
    assert preprocess_text("") == []

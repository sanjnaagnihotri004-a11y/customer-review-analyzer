"""
tests/test_sentiment.py
────────────────────────
Unit tests for sentiment classification and scoring.
"""

from core.sentiment import classify_words, analyze_sentiment


def test_classify_words():
    words = ["good", "great", "bad", "terrible", "laptop"]
    pos, neg = classify_words(words)

    assert "good" in pos
    assert "great" in pos
    assert "bad" in neg
    assert "terrible" in neg
    assert "laptop" not in pos
    assert "laptop" not in neg


def test_analyze_sentiment_positive():
    tokens = ["great", "awesome", "product"]
    result = analyze_sentiment(tokens)

    assert result["label"] == "Positive"
    assert result["positive_count"] == 2
    assert result["negative_count"] == 0
    assert result["score"] == 2


def test_analyze_sentiment_negative():
    tokens = ["terrible", "awful", "defect", "screen"]
    result = analyze_sentiment(tokens)

    assert result["label"] == "Negative"
    assert result["score"] < 0
    assert result["negative_count"] >= 2


def test_analyze_sentiment_neutral():
    tokens = ["laptop", "phone", "device"]
    result = analyze_sentiment(tokens)

    assert result["label"] == "Neutral"
    assert result["score"] == 0
    assert result["positive_count"] == 0
    assert result["negative_count"] == 0

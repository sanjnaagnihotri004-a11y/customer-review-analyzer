"""
core/sentiment.py
─────────────────
Handles sentiment classification, polarity scoring, and keyword extraction.

WHAT THIS MODULE DOES:
  1. Downloads and loads the NLTK Opinion Lexicon (curated lists of positive and negative English words).
  2. Classifies extracted words into positive and negative sets.
  3. Computes sentiment summary statistics (counts, scores, overall sentiment label).
"""

from typing import List, Dict, Tuple, Any
import nltk
from nltk.corpus import opinion_lexicon

# Download the opinion lexicon quietly if it isn't downloaded yet
nltk.download("opinion_lexicon", quiet=True)

# Load the positive and negative word sets into memory for O(1) fast lookup
POSITIVE_WORDS = set(opinion_lexicon.positive())
NEGATIVE_WORDS = set(opinion_lexicon.negative())


def classify_words(words: List[str]) -> Tuple[List[str], List[str]]:
    """
    Separates a list of words into positive and negative matches.

    Returns:
        (positive_words_list, negative_words_list)
    """
    pos = [w for w in words if w in POSITIVE_WORDS]
    neg = [w for w in words if w in NEGATIVE_WORDS]
    return pos, neg


def analyze_sentiment(words: List[str]) -> Dict[str, Any]:
    """
    Computes a complete sentiment report from a list of tokens.

    Returns a dictionary containing:
      - positive_words: list of detected positive words
      - negative_words: list of detected negative words
      - positive_count: number of positive words
      - negative_count: number of negative words
      - score: net score (positive - negative)
      - label: "Positive", "Negative", or "Neutral"
    """
    pos_words, neg_words = classify_words(words)
    pos_count = len(pos_words)
    neg_count = len(neg_words)
    score = pos_count - neg_count

    if score > 0:
        label = "Positive"
    elif score < 0:
        label = "Negative"
    else:
        label = "Neutral"

    return {
        "positive_words": pos_words,
        "negative_words": neg_words,
        "positive_count": pos_count,
        "negative_count": neg_count,
        "score": score,
        "label": label,
    }

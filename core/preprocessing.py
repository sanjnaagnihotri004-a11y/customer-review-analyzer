"""
core/preprocessing.py
─────────────────────
Handles text cleaning, tokenization, and lemmatization.

WHAT THIS MODULE DOES:
  1. Cleans raw review text (removes punctuation, symbols).
  2. Uses spaCy to tokenize the sentence into individual words.
  3. Filters out 'stop words' (words like 'is', 'the', 'and' that add no sentiment).
  4. Lemmatizes words (converts them to base form, e.g., 'loved' -> 'love').
"""

import re
from typing import List
import spacy

# Load the spaCy English pipeline once when this module is imported.
# spaCy is an industry-standard NLP library used for fast linguistic processing.
nlp = spacy.load("en_core_web_sm")


def clean_text(text: str) -> str:
    """
    Remove non-alphanumeric characters (punctuation, emojis) and convert to lowercase.

    Example:
        clean_text("Great phone! 10/10") -> "great phone 1010"
    """
    if not text:
        return ""
    # [^\w\s] matches any character that is NOT a word character or whitespace
    return re.sub(r"[^\w\s]", "", text.lower()).strip()


def preprocess_text(text: str) -> List[str]:
    """
    Takes raw review text and returns a list of cleaned, lemmatized tokens.

    Steps:
      1. Clean text (remove punctuation, lowercase).
      2. Run through spaCy pipeline.
      3. Filter out stop words (like 'the', 'is') and non-alphabetic tokens.
      4. Extract base lemma for each word.

    Example:
        preprocess_text("The batteries were lasting long and amazing!")
        -> ['battery', 'last', 'long', 'amazing']
    """
    cleaned = clean_text(text)
    if not cleaned:
        return []

    doc = nlp(cleaned)
    lemmas = [
        token.lemma_
        for token in doc
        if not token.is_stop and token.is_alpha
    ]
    return lemmas

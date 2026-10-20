"""
models/review.py
────────────────
Defines the "reviews" table in the database.

Each row in this table represents one customer review
that a user submitted for analysis.

COLUMNS:
  - id         : Unique number for each review (auto-generated).
  - user_id    : Which user submitted this review (links to users.id).
  - raw_text   : The original review text the user typed in.
  - sentiment  : The analysis results stored as JSON, e.g.:
                 {"positive": ["good", "great"], "negative": ["bad"]}
  - created_at : When the review was submitted (auto-filled by the database).

WHY WE NEED THIS:
  In the college version, analysis results disappeared when the page
  was refreshed. Now every review is saved permanently, so users can:
  - View their past analyses.
  - Build a history of reviews over time.
  - Export data for reports.
"""

from sqlalchemy import Column, Integer, Text, DateTime, func, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Review(Base):
    # The name of the table in PostgreSQL
    __tablename__ = "reviews"

    # --- COLUMNS ---

    # Primary key — unique ID for each review
    id = Column(Integer, primary_key=True, index=True)

    # Which user submitted this review.
    # In a full app, this would be a ForeignKey pointing to users.id.
    # For now, we keep it simple as just an integer.
    user_id = Column(Integer, nullable=False)

    # The original review text, exactly as the user typed it.
    # "Text" (capital T) allows unlimited length, unlike String(255).
    raw_text = Column(Text, nullable=False)

    # The sentiment analysis results, stored as a JSON object.
    # Example: {"positive": ["good", "love"], "negative": ["bad"]}
    # JSON columns let us store structured data without creating
    # separate tables for positive/negative words.
    sentiment = Column(JSON)

    # When this review was created.
    # "server_default=func.now()" tells PostgreSQL to automatically
    # fill in the current date and time when a new row is inserted.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

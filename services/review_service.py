"""
services/review_service.py
──────────────────────────
Database operations for customer reviews.

WHAT THIS MODULE DOES:
  1. Saves an analyzed customer review and its sentiment JSON to PostgreSQL.
  2. Fetches the review history for a specific logged-in user.
  3. Provides review deletion if needed.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.review import Review
from core.logger import logger


def create_review(
    db: Session,
    user_id: int,
    raw_text: str,
    sentiment_data: Dict[str, Any],
) -> Review:
    """
    Saves a newly analyzed review into the database.

    Args:
        db: Active SQLAlchemy database session.
        user_id: The ID of the authenticated user.
        raw_text: The review text submitted by the user.
        sentiment_data: Dictionary containing sentiment stats (e.g. positive/negative words, score, label).

    Returns:
        The newly created Review model instance.
    """
    review = Review(
        user_id=user_id,
        raw_text=raw_text,
        sentiment=sentiment_data,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    logger.info(f"Saved review #{review.id} for user {user_id} (Sentiment: {sentiment_data.get('label')}, Score: {sentiment_data.get('score')})")
    return review


def get_user_reviews(
    db: Session,
    user_id: int,
    limit: int = 50,
) -> List[Review]:
    """
    Retrieves the most recent reviews submitted by a user, newest first.

    Args:
        db: Active SQLAlchemy database session.
        user_id: The ID of the user whose reviews we want to view.
        limit: Maximum number of reviews to return.

    Returns:
        List of Review instances ordered by created_at descending.
    """
    return (
        db.query(Review)
        .filter(Review.user_id == user_id)
        .order_by(desc(Review.created_at))
        .limit(limit)
        .all()
    )


def delete_review(
    db: Session,
    review_id: int,
    user_id: int,
) -> bool:
    """
    Deletes a review belonging to a specific user.

    Returns True if deleted, False if not found or unauthorized.
    """
    review = (
        db.query(Review)
        .filter(Review.id == review_id, Review.user_id == user_id)
        .first()
    )
    if not review:
        return False
    db.delete(review)
    db.commit()
    return True

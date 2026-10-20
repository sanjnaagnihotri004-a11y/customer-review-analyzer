"""
services/db.py
──────────────
Handles the connection between our Python app and PostgreSQL.

THREE THINGS THIS FILE DOES:

1. Creates an "engine" — the bridge between Python and PostgreSQL.
   Think of it as the phone line that connects your app to the database.

2. Provides a "SessionLocal" — a factory that creates new sessions
   (individual phone calls) whenever the app needs to talk to the DB.

3. Provides an "init_db()" function — run this ONCE to create all
   the tables (users, reviews) inside PostgreSQL.

HOW TO USE:
    from services.db import SessionLocal, init_db

    # Create the tables (run once at startup):
    init_db()

    # Talk to the database:
    db = SessionLocal()
    db.add(some_object)
    db.commit()
    db.close()
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from core.config import settings
from models.user import Base as UserBase
from models.review import Base as ReviewBase


# ──────────────────────────────────────────────
# 1. Create the ENGINE
# ──────────────────────────────────────────────
# The engine reads the DATABASE_URL from our .env file
# (via core/config.py) and establishes the connection.
#
# "echo=False" means don't print every SQL command to the terminal.
# Set it to True if you want to see what SQL is being run (useful
# for debugging).
engine = create_engine(settings.database_url, echo=False, future=True)


# ──────────────────────────────────────────────
# 2. Create the SESSION FACTORY
# ──────────────────────────────────────────────
# "sessionmaker" creates a class that, when called, gives us
# a new database session.
#
# "scoped_session" makes it thread-safe — if multiple users
# hit the app at the same time, each gets their own session.
#
# "autocommit=False" means changes are NOT saved until we
# explicitly call db.commit(). This prevents accidental writes.
#
# "autoflush=False" means SQLAlchemy won't automatically send
# pending changes to the DB — we control when that happens.
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


# ──────────────────────────────────────────────
# 3. Create all tables (run once)
# ──────────────────────────────────────────────
def init_db():
    """
    Looks at all the models (User, Review) and creates
    the corresponding tables in PostgreSQL if they don't
    already exist.

    Safe to call multiple times — it won't delete existing data.
    """
    UserBase.metadata.create_all(bind=engine)
    ReviewBase.metadata.create_all(bind=engine)


# ──────────────────────────────────────────────
# 4. Helper to get a session (and auto-close it)
# ──────────────────────────────────────────────
def get_db():
    """
    A generator that provides a database session and
    ensures it is closed after use.

    Usage:
        for db in get_db():
            db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

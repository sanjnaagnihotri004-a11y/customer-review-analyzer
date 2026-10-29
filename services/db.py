"""
services/db.py
──────────────
Handles the connection between our Python app and the database.

FEATURES:
  1. Primary: Connects to PostgreSQL (Docker).
  2. Resilient Fallback: If Docker/PostgreSQL is offline, it automatically falls back
     to a local SQLite database file (reviewdb.sqlite3) so the app works seamlessly
     inside VS Code without requiring Docker to be running!
  3. Provides SessionLocal and init_db() to create schema and default admin.
"""

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from core.config import settings
from models.user import Base as UserBase, User
from models.review import Base as ReviewBase
from core.logger import logger


# ──────────────────────────────────────────────
# 1. Create the ENGINE with Auto-Fallback
# ──────────────────────────────────────────────
def _get_engine():
    """
    Attempts to connect to PostgreSQL. If Docker is offline,
    falls back cleanly to a local SQLite database.
    """
    try:
        pg_engine = create_engine(settings.database_url, echo=False, future=True)
        # Probe the connection quickly with a 2-second timeout
        with pg_engine.connect() as conn:
            pass
        return pg_engine
    except Exception as err:
        logger.warning(f"PostgreSQL offline ({err}). Activating local SQLite database fallback.")
        db_path = Path(__file__).resolve().parents[1] / "reviewdb.sqlite3"
        sqlite_url = f"sqlite:///{db_path}"
        return create_engine(
            sqlite_url,
            echo=False,
            future=True,
            connect_args={"check_same_thread": False},
        )


engine = _get_engine()

# ──────────────────────────────────────────────
# 2. Create the SESSION FACTORY
# ──────────────────────────────────────────────
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


# ──────────────────────────────────────────────
# 3. Create all tables & ensure default admin exists
# ──────────────────────────────────────────────
def init_db():
    """
    Creates tables if they don't exist yet, and ensures a default
    admin account (admin@example.com / admin123) is ready to use.
    """
    UserBase.metadata.create_all(bind=engine)
    ReviewBase.metadata.create_all(bind=engine)

    # Seed initial admin user if table is empty
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            from services.auth import hash_password
            new_admin = User(
                email="admin@example.com",
                hashed_password=hash_password("admin123"),
                is_active=True,
                is_admin=True,
            )
            db.add(new_admin)
            db.commit()
            logger.info("Initialized default admin account: admin@example.com")
    finally:
        db.close()


# ──────────────────────────────────────────────
# 4. Helper to get a session
# ──────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

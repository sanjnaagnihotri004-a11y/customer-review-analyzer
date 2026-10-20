"""
models/user.py
──────────────
Defines the "users" table in the database.

Each row in this table represents one registered user.

COLUMNS:
  - id              : A unique number assigned automatically (1, 2, 3…).
  - email           : The user's email address (must be unique — no duplicates).
  - hashed_password : The user's password, stored as a hash (never plain text).
  - is_active       : Whether the account is enabled (True) or disabled (False).
  - is_admin        : Whether the user has admin privileges.

WHY WE NEED THIS:
  We're adding authentication (login/logout) to the app.
  This table stores the credentials that streamlit-authenticator
  will check when a user tries to log in.
"""

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base

# "Base" is the foundation class that all models inherit from.
# SQLAlchemy uses it to keep track of all the tables you define.
Base = declarative_base()


class User(Base):
    # The name of the table in PostgreSQL
    __tablename__ = "users"

    # --- COLUMNS ---

    # Primary key = unique identifier for each row.
    # "index=True" makes lookups faster.
    id = Column(Integer, primary_key=True, index=True)

    # The user's email. "unique=True" means no two users can have
    # the same email. "nullable=False" means this field is required.
    email = Column(String, unique=True, nullable=False, index=True)

    # The hashed password. We NEVER store plain-text passwords.
    # bcrypt converts "MyPassword123" into something like
    # "$2b$12$LJ3m..." which is impossible to reverse.
    hashed_password = Column(String, nullable=False)

    # Is this account active? (default: yes)
    is_active = Column(Boolean, default=True)

    # Is this user an admin? (default: no)
    is_admin = Column(Boolean, default=False)

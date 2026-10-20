"""
services/auth.py
────────────────
Handles everything related to user authentication:
  1. Hashing passwords (turning plain text into a scrambled string).
  2. Verifying passwords (checking if a typed password matches the hash).
  3. Creating new users in the database.
  4. Looking up users by email.

LIBRARY USED: bcrypt
  - Industry-standard password hashing library.
  - Used by GitHub, Dropbox, and many other companies.
  - It automatically adds "salt" (random extra characters) so that
    even two users with the same password get different hashes.
"""

import bcrypt
from sqlalchemy.orm import Session

from models.user import User
from core.logger import logger


# ──────────────────────────────────────────────
# 1. HASH A PASSWORD
# ──────────────────────────────────────────────
def hash_password(plain_password: str) -> str:
    """
    Takes a plain-text password like "mypassword123"
    and returns a hashed version like "$2b$12$xK9z..."

    Steps:
      1. Convert the string to bytes (bcrypt needs bytes, not strings).
      2. Generate a "salt" — random characters added to make each hash unique.
      3. Hash the password + salt together.
      4. Convert the result back to a string for storage in the database.
    """
    # Convert string to bytes (bcrypt works with bytes)
    password_bytes = plain_password.encode("utf-8")

    # Generate a salt and hash the password
    # "gensalt()" creates a random salt each time
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    # Convert bytes back to string so we can store it in the database
    return hashed.decode("utf-8")


# ──────────────────────────────────────────────
# 2. VERIFY A PASSWORD
# ──────────────────────────────────────────────
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if a plain-text password matches a stored hash.

    Example:
      verify_password("mypassword123", "$2b$12$xK9z...")  →  True
      verify_password("wrongpassword", "$2b$12$xK9z...")  →  False

    Returns True if they match, False if they don't.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


# ──────────────────────────────────────────────
# 3. CREATE A NEW USER
# ──────────────────────────────────────────────
def create_user(
    db: Session,
    email: str,
    plain_password: str,
    is_admin: bool = False,
) -> User:
    """
    Creates a new user in the database.

    Steps:
      1. Hash the password (never store plain text!).
      2. Create a User object with the email and hashed password.
      3. Add it to the database and save (commit).
      4. Refresh the object so it picks up the auto-generated ID.
      5. Return the new user.
    """
    hashed = hash_password(plain_password)

    new_user = User(
        email=email,
        hashed_password=hashed,
        is_active=True,
        is_admin=is_admin,
    )

    db.add(new_user)      # Stage the new user (like git add)
    db.commit()           # Save to the database (like git commit)
    db.refresh(new_user)  # Reload from DB to get the auto-generated ID

    logger.info(f"New user registered: {new_user.email} (ID: {new_user.id}, Admin: {new_user.is_admin})")
    return new_user


# ──────────────────────────────────────────────
# 4. LOOK UP A USER BY EMAIL
# ──────────────────────────────────────────────
def get_user_by_email(db: Session, email: str):
    """
    Searches the 'users' table for a user with the given email.

    Returns:
      - The User object if found.
      - None if no user exists with that email.
    """
    return db.query(User).filter(User.email == email).first()


# ──────────────────────────────────────────────
# 5. AUTHENTICATE (combines steps 2 + 4)
# ──────────────────────────────────────────────
def authenticate_user(db: Session, email: str, plain_password: str):
    """
    The main login function. Called when a user clicks "Login".

    Steps:
      1. Look up the user by email.
      2. If the email doesn't exist → return None (login fails).
      3. If the email exists, check the password.
      4. If the password is wrong → return None (login fails).
      5. If both match → return the User object (login succeeds).
    """
    user = get_user_by_email(db, email)

    # Email not found
    if user is None:
        logger.warning(f"Authentication failed: Email not found: '{email}'")
        return None

    # Password doesn't match
    if not verify_password(plain_password, user.hashed_password):
        logger.warning(f"Authentication failed: Incorrect password for: '{email}'")
        return None

    # Both correct — login successful!
    logger.info(f"Authentication successful for user: '{email}' (ID: {user.id})")
    return user

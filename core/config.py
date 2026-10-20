"""
core/config.py
──────────────
Centralised configuration for the Customer Review Analyzer.

HOW IT WORKS (step by step):
1. python-dotenv reads the .env file and puts each KEY=VALUE pair
   into the operating system's environment variables.
2. pydantic's BaseSettings class reads those environment variables
   and converts them into typed Python attributes.
3. If a required variable is MISSING, pydantic raises a clear error
   BEFORE the app starts — so you find out immediately, not after
   30 minutes of debugging.

HOW TO USE IT (from any other module):
    from core.config import settings
    print(settings.database_url)   # → "postgresql://..."
    print(settings.secret_key)     # → "change-me-..."
"""

from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# ──────────────────────────────────────────────
# 1. Load the .env file
# ──────────────────────────────────────────────
# Path(__file__)          → this file (config.py)
# .resolve()              → full absolute path
# .parents[1]             → go up 1 level (from core/ to the project root)
# / ".env"                → join with the filename
#
# Example:
#   This file  : D:\customer-review-analyzer\core\config.py
#   .parents[1]: D:\customer-review-analyzer
#   Result     : D:\customer-review-analyzer\.env
# ──────────────────────────────────────────────
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH)


# ──────────────────────────────────────────────
# 2. Declare the settings we expect
# ──────────────────────────────────────────────
class Settings(BaseSettings):
    """
    Each attribute below maps to an environment variable.
    If the variable is missing, pydantic will raise a
    ValidationError with a helpful message.
    """

    # The PostgreSQL connection string
    database_url: str = Field(
        ...,                       # "..." means REQUIRED (no default value)
        description="PostgreSQL connection string",
    )

    # The secret key used to sign authentication cookies
    secret_key: str = Field(
        ...,
        description="Secret key for signing auth cookies",
    )

    # You can add more settings later, for example:
    # debug: bool = Field(default=False, description="Enable debug mode")

    class Config:
        # Tell pydantic-settings which env var names to look for.
        # By default it matches attribute names (case-insensitive).
        env_file = ".env"
        case_sensitive = False


# ──────────────────────────────────────────────
# 3. Create a single "settings" object (singleton)
#    that the rest of the app imports.
# ──────────────────────────────────────────────
settings = Settings()

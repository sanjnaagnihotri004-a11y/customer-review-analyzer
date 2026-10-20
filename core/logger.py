"""
core/logger.py
──────────────
Centralized logging configuration using Loguru.

WHY WE USE LOGURU:
  - Standard 'print()' statements vanish into thin air and cannot be tracked in production.
  - Loguru provides structured logging with timestamps, log levels (INFO, WARNING, ERROR),
    and automatic file rotation (so log files don't grow forever and fill your hard drive).
"""

import sys
from pathlib import Path
from loguru import logger

# Create the logs/ folder in the project root if it doesn't exist
LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Remove default Loguru handler to prevent duplicate entries
logger.remove()

# 1. Console Handler (for local development terminal)
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
)

# 2. File Handler (saves records to logs/app.log)
# rotation="5 MB" means when the file reaches 5MB, it starts a new file.
# retention="7 days" means logs older than 7 days are automatically deleted.
logger.add(
    LOGS_DIR / "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} - {message}",
    level="INFO",
    rotation="5 MB",
    retention="7 days",
    encoding="utf-8",
)

# Export the configured logger
__all__ = ["logger"]

"""Input Validation — Phase 10 §10.13–10.17.

Validates and sanitizes all external inputs:
    - User queries (length, content)
    - File paths (path traversal protection)
    - File uploads (type, size, filename sanitization)

Security rules:
    - Document content ≠ System instruction (§10.16)
    - User-provided paths must NEVER escape allowed directories (§10.15)
    - Filenames are sanitized to prevent OS-level exploits
"""

from __future__ import annotations

import os
import re
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Optional

from sip.core.logging import get_logger

logger = get_logger(__name__)

# ─── Constants ──────────────────────────────────────────────────────────────

MAX_QUERY_LENGTH = 4096
MAX_FILE_SIZE_MB = 50
ALLOWED_EXTENSIONS = {
    ".md", ".txt", ".rst", ".html", ".htm",
    ".json", ".yaml", ".yml", ".toml",
    ".py", ".js", ".ts", ".go", ".rs", ".java", ".c", ".cpp", ".h",
    ".xml", ".csv", ".pdf",
}

# Patterns that suggest prompt injection in document content
_INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?previous\s+instructions",
    r"(?i)you\s+are\s+now\s+a\s+different",
    r"(?i)reveal\s+(all\s+)?(system\s+)?secrets",
    r"(?i)disregard\s+(all\s+)?instructions",
]


# ─── Query Validation ──────────────────────────────────────────────────────


def sanitize_query(query: str) -> str:
    """Validate and sanitize a user query.

    Returns the cleaned query string.
    Raises ValueError if the query is invalid.
    """
    if not query:
        raise ValueError("Query cannot be empty")

    if len(query) > MAX_QUERY_LENGTH:
        raise ValueError(
            f"Query exceeds maximum length of {MAX_QUERY_LENGTH} characters"
        )

    # Remove null bytes and other control characters
    query = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", query)
    
    query = query.strip()
    if not query:
        raise ValueError("Query cannot be empty")

    return query


def detect_prompt_injection(text: str) -> bool:
    """Check if text contains common prompt injection patterns.

    This is a heuristic detector — not a guarantee.  The architectural
    defense (§10.16: document content ≠ system instruction) is the
    primary protection.
    """
    for pattern in _INJECTION_PATTERNS:
        if re.search(pattern, text):
            logger.warning(
                "security.prompt_injection_detected",
                pattern=pattern,
            )
            return True
    return False


# ─── File Path Validation (§10.15) ─────────────────────────────────────────


def validate_file_path(
    user_path: str,
    allowed_base: str | Path,
) -> Path:
    """Validate that a user-provided path stays within the allowed directory.

    Prevents path traversal attacks (../../secret.txt).

    Returns the resolved absolute path if valid.
    Raises ValueError if the path escapes the allowed base.
    """
    allowed_base = Path(allowed_base).resolve()
    # Resolve the user path relative to the allowed base
    requested = (allowed_base / user_path).resolve()

    if not str(requested).startswith(str(allowed_base)):
        logger.warning(
            "security.path_traversal_blocked",
            attempted_path=user_path,
            allowed_base=str(allowed_base),
        )
        raise ValueError("Path traversal detected — access denied")

    return requested


# ─── File Upload Validation (§10.14) ───────────────────────────────────────


def _sanitize_filename(filename: str) -> str:
    """Remove dangerous characters from a filename."""
    # Strip path separators
    filename = PurePosixPath(filename).name
    filename = PureWindowsPath(filename).name
    # Remove special characters (keep alphanumeric, dots, hyphens, underscores)
    filename = re.sub(r"[^\w.\-]", "_", filename)
    # Prevent hidden files
    filename = filename.lstrip(".")
    return filename or "unnamed_file"


def validate_file_upload(
    filename: str,
    file_size_bytes: int,
    allowed_extensions: set[str] | None = None,
    max_size_mb: float = MAX_FILE_SIZE_MB,
) -> str:
    """Validate a file upload and return the sanitized filename.

    Raises ValueError if validation fails.
    """
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_EXTENSIONS

    # 1. Sanitize filename
    clean_name = _sanitize_filename(filename)

    # 2. Check extension
    ext = Path(clean_name).suffix.lower()
    if ext not in allowed_extensions:
        raise ValueError(
            f"File type '{ext}' is not allowed. "
            f"Allowed: {sorted(allowed_extensions)}"
        )

    # 3. Check size
    max_bytes = int(max_size_mb * 1024 * 1024)
    if file_size_bytes > max_bytes:
        raise ValueError(
            f"File size ({file_size_bytes} bytes) exceeds "
            f"maximum of {max_size_mb} MB"
        )

    logger.info(
        "security.file_validated",
        original_filename=filename,
        sanitized_filename=clean_name,
        size_bytes=file_size_bytes,
    )

    return clean_name

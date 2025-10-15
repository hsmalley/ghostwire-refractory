"""
Security utilities for GhostWire Refractory
"""

import re
from typing import Any

from ..utils.error_handling import ValidationError


def validate_session_id(session_id: str) -> bool:
    """Validate session ID format"""
    if not session_id:
        raise ValidationError("Session ID cannot be empty")

    if not isinstance(session_id, str):
        raise ValidationError("Session ID must be a string")

    # Basic validation: alphanumeric, hyphens, and underscores, 1-64 chars
    if not re.match(r"^[a-zA-Z0-9_-]{1,64}$", session_id):
        raise ValidationError("Session ID contains invalid characters or is too long")

    return True


def validate_text_content(text: str, max_length: int = 10000) -> bool:
    """Validate text content"""
    if not text:
        raise ValidationError("Text content cannot be empty")

    if not isinstance(text, str):
        raise ValidationError("Text content must be a string")

    if len(text) > max_length:
        raise ValidationError(
            f"Text content too long. Maximum {max_length} characters allowed"
        )

    # Check for potential injection patterns (basic check)
    injection_patterns = [
        r"<script",  # Potential XSS
        r"eval\s*\(",  # Potential code injection
        r"exec\s*\(",  # Potential code injection
    ]

    for pattern in injection_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValidationError(
                f"Text content contains potentially unsafe patterns: {pattern}"
            )

    return True


def validate_embedding(embedding: Any, expected_dim: int) -> bool:
    """Validate embedding vector"""
    if not isinstance(embedding, (list, tuple)):
        raise ValidationError("Embedding must be a list or tuple of floats")

    if len(embedding) != expected_dim:
        raise ValidationError(
            f"Embedding dimension {len(embedding)} does not match "
            f"expected {expected_dim}"
        )

    # Check that all elements are numbers
    for i, val in enumerate(embedding):
        if not isinstance(val, (int, float)):
            raise ValidationError(
                f"Embedding value at index {i} is not a number: {type(val)}"
            )

    # Check for non-finite values
    import numpy as np

    vec = np.array(embedding, dtype=np.float32)
    if not np.all(np.isfinite(vec)):
        raise ValidationError("Embedding contains non-finite values (NaN or infinity)")

    return True


def sanitize_input(text: str) -> str:
    """Basic input sanitization"""
    if not text:
        return text

    # Remove null bytes
    text = text.replace("\x00", "")

    # Basic HTML entity encoding (not a complete solution, just a start)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&#x27;")

    return text


def is_safe_filename(filename: str) -> bool:
    """Check if a filename is safe to use"""
    if not filename:
        return False

    # Prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        return False

    # Only allow alphanumeric, dots, hyphens, and underscores
    if not re.match(r"^[a-zA-Z0-9._-]+$", filename):
        return False

    # Prevent common dangerous extensions (this is just a basic check)
    dangerous_exts = [
        ".exe",
        ".bat",
        ".cmd",
        ".com",
        ".pif",
        ".scr",
        ".vbs",
        ".js",
        ".jar",
    ]
    return not any(filename.lower().endswith(ext) for ext in dangerous_exts)

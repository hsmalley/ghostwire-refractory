"""
Error handling utilities for GhostWire Refractory
"""

from enum import Enum

from fastapi import HTTPException, status
from pydantic import BaseModel


class ErrorCode(str, Enum):
    """Enumeration of error codes for the application"""

    # General errors
    GENERAL_ERROR = "GENERAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"

    # Database errors
    DATABASE_ERROR = "DATABASE_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"

    # Embedding errors
    EMBEDDING_ERROR = "EMBEDDING_ERROR"
    EMBEDDING_DIM_MISMATCH = "EMBEDDING_DIM_MISMATCH"

    # Memory errors
    MEMORY_NOT_FOUND = "MEMORY_NOT_FOUND"
    COLLECTION_NOT_FOUND = "COLLECTION_NOT_FOUND"

    # Authentication errors
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    INVALID_TOKEN = "INVALID_TOKEN"

    # Rate limiting errors
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"


class APIError(BaseModel):
    """Standardized error response model"""

    code: ErrorCode
    message: str
    details: dict | None = None


class GhostWireException(Exception):
    """Base exception class for GhostWire Refractory"""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.GENERAL_ERROR,
        details: dict | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)

    def to_http_exception(
        self, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ) -> HTTPException:
        """Convert to HTTPException for FastAPI"""
        return HTTPException(
            status_code=status_code,
            detail={
                "code": self.error_code.value,
                "message": self.message,
                "details": self.details,
            },
        )

    def to_api_error(self) -> APIError:
        """Convert to APIError model"""
        return APIError(
            code=self.error_code, message=self.message, details=self.details
        )


# Specific exception classes
class ValidationError(GhostWireException):
    """Exception raised for validation errors"""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, ErrorCode.VALIDATION_ERROR, details)
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class DatabaseError(GhostWireException):
    """Exception raised for database errors"""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, ErrorCode.DATABASE_ERROR, details)
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class EmbeddingError(GhostWireException):
    """Exception raised for embedding-related errors"""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, ErrorCode.EMBEDDING_ERROR, details)
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class EmbeddingDimMismatchError(GhostWireException):
    """Exception raised when embedding dimensions don't match"""

    def __init__(self, expected: int, actual: int):
        message = f"Embedding dimension mismatch: expected {expected}, got {actual}"
        details = {"expected_dim": expected, "actual_dim": actual}
        super().__init__(message, ErrorCode.EMBEDDING_DIM_MISMATCH, details)
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class MemoryNotFoundError(GhostWireException):
    """Exception raised when a memory is not found"""

    def __init__(self, memory_id: int):
        message = f"Memory with ID {memory_id} not found"
        details = {"memory_id": memory_id}
        super().__init__(message, ErrorCode.MEMORY_NOT_FOUND, details)
        self.status_code = status.HTTP_404_NOT_FOUND


class CollectionNotFoundError(GhostWireException):
    """Exception raised when a collection is not found"""

    def __init__(self, collection_name: str):
        message = f"Collection '{collection_name}' not found"
        details = {"collection_name": collection_name}
        super().__init__(message, ErrorCode.COLLECTION_NOT_FOUND, details)
        self.status_code = status.HTTP_404_NOT_FOUND


class AuthenticationError(GhostWireException):
    """Exception raised for authentication errors"""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, ErrorCode.AUTHENTICATION_ERROR)
        self.status_code = status.HTTP_401_UNAUTHORIZED


class AuthorizationError(GhostWireException):
    """Exception raised for authorization errors"""

    def __init__(self, message: str = "Authorization failed"):
        super().__init__(message, ErrorCode.AUTHORIZATION_ERROR)
        self.status_code = status.HTTP_403_FORBIDDEN


class RateLimitExceededError(GhostWireException):
    """Exception raised when rate limit is exceeded"""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, ErrorCode.RATE_LIMIT_EXCEEDED)
        self.status_code = status.HTTP_429_TOO_MANY_REQUESTS


# Error handling functions
def handle_exception(exc: Exception) -> GhostWireException:
    """Handle an exception and return appropriate GhostWireException"""
    if isinstance(exc, GhostWireException):
        return exc
    elif isinstance(exc, HTTPException):
        # Convert HTTPException to GhostWireException if needed
        return GhostWireException(str(exc.detail))
    else:
        # For other exceptions, wrap them in a general error
        return GhostWireException(f"An unexpected error occurred: {str(exc)}")


def error_response(
    code: ErrorCode, message: str, details: dict | None = None, status_code: int = 500
):
    """Create standardized error response"""
    return {
        "error": {"code": code.value, "message": message, "details": details}
    }, status_code

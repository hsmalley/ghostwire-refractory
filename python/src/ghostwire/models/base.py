"""
Base models for GhostWire Refractory
"""
from pydantic import BaseModel


class APIResponse(BaseModel):
    """Base API response model"""
    status: str = "ok"
    message: str = ""


class ErrorResponse(BaseModel):
    """Base error response model"""
    status: str = "error"
    message: str
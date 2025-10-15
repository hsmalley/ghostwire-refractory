"""
# ⚡️ Health Endpoint

A silent pulse that confirms GhostWire is alive. The `/health` route returns the wire's status and version, letting external monitors breathe easy.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from .metrics import instrument_route


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
    message: str = ""


router = APIRouter()


@instrument_route("health")
async def health_check():
    """Basic health check endpoint"""
    return HealthResponse(status="ok")


# Register the instrumented route
router.add_api_route(
    "/health", health_check, methods=["GET"], response_model=HealthResponse
)

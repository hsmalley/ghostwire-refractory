"""
CLI module for GhostWire Refractory
"""

import uvicorn

from .config.settings import settings
from .main import app


def main():
    """Main entry point for the CLI."""
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    main()

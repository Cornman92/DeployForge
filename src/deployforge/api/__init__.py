"""
DeployForge REST API

FastAPI-based REST API for DeployForge with authentication, WebSocket support,
and comprehensive endpoints for all operations.
"""

__version__ = "0.7.0"

from deployforge.api.main import app

__all__ = ["app"]

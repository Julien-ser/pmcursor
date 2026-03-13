#!/usr/bin/env python3
"""Main entry point for PMCursor application."""

import uvicorn
from src.config import settings

if __name__ == "__main__":
    print(f"Starting PMCursor server on {settings.app_host}:{settings.app_port}")
    print("Open your browser to http://localhost:8000")
    uvicorn.run(
        "src.api.server:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )

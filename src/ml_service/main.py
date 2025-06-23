"""
ML Service Main Entry Point
"""

import logging

import uvicorn

from app.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    uvicorn.run(
        "app.api:app", host=settings.API_HOST, port=settings.API_PORT, reload=True
    )

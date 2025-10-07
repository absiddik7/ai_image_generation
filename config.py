import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app configuration


def create_app():
    from fastapi import FastAPI
    app = FastAPI(
        title="ConsultingHub AI Image Generator",
        description="Generates professional document cover images using Pollinations.AI's free API. Access the interactive API documentation at /docs.",
        version="1.0.0",
        contact={
            "name": "Support",
            "email": "support@example.com"
        }
    )
    return app

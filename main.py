from fastapi import FastAPI, HTTPException
from models.schemas import GenerateCoverRequest, GenerateCoverResponse, ImageResponse
from services.image_service import generate_cover_image
from categories import CATEGORIES
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ConsultingHub AI Image Generator",
    description="Generates professional document cover images using Pollinations.AI's free API. Access the interactive API documentation at /docs.",
    version="1.0.0",
    contact={
        "name": "Support",
        "email": "support@example.com"
    }
)


@app.post("/generate-cover-image-with-text", response_model=GenerateCoverResponse, summary="Generate a Document Cover Image with Text")
async def generate_cover_image_with_text(request: GenerateCoverRequest):
    """
    Generate a single cover image URL with title and category text based on provided details.

    This endpoint validates the category_id and category_name against a predefined dictionary, then creates a professional document cover image (864x1152 px) with the title
    and category name at the top, using visuals and style derived from the category data.
    Returns the Pollinations.AI URL to fetch the image.

    **Request Body:**
    - `title`: The document title to display on the image.
    - `category_name`: The name of the document category (e.g., Tender Specialist, Tax & VAT Specialist).
    - `category_id`: The ID of the document category (must match the name in the dictionary).

    **Notes:**
    - Uses Pollinations.AI's free API with the 'flux' model and enhanced quality.
    - If category_id or category_name doesn't match, returns error.
    """
    try:
        # Validate category_id and category_name
        category_data = CATEGORIES.get(request.category_id)
        if not category_data or category_data.get("name") != request.category_name:
            raise ValueError(
                f"Category ID {request.category_id} does not match name '{request.category_name}' or is invalid.")

        # Get description and style guideline from the matched category
        category_description = category_data["description"]
        style_guideline = category_data["style_guideline"]

        # Craft the dynamic prompt
        prompt = f"""
                    Professional document cover illustration.
                    Ultra-high-resolution, vector art quality, crisp details, polished, corporate aesthetic.

                    **Main Title:** '{request.title}'
                    **Subtitle:** '{request.category_name}'
                    (Both titles in bold, black, clean sans-serif font, centered at the top of the image. Text must be perfectly rendered, fully visible, no misspellings.)

                    **Visual Subject:** {request.category_name}, visually represented by {category_description}

                    **Style & Composition:** {style_guideline}
                    Ensure a clear, impactful, and professional design. The composition should be central and well-balanced, avoiding scattered elements.
                    """

        logger.info(f"Generating image for title {request.title}...")

        # Generate image URL with enhanced quality
        image_url = generate_cover_image(
            prompt,
            width=864,
            height=1152,
            model="flux",
            enhance=True,
            nologo=True,
            safe=True
        )

        return GenerateCoverResponse(
            images=[ImageResponse(url=image_url)]
        )

    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error generating image for {request.title}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-cover-image-no-text", response_model=GenerateCoverResponse, summary="Generate a Document Cover Image without Text")
async def generate_cover_image_no_text(request: GenerateCoverRequest):
    """
    Generate a single cover image URL without text based on category details.

    This endpoint validates the category_id and category_name against a predefined dictionary, then creates a professional document cover image (864x1152 px) using
    visuals and style derived from the category data.
    Returns the Pollinations.AI URL to fetch the image.

    **Request Body:**
    - `title`: Ignored (no text will be included).
    - `category_name`: The name of the document category (e.g., Tender Specialist, Tax & VAT Specialist).
    - `category_id`: The ID of the document category (must match the name in the dictionary).

    **Notes:**
    - Uses Pollinations.AI's free API with the 'flux' model and enhanced quality.
    - If category_id or category_name doesn't match, returns error.
    """
    try:
        # Validate category_id and category_name
        category_data = CATEGORIES.get(request.category_id)
        if not category_data or category_data.get("name") != request.category_name:
            raise ValueError(
                f"Category ID {request.category_id} does not match name '{request.category_name}' or is invalid.")

        # Get description and style guideline from the matched category
        category_description = category_data["description"]
        style_guideline = category_data["style_guideline"]

        # Craft the dynamic prompt without text
        prompt = f"""
                    Professional document cover illustration.
                    Ultra-high-resolution, vector art quality, crisp details, polished, corporate aesthetic.

                    **Visual Subject:** {request.category_name}, visually represented by {category_description}

                    **Style & Composition:** {style_guideline}
                    Ensure a clear, impactful, and professional design. The composition should be central and well-balanced, avoiding scattered elements, with no text overlay.
                    """

        logger.info(
            f"Generating image for category {request.category_name}...")

        # Generate image URL with enhanced quality
        image_url = generate_cover_image(
            prompt,
            width=864,
            height=1152,
            model="flux",
            enhance=True,
            nologo=True,
            safe=True
        )

        return GenerateCoverResponse(
            images=[ImageResponse(url=image_url)]
        )

    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(
            f"Error generating image for {request.category_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException
from app.models.schemas import GenerateCoverRequest, GenerateCoverResponse, ImageResponse
from app.utils.prompt_utils import (
    generate_cover_image_prompt
)
from app.utils.image_utils import (
    add_title_to_image,
    generate_image
)
import logging
from fastapi.responses import FileResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/api/v1/generate-dcoument-cover-image", response_model=GenerateCoverResponse, summary="Generate a Document Cover Image.")
async def generate_cover_image_with_title(request: GenerateCoverRequest):
    """
    Generate a single cover image URL without text based on category details, then add title as a downloadable image.

    This endpoint validates the category_id and category_name against a predefined dictionary, creates a professional document cover image (864x1152 px) without text,
    overlays the title and category name, and returns it as a downloadable file.

    **Request Body:**
    - `title`: The document title to overlay on the image.
    - `category_name`: The name of the document category (e.g., Tender Specialist, Tax & VAT Specialist).
    - `category_id`: The ID of the document category (must match the name in the dictionary).

    **Notes:**
    - Uses Pollinations.AI's free API with the 'flux' model and enhanced quality.
    - If category_id or category_name doesn't match, returns error.
    - Returns the image as a downloadable file.
    """
    try:
        prompt = generate_cover_image_prompt(
            request.category_name, request.subcategory_name, request.tertiary_category_name, request.title
        )
        logger.info(
            f"Generating image for category {request.category_name}...")
        image_url = generate_image(prompt)
        output_path = add_title_to_image(
            image_url, request.title, request.category_name)
        return FileResponse(
            path=output_path,
            media_type="image/png",
            filename=f"{request.title.replace(' ', '_')}_{request.category_name}.png"
        )
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(
            f"Error generating image for {request.category_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

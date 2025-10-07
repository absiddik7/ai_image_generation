from fastapi import APIRouter, HTTPException
from models.schemas import GenerateCoverRequest, GenerateCoverResponse, ImageResponse
from utils import validate_category, generate_prompt_image_with_text, generate_prompt_image_with_no_text, generate_image, add_title_to_image
import logging
from fastapi.responses import FileResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate-cover-image-with-text", response_model=GenerateCoverResponse, summary="Generate a Document Cover Image with Text")
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
        category_data = validate_category(
            request.category_id, request.category_name)
        prompt = generate_prompt_image_with_text(
            category_data, request.title, request.category_name)
        logger.info(f"Generating image for title {request.title}...")
        image_url = generate_image(prompt)
        return GenerateCoverResponse(images=[ImageResponse(url=image_url)])
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error generating image for {request.title}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-cover-image-no-text", response_model=GenerateCoverResponse, summary="Generate a Document Cover Image without Text with Title Overlay")
async def generate_cover_image_no_text(request: GenerateCoverRequest):
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
        category_data = validate_category(
            request.category_id, request.category_name)
        prompt = generate_prompt_image_with_no_text(
            category_data, request.category_name)
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

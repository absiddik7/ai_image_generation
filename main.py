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
    description="Generates a single professional document cover image URL using Pollinations.AI's free API. Access the interactive API documentation at /docs.",
    version="1.0.0",
    contact={
        "name": "Support",
        "email": "support@example.com"
    }
)

@app.post("/generate-cover-image", response_model=GenerateCoverResponse, summary="Generate a Document Cover Image")
async def generate_cover_image_endpoint(request: GenerateCoverRequest):
    """
    Generate a single cover image URL for a document based on provided details.

    This endpoint validates the category_id and category_name against a predefined dictionary, then creates a professional document cover image (260x372 px) with the title
    in black at the top section, using visuals and style derived from the category data.
    Returns the Pollinations.AI URL to fetch the image.

    **Request Body:**
    - `title`: The document title to display on the image.
    - `category_name`: The name of the document category (e.g., Tender Specialist, Tax & VAT Specialist).
    - `category_id`: The ID of the document category (must match the name in the dictionary).

    **Response:**
    - Returns a JSON object with the image URL.

    **Example:**
    - Input: {"title": "Road Construction of School", "category_name": "Procurement", "category_id": 2}
    - Output: {"status": "success", "images": [{"url": "https://pollinations.ai/p/..."}]}

    **Notes:**
    - Uses Pollinations.AI's free API with the 'flux' model and enhanced quality.
    - If category_id or category_name doesn't match, returns error.
    """
    try:
        # Validate category_id and category_name
        category_data = CATEGORIES.get(request.category_id)
        if not category_data or category_data.get("name") != request.category_name:
            raise ValueError(f"Category ID {request.category_id} does not match name '{request.category_name}' or is invalid.")

        # Get description and style guideline from the matched category
        category_description = category_data["description"]
        style_guideline = category_data["style_guideline"]

        # Craft the dynamic prompt
        prompt = f"""
        Illustration for a professional document cover with a size of 260x372 pixels, designed with high-resolution, crisp details, and a polished, professional appearance.
        Include the text '{request.title}' in black, bold, clean sans-serif font, centered at the top of the image with a minimal font size-18  (adjusted to fit within 230 pixels width), ensuring no overflow and full visibility.
        Below the title, add the text '{request.category_name}' in a smaller, clean sans-serif font in black, centered, with a font size-12 reduced to fit neatly under the title without overlapping or exceeding the 230 pixels width.
        The main subject is based on the {request.category_name} category, visually represented by {category_description}.
        Style: {style_guideline}, clear and organized composition, high-resolution, professional design with a sleek, corporate aesthetic and enhanced clarity.
        """

        logger.info(f"Generating image for title {request.title}...")

        # Generate image URL with enhanced quality
        image_url = generate_cover_image(
            prompt,
            width=620,
            height=400,
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

@app.get("/health", summary="Check API Health")
async def health_check():
    """
    Check the health status of the API.
    """
    return {"status": "healthy"}
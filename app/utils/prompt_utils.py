import logging
import random
from app.services.ai_text_service import AITextService

logger = logging.getLogger(__name__)


def generate_cover_image_prompt(category, subcategory, tertiary_category, document_title):
    """
    Generate a prompt for creating a document cover image using Pollinations AI.

    This function takes category, subcategory, tertiary category, and document title,
    constructs a meta-prompt, and uses AITextService to call the Pollinations text-to-text API.
    The image prompt ensures no text in the image and reflects the category hierarchy.
    A random seed and temperature (0.7–1.2) are generated for each call.

    Args:
        category (str): The main category.
        subcategory (str): The subcategory.
        tertiary_category (str): The tertiary category.
        document_title (str): The title of the document.

    Returns:
        str: The generated prompt for the cover image.

    Raises:
        ValueError: If API request fails.
    """
    # Generate random temperature in a constrained range for balanced creativity
    temperature = random.uniform(0.7, 1.2)
    # Generate random seed
    seed = random.randint(1, 1000000)

    # Meta-prompt for Pollinations AI to generate the image prompt
    meta_prompt = (
        f"Generate a detailed text-to-image prompt for a document cover image based on the following: "
        f"Category: {category}, Subcategory: {subcategory}, Tertiary Category: {tertiary_category}, "
        f"Document Title: {document_title}. "
        "The image must visually represent the category hierarchy in a creative, abstract, or symbolic way. "
        "Ensure the prompt specifies that the image contains absolutely no text, letters, or words. "
        "The prompt should describe a visually appealing UI-like design for the cover, such as layouts, colors, "
        "icons, or elements that evoke the themes of the categories without any textual elements. "
        "Make the description vivid and suitable for an AI image generator like Stable Diffusion."
    )

    # Use AITextService to call the API
    logger.debug(f"Generating cover image prompt with category: {category}, subcategory: {subcategory}, "
                 f"tertiary_category: {tertiary_category}, document_title: {document_title}")
    generated_prompt = AITextService.generate_image_prompt(
        meta_prompt, seed, temperature)
    return generated_prompt

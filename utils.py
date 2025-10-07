from categories import CATEGORIES
import logging
from services.image_service import generate_cover_image
import random

logger = logging.getLogger(__name__)

def validate_category(category_id: int, category_name: str) -> dict:
    """
    Validate category_id and category_name against CATEGORIES dictionary.

    Args:
        category_id (int): The ID of the category.
        category_name (str): The name of the category.

    Returns:
        dict: Category data if valid.

    Raises:
        ValueError: If validation fails.
    """
    category_data = CATEGORIES.get(category_id)
    if not category_data or category_data.get("name") != category_name:
        raise ValueError(
            f"Category ID {category_id} does not match name '{category_name}' or is invalid.")
    return category_data

def generate_prompt_image_with_text(category_data: dict, title: str, category_name: str) -> str:
    """
    Generate a prompt with title and category text using random descriptive elements and styles.

    Args:
        category_data (dict): Category data containing descriptive_elements and style_variations.
        title (str): Document title.
        category_name (str): Category name.

    Returns:
        str: Formatted prompt.
    """
    descriptive_element = random.choice(category_data["descriptive_elements"])
    style_variation = random.choice(category_data["style_variations"])
    return f"""
                Professional document infographic thumbnail.
                

                **Main Title:** '{title}'
                **Subtitle:** '{category_name}'
                (Both titles in bold, black, clean sans-serif font, centered at the top of the image. Text must be perfectly rendered, fully visible, no misspellings.)

                **visually represented by {descriptive_element}

                **Style & Composition:** {style_variation}
                """

def generate_prompt_image_with_no_text(category_data: dict, category_name: str) -> str:
    """
    Generate a prompt without text using random descriptive elements and styles.

    Args:
        category_data (dict): Category data containing descriptive_elements and style_variations.
        category_name (str): Category name.

    Returns:
        str: Formatted prompt.
    """
    descriptive_element = random.choice(category_data["descriptive_elements"])
    style_variation = random.choice(category_data["style_variations"])
    return f"""
                Professional document cover illustration.
                Ultra-high-resolution, vector art quality, crisp details, polished, corporate aesthetic.

                **Visual Subject:** {category_name}, visually represented by {descriptive_element}

                **Style & Composition:** {style_variation}
                Ensure a clear, impactful, and professional design. The composition should be central and well-balanced, avoiding scattered elements, with no text overlay.
                """

def generate_image(prompt: str, width: int = 864, height: int = 1152) -> str:
    """
    Generate image URL using the image service.

    Args:
        prompt (str): Text description for image generation.
        width (int): Image width in pixels.
        height (int): Image height in pixels.

    Returns:
        str: Generated image URL.

    Raises:
        Exception: If image generation fails.
    """
    try:
        image_url = generate_cover_image(
            prompt,
            width=width,
            height=height,
            model="flux",
            enhance=True,
            nologo=True,
            safe=True
        )
        return image_url
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise
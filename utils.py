from categories import CATEGORIES
import logging
from services.image_service import generate_cover_image
import random
from PIL import Image, ImageDraw, ImageFont
import requests
import io
import os

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
                Ensure a clear, impactful, and professional design. The composition should be central and well-balanced, No text in the image, just the visual elements. 
                """


def add_title_to_image(image_url: str, title: str, category_name: str, width: int = 864, height: int = 1152) -> str:
    """
    Add title and category name to a generated image.

    Args:
        image_url (str): URL of the generated image.
        title (str): Document title to overlay.
        category_name (str): Category name to overlay.
        width (int): Image width in pixels.
        height (int): Image height in pixels.

    Returns:
        str: Path to the saved image with title.

    Raises:
        Exception: If image processing fails.
    """
    try:
        # Download the image
        response = requests.get(image_url, timeout=60)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content)).convert("RGBA")

        # Ensure image size matches expected dimensions
        if image.size != (width, height):
            image = image.resize((width, height), Image.Resampling.LANCZOS)

        # Create a drawing context
        draw = ImageDraw.Draw(image)

        # Load fonts (Arial or fallback)
        try:
            title_font = ImageFont.truetype("Arial.ttf", 48)  # Main title font
            # Subtitle font, 24 px, non-bold
            subtitle_font = ImageFont.truetype("Arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()  # Fallback for title
            subtitle_font = ImageFont.load_default()  # Fallback for subtitle
            logger.warning(
                "Falling back to default font due to Arial.ttf unavailability")

        # Define text and position
        main_title = title
        subtitle = category_name
        text_color = (0, 0, 0)  # Black
        top_margin = 50
        max_title_width = 780

        # Wrap title if it exceeds max_title_width
        main_text_bbox = draw.textbbox((0, 0), main_title, font=title_font)
        main_text_width = main_text_bbox[2] - main_text_bbox[0]
        if main_text_width > max_title_width:
            from textwrap import fill
            # Adjust width parameter for wrapping
            main_title = fill(main_title, width=30)
            main_text_bbox = draw.textbbox((0, 0), main_title, font=title_font)
            main_text_width = main_text_bbox[2] - main_text_bbox[0]
            main_text_height = main_text_bbox[3] - main_text_bbox[1]
        else:
            main_text_height = main_text_bbox[3] - main_text_bbox[1]

        sub_text_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        sub_text_width = sub_text_bbox[2] - sub_text_bbox[0]
        sub_text_height = sub_text_bbox[3] - sub_text_bbox[1]

        # Center within 750 px, with 57 px margin on each side of 864 px
        main_x = (width - max_title_width) // 2 + \
            (max_title_width - main_text_width) // 2
        main_y = top_margin
        sub_x = (width - max_title_width) // 2 + \
            (max_title_width - sub_text_width) // 2
        sub_y = top_margin + main_text_height + 10  # Add spacing between titles

        # Log debug information
        logger.debug(
            f"Main title: '{main_title}', width: {main_text_width}, height: {main_text_height}, x: {main_x}, y: {main_y}")
        logger.debug(
            f"Subtitle: '{subtitle}', width: {sub_text_width}, height: {sub_text_height}, x: {sub_x}, y: {sub_y}")

        # Draw main title with bold effect
        for offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            draw.text((main_x + offset[0], main_y + offset[1]),
                      main_title, font=title_font, fill=(100, 100, 100))
        draw.text((main_x, main_y), main_title,
                  font=title_font, fill=text_color)

        # Draw subtitle without bold effect
        draw.text((sub_x, sub_y), subtitle,
                  font=subtitle_font, fill=text_color)

        # Save the modified image
        output_path = f"output_image_{os.urandom(8).hex()}.png"
        image.save(output_path, "PNG")
        logger.info(f"Image saved to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to add title to image: {e}")
        raise


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

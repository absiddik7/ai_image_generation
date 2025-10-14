import logging
from app.services.ai_image_service import AIImageService
from PIL import Image, ImageDraw, ImageFont
import requests
import io
import os
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_contrast_color(background_rgb):
    """
    Calculate the appropriate text color based on background luminance.

    Args:
        background_rgb (tuple): RGB values of the background (R, G, B).

    Returns:
        tuple: RGB values for the text color (black or white).
    """
    # Calculate luminance using the formula: 0.299R + 0.587G + 0.114B
    r, g, b = background_rgb
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    # Use white text for dark backgrounds, black for light
    return (255, 255, 255) if luminance < 0.5 else (0, 0, 0)


def get_background_color(image, x, y, width, height):
    """
    Calculate the average background color in the text area.

    Args:
        image (PIL.Image): The input image.
        x (int): X-coordinate of the text area.
        y (int): Y-coordinate of the text area.
        width (int): Width of the text area.
        height (int): Height of the text area.

    Returns:
        tuple: Average RGB color of the background.
    """
    # Convert image to RGB if it’s RGBA
    if image.mode == 'RGBA':
        image = image.convert('RGB')

    # Crop the region where text will be placed
    region = image.crop((x, y, x + width, y + height))
    # Convert to numpy array for averaging
    pixels = np.array(region)
    # Calculate mean RGB values
    avg_color = np.mean(pixels, axis=(0, 1)).astype(int)
    return tuple(avg_color)


def add_title_to_image(image_url: str, title: str, category_name: str, width: int = 864, height: int = 1152) -> str:
    """
    Add title and category name to a generated image with dynamic text color based on background.

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

        draw = ImageDraw.Draw(image)

        try:
            title_font = ImageFont.truetype("Arial.ttf", 48)
            subtitle_font = ImageFont.truetype(
                "Arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            logger.warning(
                "Falling back to default font due to Arial.ttf unavailability")

        # Define text and position
        main_title = title
        subtitle = category_name
        top_margin = 50
        max_title_width = 780

        # Wrap title if it exceeds max_title_width
        main_text_bbox = draw.textbbox((0, 0), main_title, font=title_font)
        main_text_width = main_text_bbox[2] - main_text_bbox[0]
        if main_text_width > max_title_width:
            from textwrap import fill
            main_title = fill(main_title, width=30)
            main_text_bbox = draw.textbbox((0, 0), main_title, font=title_font)
            main_text_width = main_text_bbox[2] - main_text_bbox[0]
            main_text_height = main_text_bbox[3] - main_text_bbox[1]
        else:
            main_text_height = main_text_bbox[3] - main_text_bbox[1]

        sub_text_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        sub_text_width = sub_text_bbox[2] - sub_text_bbox[0]
        sub_text_height = sub_text_bbox[3] - sub_text_bbox[1]

        # Center within 780 px, with 57 px margin on each side of 864 px
        main_x = (width - max_title_width) // 2 + \
            (max_title_width - main_text_width) // 2
        main_y = top_margin
        sub_x = (width - max_title_width) // 2 + \
            (max_title_width - sub_text_width) // 2
        sub_y = top_margin + main_text_height + 10

        # Calculate average background color for the text areas
        # Use the larger text area to ensure good contrast
        text_area_width = max(main_text_width, sub_text_width)
        text_area_height = main_text_height + sub_text_height + 10
        bg_color = get_background_color(
            image, main_x, main_y, text_area_width, text_area_height)
        text_color = get_contrast_color(bg_color)

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
        image_url = AIImageService.generate_cover_image(
            prompt,
            width=width,
            height=height,
            model="flux",
            enhance=True,
            nologo=True,
            safe=True,
        )
        return image_url
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise

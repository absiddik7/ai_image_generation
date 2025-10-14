import requests
import urllib.parse
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIImageService:
    """Service class for interacting with the Pollinations AI image generation API."""

    BASE_URL = "https://pollinations.ai/p/"

    @staticmethod
    def generate_cover_image(
        prompt: str,
        width: int = 864,
        height: int = 1152,
        model: str = "flux",
        seed: int | str = "random",
        nologo: bool = True,
        private: bool = False,
        enhance: bool = True,
        safe: bool = True,
        negative: str | None = None
    ) -> str:
        """
        Generate an image URL using Pollinations.AI free API.

        Args:
            prompt (str): Text description for image generation.
            width (int): Image width in pixels (default 864).
            height (int): Image height in pixels (default 1152).
            model (str): Image generation model name (default 'flux').
            seed (int | str): Random seed value or 'random' (generates a random int if 'random').
            nologo (bool): Remove Pollinations logo (default True).
            private (bool): Hide from public gallery (default False).
            enhance (bool): Enhance image quality (default True).
            safe (bool): Enable safe mode (default True).
            negative (str | None): Negative prompt (what to avoid).

        Returns:
            str: Generated image URL.

        Raises:
            Exception: If image generation fails.
        """
        try:
            # Generate a random seed if 'random' is specified
            if seed == "random":
                seed = random.randint(0, 9999)
                logger.info(f"Generated random seed: {seed}")

            # Build query parameters
            query_params = {
                "width": width,
                "height": height,
                "model": model,
                "seed": seed,
                "nologo": str(nologo).lower(),
                "private": str(private).lower(),
                "enhance": str(enhance).lower(),
                "safe": str(safe).lower()
            }

            if negative:
                query_params["negative"] = negative

            # Encode prompt and construct URL
            encoded_prompt = urllib.parse.quote(prompt)
            query_string = urllib.parse.urlencode(query_params)
            url = f"{AIImageService.BASE_URL}{encoded_prompt}?{query_string}"

            logger.info(f"Generating image with URL: {url[:100]}...")

            # Validate the URL (without downloading the image)
            response = requests.head(url, timeout=60)
            response.raise_for_status()

            return url

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise Exception(f"Failed to generate image URL: {str(e)}")

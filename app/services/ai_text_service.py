import requests
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AITextService:
    """Service class for interacting with the Pollinations AI text-to-text API."""

    BASE_URL = "https://text.pollinations.ai/"

    @staticmethod
    def generate_image_prompt(meta_prompt: str, seed: int, temperature: float) -> str:
        """
        Call the Pollinations AI API to generate text based on a meta-prompt.

        Args:
            meta_prompt (str): The meta-prompt to send to the API.
            seed (int): Seed for reproducible results.
            temperature (float): Controls randomness in output (0.0 to 3.0).

        Returns:
            str: The generated text from the API.

        Raises:
            ValueError: If temperature is out of range or API request fails.
        """
        if not 0.0 <= temperature <= 3.0:
            raise ValueError("Temperature must be between 0.0 and 3.0")

        # URL-encode the meta-prompt
        encoded_prompt = requests.utils.quote(meta_prompt)
        api_url = f"{AITextService.BASE_URL}{encoded_prompt}"
        params = {'seed': seed, 'temperature': temperature}

        try:
            logger.debug(
                f"Sending API request with seed: {seed}, temperature: {temperature:.2f}")
            response = requests.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            generated_text = response.text.strip()
            return generated_text
        except requests.RequestException as e:
            logger.error(f"Error fetching from Pollinations AI: {e}")
            raise ValueError(f"Error fetching from Pollinations AI: {e}")

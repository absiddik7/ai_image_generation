from pydantic import BaseModel
from typing import List

class GenerateCoverRequest(BaseModel):
    title: str
    category_name: str
    subcategory_name: str
    tertiary_category_name: str

class ImageResponse(BaseModel):
    url: str  # URL to the generated image

class GenerateCoverResponse(BaseModel):
    status: str = "success"
    images: List[ImageResponse]
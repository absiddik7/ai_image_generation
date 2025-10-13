from pydantic import BaseModel
from typing import List

class GenerateCoverRequest(BaseModel):
    title: str
    category_name: str
    category_id: int

class ImageResponse(BaseModel):
    url: str  # URL to the generated image

class GenerateCoverResponse(BaseModel):
    status: str = "success"
    images: List[ImageResponse]
"""
Tile-specific data models
"""

from pydantic import BaseModel, Field
from typing import List

class TileModel(BaseModel):
    position: List[int] = Field(min_length=2, max_length=2)
    description: str = Field(default="")
    terrainType: str = Field(default="plains")
    terrainEmoji: str = Field(default="🌾")

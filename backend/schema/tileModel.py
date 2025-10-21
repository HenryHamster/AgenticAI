"""
Tile-specific data models
"""

from pydantic import BaseModel, Field
from typing import List, Tuple

class SecretKV(BaseModel):
    key: str
    value: int

class TileModel(BaseModel):
    position: List[int] = Field(min_length=2, max_length=2)
    description: str = Field(default="")
    secrets: List[SecretKV] = Field(default_factory=list)
    terrainType: str = Field(default="plains")
    terrainEmoji: str = Field(default="🌾")

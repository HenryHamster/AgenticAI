"""
DungeonMaster-specific data models
"""

from pydantic import BaseModel, Field
from typing import List

class DungeonMasterModel(BaseModel):
    responses: List[str] = Field(default_factory=list)
    # Add other DM properties as needed

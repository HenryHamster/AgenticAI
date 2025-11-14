"""
Player-specific data models
"""

from pydantic import BaseModel, Field
from typing import List

class PlayerValuesModel(BaseModel):
    money: int = Field(ge=0, default=0)
    health: int = Field(ge=0, default=100)

class PlayerModel(BaseModel):
    uid: str = Field(min_length=1)
    position: List[int] = Field(min_length=2, max_length=2)
    model: str = Field(default="gpt-4.1-mini")
    player_class: str = Field(default="human")
    values: PlayerValuesModel = Field(default_factory=PlayerValuesModel)
    responses: List[str] = Field(default_factory=list)
    agent_prompt: str = Field(default="")

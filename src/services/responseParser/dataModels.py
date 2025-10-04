from pydantic import BaseModel, Field
from typing import List

class CharacterState(BaseModel):
    money: int = Field(ge=0)
    health: int = Field(ge=0)
    position: List[int] = Field(min_length=2, max_length=2)
    current_action: str

class WorldState(BaseModel):
    tiles: List[dict] = Field(default_factory=list)

class GameResponse(BaseModel):
    character_state: CharacterState
    world_state: WorldState

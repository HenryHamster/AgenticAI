from pydantic import BaseModel, Field
from typing import List

class CharacterState(BaseModel):
    uid: str
    money_change: int = Field()
    health_change: int = Field()
    position_change: List[int] = Field(min_length=2, max_length=2)

class WorldState(BaseModel):
    tiles: List[dict] = Field(default_factory=list)

class GameResponse(BaseModel):
    character_state: List[CharacterState]
    world_state: WorldState

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Tuple

class CharacterState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    uid: str
    money_change: int = Field()
    health_change: int = Field()
    position_change: List[int] = Field(min_length=2, max_length=2)
class TileState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    position: List[int] = Field(min_length=2, max_length=2)
    description: str
class WorldState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tiles: List[TileState] = Field(default_factory=list)

class GameResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    character_state: List[CharacterState]
    world_state: WorldState
    narrative_result: str = Field(default ="")    

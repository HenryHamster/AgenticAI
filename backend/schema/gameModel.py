"""
Game-specific data models
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from schema.dataModels import GameResponse, CharacterState, WorldState

class GameStateModel(BaseModel):
    players: Dict[str, 'PlayerModel'] = Field(default_factory=dict)
    dm: 'DungeonMasterModel' = Field(default_factory=lambda: DungeonMasterModel())
    tiles: List['TileModel'] = Field(default_factory=list)
    player_responses: Dict[str, str] = Field(default_factory=dict)
    dungeon_master_verdict: str = Field(default="")

class GameModel(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(default="Untitled Game")
    description: str = Field(default="")
    status: str = Field(default="active")
    world_size: int = Field(default=1)
    created_at: Optional[str] = Field(default=None)
    updated_at: Optional[str] = Field(default=None)

# Import here to avoid circular imports
from schema.playerModel import PlayerModel
from schema.tileModel import TileModel
from schema.dungeonMasterModel import DungeonMasterModel
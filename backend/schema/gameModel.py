"""
Game-specific data models
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from api.apiDtoModel import GameResponse, CharacterState, WorldState, TileState

class GameStateModel(BaseModel):
    players: Dict[str, 'PlayerModel'] = Field(default_factory=dict)
    dm: 'DungeonMasterModel' = Field(default_factory=lambda: DungeonMasterModel())
    tiles: List['TileModel'] = Field(default_factory=list)
    player_responses: Dict[str, str] = Field(default_factory=dict)
    dungeon_master_verdict: str = Field(default="")
    # Decomposed verdict components
    character_state_change: List[CharacterState] = Field(default_factory=list)
    world_state_change: Optional[WorldState] = Field(default=None)
    narrative_result: str = Field(default="")

class PlayerConfigModel(BaseModel):
    """Individual player configuration"""
    name: str
    starting_health: int = 100
    starting_currency: int = 0

class GameModel(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(default="Untitled Game")
    description: str = Field(default="")
    status: str = Field(default="active")
    model: str = Field(default="mock")
    world_size: int = Field(default=1)
    winner_player_name: Optional[str] = Field(default=None)
    currency_target: Optional[int] = Field(default=None)
    max_turns: Optional[int] = Field(default=None)
    total_players: Optional[int] = Field(default=None)
    starting_currency: Optional[int] = Field(default=0)  # Default for backward compatibility
    starting_health: Optional[int] = Field(default=100)  # Default for backward compatibility
    player_configs: Optional[List[PlayerConfigModel]] = Field(default=None)  # Individual player configs
    game_duration: Optional[str] = Field(default=None)  # Duration as ISO 8601 string or seconds
    created_at: Optional[str] = Field(default=None)
    updated_at: Optional[str] = Field(default=None)

# Import here to avoid circular imports
from schema.playerModel import PlayerModel
from schema.tileModel import TileModel
from schema.dungeonMasterModel import DungeonMasterModel
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from schema.tileModel import SecretKV

class CharacterState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    uid: str
    money_change: int = Field()
    health_change: int = Field()
    position_change: List[int] = Field(min_length=2, max_length=2)
    inventory_add: Optional[List[str]] = Field(default=None)
    inventory_remove: Optional[List[str]] = Field(default=None)

class TileState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    position: List[int] = Field(min_length=2, max_length=2)
    secrets: Optional[List[SecretKV]] = Field(default_factory=list)
    description: str
    terrainType: str = Field(default="plains")
    terrainEmoji: str = Field(default="🌾")

class WorldState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tiles: List[TileState] = Field(default_factory=list)

class PlayerEvaluation(BaseModel): 
    creativity: int = Field(default=0, ge=0, le=100)
    action_validity: int = Field(default=0, ge=0, le=100)
    progress_made: int = Field(default=0, ge=0, le=100)   

class GameResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    character_state_change: List[CharacterState]  = Field(..., min_length=1, max_length=10, description="List of character state changes") 
    world_state_change: WorldState
    narrative_result: str = Field(default ="")

class PlayerConfig(BaseModel):
    """Configuration for a single player"""
    model_config = ConfigDict(extra="forbid")
    name: str = Field(..., min_length=1, description="Player name/identifier")
    starting_health: int = Field(default=100, ge=1, description="Starting health for this player")
    starting_currency: int = Field(default=0, ge=0, description="Starting currency for this player")
    character_class: Optional[str] = Field(default=None, description="Character class (Warrior, Mage, Rogue)")
    agent_prompt: Optional[str] = Field(default="", description="Additional instructions for this player's agent")

class GameConfig(BaseModel):
    """Game-level configuration"""
    model_config = ConfigDict(extra="forbid")
    world_size: int = Field(default=2, ge=1, le=10, description="World size (grid extends from -size to +size)")
    model_mode: str = Field(default="gpt-4.1-nano", pattern=r"^(gpt-4.1-nano|gpt-4.1-mini|mock)$", description="AI model to use")
    currency_target: int = Field(default=1000, ge=1, description="Currency target for win condition")
    max_turns: int = Field(default=10, ge=1, description="Maximum number of turns")

class CreateGameRequest(BaseModel):
    """Request body for creating a new game"""
    model_config = ConfigDict(extra="forbid")
    game_config: GameConfig = Field(default_factory=GameConfig, description="Game-level configuration")
    players: List[PlayerConfig] = Field(..., min_length=1, max_length=10, description="List of player configurations")    

"""
Player-specific data models
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional

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
    character_template_name: Optional[str] = Field(default=None)
    current_abilities: List[str] = Field(default_factory=list)
    resource_pools: Dict[str, int] = Field(default_factory=dict)
    skill_cooldowns: Dict[str, int] = Field(default_factory=dict)
    experience: int = Field(ge=0, default=0)
    level: int = Field(ge=1, le=20, default=1)
    inventory: List[str] = Field(default_factory=list)
    invalid_action_count: int = Field(ge=0, default=0)
    total_action_count: int = Field(ge=0, default=0)

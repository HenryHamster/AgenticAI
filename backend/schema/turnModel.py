"""
Turn data model for storing game state at each turn
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from schema.gameModel import GameStateModel


class TurnModel(BaseModel):
    id: Optional[int] = Field(default=None)
    game_id: str = Field(min_length=1)
    turn_number: int = Field(ge=0)
    game_state: GameStateModel = Field(default_factory=GameStateModel)
    created_at: Optional[str] = Field(default=None)
    experience_awarded: Dict[str, int] = Field(default_factory=dict)
    level_ups: Dict[str, int] = Field(default_factory=dict)
    unlocked_skills: Dict[str, List[str]] = Field(default_factory=dict)

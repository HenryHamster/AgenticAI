from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class GameState:
    id: str
    state: Dict[str, Any]                    # D&D environment data (terrain, NPCs, treasures)
    x: int                                   # Grid x-coordinate
    y: int                                   # Grid y-coordinate
    environment_type: str                    # Mountain, river, dungeon, town, etc.
    available_actions: List[str]             # Context-specific D&D actions
    
    def __init__(self, id: str = "", state: Dict[str, Any] = None, x: int = 0, y: int = 0, 
                 environment_type: str = "", available_actions: List[str] = None):
        self.id = id
        self.state = state or {}
        self.x = x
        self.y = y
        self.environment_type = environment_type
        self.available_actions = available_actions or []

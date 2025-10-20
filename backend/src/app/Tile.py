from database.fileManager import Savable
from typing import override

class Tile(Savable):
    """Tile class for game world. Tiles are stored as part of game state, not in separate database table."""
    position: tuple[int,int]
    description: str
    terrainType: str
    terrainEmoji: str
    def __init__(self, description: str = "", position: tuple[int,int] = (0,0), terrainType: str = "plains", terrainEmoji: str = "🌾"):
        self.description = description
        self.position = position
        self.terrainType = terrainType
        self.terrainEmoji = terrainEmoji
    def update_description(self, new_description: str):
        self.description = new_description
    @override
    def to_dict(self) -> dict:
        return {
            "position": [self.position[0], self.position[1]],  # Store as list for JSON compatibility
            "description": self.description,
            "terrainType": self.terrainType,
            "terrainEmoji": self.terrainEmoji
        }
    @classmethod
    def from_dict(cls, data: dict) -> "Tile":
        pos_list = data.get("position", [0, 0])
        if not isinstance(pos_list, (list, tuple)) or len(pos_list) != 2:
            pos_list = [0, 0]
        return cls(
            description=data.get("description", ""),
            position=(int(pos_list[0]), int(pos_list[1])),
            terrainType=data.get("terrainType", "plains"),
            terrainEmoji=data.get("terrainEmoji", "🌾")
        )
    @override
    def save(self) -> str:
        """Save tile as JSON string. Tiles are stored in game state, not database."""
        return Savable.toJSON(self.to_dict())

    @override
    def load(self, loaded_data: dict | str | None = None, tile_id: str | None = None):
        """Load tile from data dict or JSON string. Tiles are loaded from game state, not database."""
        if isinstance(loaded_data, str):
            loaded_data = Savable.fromJSON(loaded_data)
        
        if not loaded_data:
            raise ValueError("No data provided to load")
        
        # Load properties
        pos_list = loaded_data.get("position", [0, 0])
        if not isinstance(pos_list, (list, tuple)) or len(pos_list) != 2:
            pos_list = [0, 0]
        self.position = (int(pos_list[0]), int(pos_list[1]))
        self.description = loaded_data.get("description", "")
        self.terrainType = loaded_data.get("terrainType", "plains")
        self.terrainEmoji = loaded_data.get("terrainEmoji", "🌾")
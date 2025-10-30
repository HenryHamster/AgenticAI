from database.fileManager import Savable
from typing import List
from typing_extensions import override
import json

class Secret:
    """Secret class representing a key-value pair for tile secrets."""
    def __init__(self, key: str, value: int):
        self.key = key
        self.value = value
    
    def to_tuple(self) -> tuple[str, int]:
        """Convert to tuple for backward compatibility."""
        return (self.key, self.value)
    
    def to_dict(self) -> dict:
        """Convert to dict for serialization."""
        return {"key": self.key, "value": self.value}
    
    @classmethod
    def from_tuple(cls, t: tuple[str, int]) -> "Secret":
        """Create Secret from tuple."""
        return cls(t[0], t[1])
    
    @classmethod
    def from_dict(cls, d: dict) -> "Secret":
        """Create Secret from dict."""
        return cls(d["key"], d["value"])
    
    def __repr__(self):
        return f"Secret(key='{self.key}', value={self.value})"

class Tile(Savable):
    """Tile class for game world. Tiles are stored as part of game state, not in separate database table."""
    position: tuple[int,int]
    description: str
    secrets: List[Secret]
    terrainType: str
    terrainEmoji: str
    def __init__(self, description: str = "", position: tuple[int,int] = (0,0), secrets: List[Secret | tuple[str, int] | dict] = [], terrainType: str = "plains", terrainEmoji: str = "🌾"):
        self.description = description
        self.position = position
        # Convert various formats to Secret objects
        converted_secrets = []
        for s in secrets:
            if isinstance(s, Secret):
                converted_secrets.append(s)
            elif isinstance(s, tuple):
                converted_secrets.append(Secret.from_tuple(s))
            elif isinstance(s, dict):
                converted_secrets.append(Secret.from_dict(s))
            elif hasattr(s, 'key') and hasattr(s, 'value'):
                # Handle SecretKV pydantic models
                converted_secrets.append(Secret(s.key, s.value))
        self.secrets = converted_secrets
        self.terrainType = terrainType
        self.terrainEmoji = terrainEmoji
    def update_description(self, new_description: str):
        self.description = new_description
    def update_secrets(self, secrets: List[Secret | tuple[str,int] | dict]):
        # Convert various formats to Secret objects
        converted_secrets = []
        for s in secrets:
            if isinstance(s, Secret):
                converted_secrets.append(s)
            elif isinstance(s, tuple):
                converted_secrets.append(Secret.from_tuple(s))
            elif isinstance(s, dict):
                converted_secrets.append(Secret.from_dict(s))
            elif hasattr(s, 'key') and hasattr(s, 'value'):
                # Handle SecretKV pydantic models
                converted_secrets.append(Secret(s.key, s.value))
        self.secrets = converted_secrets
    @override
    def to_dict(self) -> dict:
        return {
            "position": [self.position[0], self.position[1]],  # Store as list for JSON compatibility
            "description": self.description,
            "secrets": json.dumps([[s.key, s.value] for s in self.secrets]),
            "terrainType": self.terrainType,
            "terrainEmoji": self.terrainEmoji
        }
    def clean_to_dict(self) -> dict:
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
        secrets_data = json.loads(data.get("secrets", "[]"))
        secrets = [Secret(item[0], item[1]) for item in secrets_data]
        return cls(     
            description=data.get("description", ""),
            position=(int(pos_list[0]), int(pos_list[1])),
            secrets=secrets,
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

        secrets_data = json.loads(loaded_data.get("secrets", "[]"))
        self.secrets = [Secret(item[0], item[1]) for item in secrets_data]
        self.position = (int(pos_list[0]), int(pos_list[1]))
        self.description = loaded_data.get("description", "")
        self.terrainType = loaded_data.get("terrainType", "plains")
        self.terrainEmoji = loaded_data.get("terrainEmoji", "🌾")
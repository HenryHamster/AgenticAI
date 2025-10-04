from src.database.fileManager import Savable
from typing import override, overload
class Tile(Savable):
    position: tuple[int,int]
    description: str #Just a basic string
    def __init__(self, description: str = "", position: tuple[int,int] = (0,0)):
        self.description = description
        self.position = position
    def update_description(self, new_description: str):
        self.description = new_description
    @override
    def save(self) -> str:
        # Store position as a list (JSON doesn't support tuples)
        return Savable.toJSON({
            "position": list(self.position),
            "description": self.description,
        })

    @override
    def load(self, loaded_data: dict | str):
        loaded_data = loaded_data if isinstance(loaded_data, dict) else Savable.fromJSON(loaded_data)       
        self.position = tuple(loaded_data.get("position", (0, 0)))
        self.description = loaded_data.get("description", "")
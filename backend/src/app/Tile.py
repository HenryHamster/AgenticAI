from database.fileManager import Savable
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
    def to_dict(self) -> dict:
        return {
            "position": [self.position[0], self.position[1]], #Store as list for JSON compatibility
            "description": self.description
        }
    @classmethod
    def from_dict(cls, data: dict) -> "Tile":
        pos_list = data.get("position", [0, 0])
        if not isinstance(pos_list, (list, tuple)) or len(pos_list) != 2:
            pos_list = [0, 0]
        return cls(
            description=data.get("description", ""),
            position=(int(pos_list[0]), int(pos_list[1]))
        )
    @override
    def save(self) -> str:
        # Store position as a list (JSON doesn't support tuples)
        return Savable.toJSON(self.to_dict())

    @override
    def load(self, loaded_data: dict | str):
        if isinstance(loaded_data, str):
            loaded_data = Savable.fromJSON(loaded_data)
        obj = Tile.from_dict(loaded_data)
        self.description = obj.description
        self.position = obj.position
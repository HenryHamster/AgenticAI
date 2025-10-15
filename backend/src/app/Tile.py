from database.fileManager import Savable
from typing import override, overload
from schema.tileModel import TileModel
from lib.database.tileService import save_tile_to_database, load_tile_from_database

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
        # Create TileModel for validation
        tile_data = {
            "position": list(self.position),
            "description": self.description
        }
        
        # Validate with TileModel
        tile_model = TileModel(**tile_data)
        
        # Save to database using lib function
        saved_id = save_tile_to_database(tile_model)
        
        # Return JSON string for compatibility
        return Savable.toJSON(tile_model.model_dump())

    @override
    def load(self, loaded_data: dict | str | None = None, tile_id: str | None = None):
        # If tile_id is provided, load from database using lib function
        if tile_id:
            try:
                tile_model = load_tile_from_database(tile_id)
            except ValueError as e:
                raise ValueError(f"Failed to load tile {tile_id}: {str(e)}")
        else:
            # Handle string input
            if isinstance(loaded_data, str):
                loaded_data = Savable.fromJSON(loaded_data)
            
            if not loaded_data:
                raise ValueError("No data provided to load")
            
            # Validate with TileModel
            try:
                tile_model = TileModel(**loaded_data)
            except Exception as e:
                raise ValueError(f"Invalid tile data format: {str(e)}")
        
        # Load properties
        self.position = tuple(tile_model.position)
        self.description = tile_model.description
"""
Tile service for database operations
"""

from typing import List
import json
import os
import glob
from schema.tileModel import TileModel

def save_tile_to_database(tile_model: TileModel) -> str:
    """
    Save tile data to database/file system
    Returns the saved tile position as string
    """
    position = tile_model.position
    tile_id = f"tile_{position[0]}_{position[1]}"
    
    # Ensure data directory exists in backend folder
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Save to file (placeholder for database operation)
    with open(os.path.join(data_dir, f"tile_save_{tile_id}.json"), "w") as f:
        json.dump(tile_model.model_dump(), f, indent=2)
    
    return tile_id

def load_tile_from_database(tile_id: str) -> TileModel:
    """
    Load tile data from database/file system
    Returns the loaded tile data as TileModel
    """
    try:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        with open(os.path.join(data_dir, f"tile_save_{tile_id}.json"), "r") as f:
            data = json.load(f)
        
        # Return TileModel instance
        return TileModel(**data)
    except FileNotFoundError:
        raise ValueError(f"Tile with ID {tile_id} not found")
    except Exception as e:
        raise ValueError(f"Error loading tile {tile_id}: {str(e)}")

def get_all_tiles_from_database() -> List[TileModel]:
    """
    Get all tiles from database/file system
    Returns list of TileModel instances
    """
    tiles = []
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    pattern = os.path.join(data_dir, "tile_save_*.json")
    
    for file_path in glob.glob(pattern):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            tiles.append(TileModel(**data))
        except Exception as e:
            print(f"Error loading tile from {file_path}: {str(e)}")
    
    return tiles

def delete_tile_from_database(tile_id: str) -> bool:
    """
    Delete tile from database/file system
    Returns True if successful, False otherwise
    """
    file_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"), f"tile_save_{tile_id}.json")
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting tile {tile_id}: {str(e)}")
        return False

def update_tile_in_database(tile_model: TileModel) -> bool:
    """
    Update existing tile in database/file system
    Returns True if successful, False otherwise
    """
    try:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        position = tile_model.position
        tile_id = f"tile_{position[0]}_{position[1]}"
        
        # Save updated data
        with open(os.path.join(data_dir, f"tile_save_{tile_id}.json"), "w") as f:
            json.dump(tile_model.model_dump(), f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error updating tile: {str(e)}")
        return False

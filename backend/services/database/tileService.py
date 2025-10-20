"""
Tile service for database operations
"""

from typing import List
from schema.tileModel import TileModel
from services.storage import get_storage_factory

def save_tile_to_database(tile_model: TileModel) -> str:
    """
    Save tile data to database/file system
    Returns the saved tile position as string
    """
    storage = get_storage_factory().create_tile_storage()
    return storage.save(tile_model)

def load_tile_from_database(tile_id: str) -> TileModel:
    """
    Load tile data from database/file system
    Returns the loaded tile data as TileModel
    """
    storage = get_storage_factory().create_tile_storage()
    return storage.load(tile_id)

def get_all_tiles_from_database() -> List[TileModel]:
    """
    Get all tiles from database/file system
    Returns list of TileModel instances
    """
    storage = get_storage_factory().create_tile_storage()
    return storage.get_all()

def delete_tile_from_database(tile_id: str) -> bool:
    """
    Delete tile from database/file system
    Returns True if successful, False otherwise
    """
    storage = get_storage_factory().create_tile_storage()
    return storage.delete(tile_id)

def update_tile_in_database(tile_model: TileModel) -> bool:
    """
    Update existing tile in database/file system
    Returns True if successful, False otherwise
    """
    storage = get_storage_factory().create_tile_storage()
    return storage.update(tile_model)

"""
Player service for database operations
"""

from typing import List
from schema.playerModel import PlayerModel
from services.storage import get_storage_factory

def save_player_to_database(player_model: PlayerModel) -> str:
    """
    Save player data to database/file system
    Returns the saved player ID
    """
    storage = get_storage_factory().create_player_storage()
    return storage.save(player_model)

def load_player_from_database(player_id: str) -> PlayerModel:
    """
    Load player data from database/file system
    Returns the loaded player data as PlayerModel
    """
    storage = get_storage_factory().create_player_storage()
    return storage.load(player_id)

def get_all_players_from_database() -> List[PlayerModel]:
    """
    Get all players from database/file system
    Returns list of PlayerModel instances
    """
    storage = get_storage_factory().create_player_storage()
    return storage.get_all()

def delete_player_from_database(player_id: str) -> bool:
    """
    Delete player from database/file system
    Returns True if successful, False otherwise
    """
    storage = get_storage_factory().create_player_storage()
    return storage.delete(player_id)

def update_player_in_database(player_model: PlayerModel) -> bool:
    """
    Update existing player in database/file system
    Returns True if successful, False otherwise
    """
    storage = get_storage_factory().create_player_storage()
    return storage.update(player_model)

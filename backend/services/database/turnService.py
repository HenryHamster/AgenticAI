"""
Turn service for database operations
"""

from typing import List
from schema.turnModel import TurnModel
from services.storage import get_storage_factory


def save_turn_to_database(turn_model: TurnModel) -> int:
    """
    Save turn data to database
    Returns the saved turn ID
    """
    storage = get_storage_factory().create_turn_storage()
    return storage.save(turn_model)


def load_turn_from_database(turn_id: int) -> TurnModel:
    """
    Load turn data from database
    Returns the loaded turn data as TurnModel
    """
    storage = get_storage_factory().create_turn_storage()
    return storage.load(turn_id)


def get_turns_by_game_id(game_id: str) -> List[TurnModel]:
    """
    Get all turns for a specific game from database
    Returns list of TurnModel instances ordered by turn_number
    """
    storage = get_storage_factory().create_turn_storage()
    return storage.get_by_game_id(game_id)


def get_latest_turn_by_game_id(game_id: str) -> TurnModel:
    """
    Get the latest turn for a specific game from database
    Returns the latest TurnModel instance
    """
    storage = get_storage_factory().create_turn_storage()
    return storage.get_latest_by_game_id(game_id)


def delete_turn_from_database(turn_id: int) -> bool:
    """
    Delete turn from database
    Returns True if successful, False otherwise
    """
    storage = get_storage_factory().create_turn_storage()
    return storage.delete(turn_id)


def delete_turns_by_game_id(game_id: str) -> bool:
    """
    Delete all turns for a specific game from database
    Returns True if successful, False otherwise
    """
    storage = get_storage_factory().create_turn_storage()
    return storage.delete_by_game_id(game_id)

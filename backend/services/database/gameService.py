"""
Game service for database operations
"""

from typing import List
from datetime import datetime
from schema.gameModel import GameModel, GameStateModel
from services.storage import get_storage_factory

def save_game_to_database(game_model: GameModel) -> str:
    """
    Save game data to database/file system
    Returns the saved game ID
    """
    storage = get_storage_factory().create_game_storage()
    return storage.save(game_model)

def load_game_from_database(game_id: str) -> GameModel:
    """
    Load game data from database/file system
    Returns the loaded game data as GameModel
    """
    storage = get_storage_factory().create_game_storage()
    return storage.load(game_id)

def get_game_run_from_database(game_id: str) -> GameModel:
    """
    Get game run from database/file system
    Returns the loaded game data as GameModel
    """
    return load_game_from_database(game_id)


def get_all_games_from_database() -> List[GameModel]:
    """
    Get all games from database/file system
    Returns list of GameModel instances
    """
    storage = get_storage_factory().create_game_storage()
    return storage.get_all()

def delete_game_from_database(game_id: str) -> bool:
    """
    Delete game from database/file system
    Returns True if successful, False otherwise
    """
    storage = get_storage_factory().create_game_storage()
    return storage.delete(game_id)

def update_game_in_database(game_model: GameModel) -> bool:
    """
    Update existing game in database/file system
    Returns True if successful, False otherwise
    """
    storage = get_storage_factory().create_game_storage()
    return storage.update(game_model)

def create_game_from_database(id: str) -> str:
    """
    Create game from database/file system
    Returns the created game ID
    """

    game_model = GameModel(
        id=id,
        name="Untitled Game",
        description="",
        status="active",
        game_state=GameStateModel(),
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat())

    return save_game_to_database(game_model)
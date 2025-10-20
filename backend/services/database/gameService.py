"""
Game service for database operations
"""

from typing import List
from schema.gameModel import GameModel
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

def create_game(
    id: str,
    player_info: dict = None,
    dm_info: dict = None,
    name: str = "Untitled Game",
    description: str = ""
) -> str:
    """
    Create and persist a new game to database
    
    Args:
        id: Unique identifier for the game
        player_info: Dictionary of player data keyed by UID (uses defaults if None)
        dm_info: Dungeon Master configuration (uses defaults if None)
        name: Game name
        description: Game description
        
    Returns:
        The created game ID
    """
    from services.gameInitializer import initialize_game
    
    # Initialize the game with provided or default configuration
    game = initialize_game(
        game_id=id,
        player_info=player_info,
        dm_info=dm_info,
        name=name,
        description=description,
        status="active"
    )
    
    # Note: Game will be saved after first step() call to avoid creating empty turn 0
    # Only save the game metadata without turn data
    from schema.gameModel import GameModel
    game_data = GameModel(
        id=id,
        name=game.name,
        description=game.description,
        status=game.status,
        model=getattr(game, 'model', 'mock'),
        world_size=game.world_size,
        winner_player_name=None,
        currency_target=getattr(game, 'currency_target', None),
        max_turns=getattr(game, 'max_turns', None),
        total_players=getattr(game, 'total_players', None),
        game_duration=None
    )
    save_game_to_database(game_data)
    
    return id
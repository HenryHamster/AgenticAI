"""
Game service for database operations
"""

from typing import List
import json
import os
import glob
from datetime import datetime
from schema.gameModel import GameModel, GameStateModel

def save_game_to_database(game_model: GameModel) -> str:
    """
    Save game data to database/file system
    Returns the saved game ID
    """
    # For now, using file-based storage, but can be extended to use actual database
    game_id = game_model.id
    
    # Ensure data directory exists in backend folder
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Save to file (placeholder for database operation)
    with open(os.path.join(data_dir, f"game_save_{game_id}.json"), "w") as f:
        json.dump(game_model.model_dump(), f, indent=2)
    
    return game_id

def load_game_from_database(game_id: str) -> GameModel:
    """
    Load game data from database/file system
    Returns the loaded game data as GameModel
    """
    try:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        with open(os.path.join(data_dir, f"game_save_{game_id}.json"), "r") as f:
            data = json.load(f)
        
        # Return GameModel instance
        return GameModel(**data)
    except FileNotFoundError:
        raise ValueError(f"Game with ID {game_id} not found")
    except Exception as e:
        raise ValueError(f"Error loading game {game_id}: {str(e)}")

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
    games = []
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    pattern = os.path.join(data_dir, "game_save_*.json")
    
    for file_path in glob.glob(pattern):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            games.append(GameModel(**data))
        except Exception as e:
            print(f"Error loading game from {file_path}: {str(e)}")
    
    return games

def delete_game_from_database(game_id: str) -> bool:
    """
    Delete game from database/file system
    Returns True if successful, False otherwise
    """
    file_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"), f"game_save_{game_id}.json")
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting game {game_id}: {str(e)}")
        return False

def update_game_in_database(game_model: GameModel) -> bool:
    """
    Update existing game in database/file system
    Returns True if successful, False otherwise
    """
    try:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        # Save updated data
        with open(os.path.join(data_dir, f"game_save_{game_model.id}.json"), "w") as f:
            json.dump(game_model.model_dump(), f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error updating game {game_model.id}: {str(e)}")
        return False

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
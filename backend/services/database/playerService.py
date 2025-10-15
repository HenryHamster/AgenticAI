"""
Player service for database operations
"""

from typing import List
import json
import os
import glob
from schema.playerModel import PlayerModel

def save_player_to_database(player_model: PlayerModel) -> str:
    """
    Save player data to database/file system
    Returns the saved player ID
    """
    player_id = player_model.uid
    
    # Ensure data directory exists in backend folder
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Save to file (placeholder for database operation)
    with open(os.path.join(data_dir, f"player_save_{player_id}.json"), "w") as f:
        json.dump(player_model.model_dump(), f, indent=2)
    
    return player_id

def load_player_from_database(player_id: str) -> PlayerModel:
    """
    Load player data from database/file system
    Returns the loaded player data as PlayerModel
    """
    try:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        with open(os.path.join(data_dir, f"player_save_{player_id}.json"), "r") as f:
            data = json.load(f)
        
        # Return PlayerModel instance
        return PlayerModel(**data)
    except FileNotFoundError:
        raise ValueError(f"Player with ID {player_id} not found")
    except Exception as e:
        raise ValueError(f"Error loading player {player_id}: {str(e)}")

def get_all_players_from_database() -> List[PlayerModel]:
    """
    Get all players from database/file system
    Returns list of PlayerModel instances
    """
    players = []
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    pattern = os.path.join(data_dir, "player_save_*.json")
    
    for file_path in glob.glob(pattern):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            players.append(PlayerModel(**data))
        except Exception as e:
            print(f"Error loading player from {file_path}: {str(e)}")
    
    return players

def delete_player_from_database(player_id: str) -> bool:
    """
    Delete player from database/file system
    Returns True if successful, False otherwise
    """
    file_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"), f"player_save_{player_id}.json")
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting player {player_id}: {str(e)}")
        return False

def update_player_in_database(player_model: PlayerModel) -> bool:
    """
    Update existing player in database/file system
    Returns True if successful, False otherwise
    """
    try:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        # Save updated data
        with open(os.path.join(data_dir, f"player_save_{player_model.uid}.json"), "w") as f:
            json.dump(player_model.model_dump(), f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error updating player {player_model.uid}: {str(e)}")
        return False

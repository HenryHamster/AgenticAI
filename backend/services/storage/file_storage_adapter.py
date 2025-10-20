"""
File-based storage adapter implementations.
Uses JSON files for persistence.
"""

from typing import List
import json
import os
import glob
from schema.gameModel import GameModel
from schema.playerModel import PlayerModel
from schema.tileModel import TileModel


class FileGameStorageAdapter:
    """File-based storage adapter for Game entities"""
    
    def __init__(self, data_dir: str = None):
        """
        Initialize file storage adapter
        
        Args:
            data_dir: Directory for storing data files. If None, uses default location.
        """
        if data_dir is None:
            # Default to backend/data directory
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                "data"
            )
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
    
    def save(self, game: GameModel) -> str:
        """Save a game to file system"""
        file_path = os.path.join(self.data_dir, f"game_save_{game.id}.json")
        with open(file_path, "w") as f:
            json.dump(game.model_dump(), f, indent=2)
        return game.id
    
    def load(self, game_id: str) -> GameModel:
        """Load a game from file system"""
        try:
            file_path = os.path.join(self.data_dir, f"game_save_{game_id}.json")
            with open(file_path, "r") as f:
                data = json.load(f)
            return GameModel(**data)
        except FileNotFoundError:
            raise ValueError(f"Game with ID {game_id} not found")
        except Exception as e:
            raise ValueError(f"Error loading game {game_id}: {str(e)}")
    
    def get_all(self) -> List[GameModel]:
        """Get all games from file system"""
        games = []
        pattern = os.path.join(self.data_dir, "game_save_*.json")
        
        for file_path in glob.glob(pattern):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                games.append(GameModel(**data))
            except Exception as e:
                print(f"Error loading game from {file_path}: {str(e)}")
        
        return games
    
    def delete(self, game_id: str) -> bool:
        """Delete a game from file system"""
        file_path = os.path.join(self.data_dir, f"game_save_{game_id}.json")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting game {game_id}: {str(e)}")
            return False
    
    def update(self, game: GameModel) -> bool:
        """Update an existing game in file system"""
        try:
            file_path = os.path.join(self.data_dir, f"game_save_{game.id}.json")
            with open(file_path, "w") as f:
                json.dump(game.model_dump(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error updating game {game.id}: {str(e)}")
            return False


class FilePlayerStorageAdapter:
    """File-based storage adapter for Player entities"""
    
    def __init__(self, data_dir: str = None):
        """
        Initialize file storage adapter
        
        Args:
            data_dir: Directory for storing data files. If None, uses default location.
        """
        if data_dir is None:
            # Default to backend/data directory
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                "data"
            )
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
    
    def save(self, player: PlayerModel) -> str:
        """Save a player to file system"""
        file_path = os.path.join(self.data_dir, f"player_save_{player.uid}.json")
        with open(file_path, "w") as f:
            json.dump(player.model_dump(), f, indent=2)
        return player.uid
    
    def load(self, player_id: str) -> PlayerModel:
        """Load a player from file system"""
        try:
            file_path = os.path.join(self.data_dir, f"player_save_{player_id}.json")
            with open(file_path, "r") as f:
                data = json.load(f)
            return PlayerModel(**data)
        except FileNotFoundError:
            raise ValueError(f"Player with ID {player_id} not found")
        except Exception as e:
            raise ValueError(f"Error loading player {player_id}: {str(e)}")
    
    def get_all(self) -> List[PlayerModel]:
        """Get all players from file system"""
        players = []
        pattern = os.path.join(self.data_dir, "player_save_*.json")
        
        for file_path in glob.glob(pattern):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                players.append(PlayerModel(**data))
            except Exception as e:
                print(f"Error loading player from {file_path}: {str(e)}")
        
        return players
    
    def delete(self, player_id: str) -> bool:
        """Delete a player from file system"""
        file_path = os.path.join(self.data_dir, f"player_save_{player_id}.json")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting player {player_id}: {str(e)}")
            return False
    
    def update(self, player: PlayerModel) -> bool:
        """Update an existing player in file system"""
        try:
            file_path = os.path.join(self.data_dir, f"player_save_{player.uid}.json")
            with open(file_path, "w") as f:
                json.dump(player.model_dump(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error updating player {player.uid}: {str(e)}")
            return False


class FileTileStorageAdapter:
    """File-based storage adapter for Tile entities"""
    
    def __init__(self, data_dir: str = None):
        """
        Initialize file storage adapter
        
        Args:
            data_dir: Directory for storing data files. If None, uses default location.
        """
        if data_dir is None:
            # Default to backend/data directory
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                "data"
            )
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
    
    def save(self, tile: TileModel) -> str:
        """Save a tile to file system"""
        tile_id = f"tile_{tile.position[0]}_{tile.position[1]}"
        file_path = os.path.join(self.data_dir, f"tile_save_{tile_id}.json")
        with open(file_path, "w") as f:
            json.dump(tile.model_dump(), f, indent=2)
        return tile_id
    
    def load(self, tile_id: str) -> TileModel:
        """Load a tile from file system"""
        try:
            file_path = os.path.join(self.data_dir, f"tile_save_{tile_id}.json")
            with open(file_path, "r") as f:
                data = json.load(f)
            return TileModel(**data)
        except FileNotFoundError:
            raise ValueError(f"Tile with ID {tile_id} not found")
        except Exception as e:
            raise ValueError(f"Error loading tile {tile_id}: {str(e)}")
    
    def get_all(self) -> List[TileModel]:
        """Get all tiles from file system"""
        tiles = []
        pattern = os.path.join(self.data_dir, "tile_save_*.json")
        
        for file_path in glob.glob(pattern):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                tiles.append(TileModel(**data))
            except Exception as e:
                print(f"Error loading tile from {file_path}: {str(e)}")
        
        return tiles
    
    def delete(self, tile_id: str) -> bool:
        """Delete a tile from file system"""
        file_path = os.path.join(self.data_dir, f"tile_save_{tile_id}.json")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting tile {tile_id}: {str(e)}")
            return False
    
    def update(self, tile: TileModel) -> bool:
        """Update an existing tile in file system"""
        try:
            tile_id = f"tile_{tile.position[0]}_{tile.position[1]}"
            file_path = os.path.join(self.data_dir, f"tile_save_{tile_id}.json")
            with open(file_path, "w") as f:
                json.dump(tile.model_dump(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error updating tile: {str(e)}")
            return False

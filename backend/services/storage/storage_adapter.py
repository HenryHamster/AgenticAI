"""
Storage adapter interfaces using Protocol for type checking.
These define the contract that all storage implementations must follow.
"""

from typing import Protocol, List, TypeVar
from schema.gameModel import GameModel
from schema.playerModel import PlayerModel
from schema.tileModel import TileModel

T = TypeVar('T')

class GameStorageAdapter(Protocol):
    """Interface for game storage operations"""
    
    def save(self, game: GameModel) -> str:
        """Save a game and return its ID"""
        ...
    
    def load(self, game_id: str) -> GameModel:
        """Load a game by ID"""
        ...
    
    def get_all(self) -> List[GameModel]:
        """Get all games"""
        ...
    
    def delete(self, game_id: str) -> bool:
        """Delete a game by ID"""
        ...
    
    def update(self, game: GameModel) -> bool:
        """Update an existing game"""
        ...


class PlayerStorageAdapter(Protocol):
    """Interface for player storage operations"""
    
    def save(self, player: PlayerModel) -> str:
        """Save a player and return its ID"""
        ...
    
    def load(self, player_id: str) -> PlayerModel:
        """Load a player by ID"""
        ...
    
    def get_all(self) -> List[PlayerModel]:
        """Get all players"""
        ...
    
    def delete(self, player_id: str) -> bool:
        """Delete a player by ID"""
        ...
    
    def update(self, player: PlayerModel) -> bool:
        """Update an existing player"""
        ...


class TileStorageAdapter(Protocol):
    """Interface for tile storage operations"""
    
    def save(self, tile: TileModel) -> str:
        """Save a tile and return its ID"""
        ...
    
    def load(self, tile_id: str) -> TileModel:
        """Load a tile by ID"""
        ...
    
    def get_all(self) -> List[TileModel]:
        """Get all tiles"""
        ...
    
    def delete(self, tile_id: str) -> bool:
        """Delete a tile by ID"""
        ...
    
    def update(self, tile: TileModel) -> bool:
        """Update an existing tile"""
        ...

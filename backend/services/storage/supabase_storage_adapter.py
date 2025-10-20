"""
Supabase storage adapter implementations.
Uses Supabase PostgreSQL database for persistence.
"""

from typing import List, Optional
from schema.gameModel import GameModel
from schema.playerModel import PlayerModel
from schema.tileModel import TileModel

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None


class SupabaseGameStorageAdapter:
    """Supabase-based storage adapter for Game entities"""
    
    def __init__(self, supabase_url: str, supabase_key: str, table_name: str = "games"):
        """
        Initialize Supabase storage adapter
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
            table_name: Name of the table for storing games
        """
        if not SUPABASE_AVAILABLE:
            raise ImportError(
                "Supabase client not available. Install it with: pip install supabase"
            )
        
        self.client: Client = create_client(supabase_url, supabase_key)
        self.table_name = table_name
    
    def save(self, game: GameModel) -> str:
        """Save a game to Supabase"""
        try:
            data = game.model_dump()
            # Upsert (insert or update)
            response = self.client.table(self.table_name).upsert(data).execute()
            return game.id
        except Exception as e:
            raise ValueError(f"Error saving game to Supabase: {str(e)}")
    
    def load(self, game_id: str) -> GameModel:
        """Load a game from Supabase"""
        try:
            response = self.client.table(self.table_name).select("*").eq("id", game_id).execute()
            
            if not response.data or len(response.data) == 0:
                raise ValueError(f"Game with ID {game_id} not found")
            
            return GameModel(**response.data[0])
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Error loading game {game_id} from Supabase: {str(e)}")
    
    def get_all(self) -> List[GameModel]:
        """Get all games from Supabase"""
        try:
            response = self.client.table(self.table_name).select("*").execute()
            return [GameModel(**item) for item in response.data]
        except Exception as e:
            print(f"Error loading games from Supabase: {str(e)}")
            return []
    
    def delete(self, game_id: str) -> bool:
        """Delete a game from Supabase"""
        try:
            response = self.client.table(self.table_name).delete().eq("id", game_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting game {game_id} from Supabase: {str(e)}")
            return False
    
    def update(self, game: GameModel) -> bool:
        """Update an existing game in Supabase"""
        try:
            data = game.model_dump()
            response = self.client.table(self.table_name).update(data).eq("id", game.id).execute()
            return True
        except Exception as e:
            print(f"Error updating game {game.id} in Supabase: {str(e)}")
            return False


class SupabasePlayerStorageAdapter:
    """Supabase-based storage adapter for Player entities"""
    
    def __init__(self, supabase_url: str, supabase_key: str, table_name: str = "players"):
        """
        Initialize Supabase storage adapter
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
            table_name: Name of the table for storing players
        """
        if not SUPABASE_AVAILABLE:
            raise ImportError(
                "Supabase client not available. Install it with: pip install supabase"
            )
        
        self.client: Client = create_client(supabase_url, supabase_key)
        self.table_name = table_name
    
    def save(self, player: PlayerModel) -> str:
        """Save a player to Supabase"""
        try:
            data = player.model_dump()
            # Upsert (insert or update)
            response = self.client.table(self.table_name).upsert(data).execute()
            return player.uid
        except Exception as e:
            raise ValueError(f"Error saving player to Supabase: {str(e)}")
    
    def load(self, player_id: str) -> PlayerModel:
        """Load a player from Supabase"""
        try:
            response = self.client.table(self.table_name).select("*").eq("uid", player_id).execute()
            
            if not response.data or len(response.data) == 0:
                raise ValueError(f"Player with ID {player_id} not found")
            
            return PlayerModel(**response.data[0])
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Error loading player {player_id} from Supabase: {str(e)}")
    
    def get_all(self) -> List[PlayerModel]:
        """Get all players from Supabase"""
        try:
            response = self.client.table(self.table_name).select("*").execute()
            return [PlayerModel(**item) for item in response.data]
        except Exception as e:
            print(f"Error loading players from Supabase: {str(e)}")
            return []
    
    def delete(self, player_id: str) -> bool:
        """Delete a player from Supabase"""
        try:
            response = self.client.table(self.table_name).delete().eq("uid", player_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting player {player_id} from Supabase: {str(e)}")
            return False
    
    def update(self, player: PlayerModel) -> bool:
        """Update an existing player in Supabase"""
        try:
            data = player.model_dump()
            response = self.client.table(self.table_name).update(data).eq("uid", player.uid).execute()
            return True
        except Exception as e:
            print(f"Error updating player {player.uid} in Supabase: {str(e)}")
            return False


class SupabaseTileStorageAdapter:
    """Supabase-based storage adapter for Tile entities"""
    
    def __init__(self, supabase_url: str, supabase_key: str, table_name: str = "tiles"):
        """
        Initialize Supabase storage adapter
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
            table_name: Name of the table for storing tiles
        """
        if not SUPABASE_AVAILABLE:
            raise ImportError(
                "Supabase client not available. Install it with: pip install supabase"
            )
        
        self.client: Client = create_client(supabase_url, supabase_key)
        self.table_name = table_name
    
    def save(self, tile: TileModel) -> str:
        """Save a tile to Supabase"""
        try:
            tile_id = f"tile_{tile.position[0]}_{tile.position[1]}"
            data = tile.model_dump()
            data["tile_id"] = tile_id  # Add explicit tile_id for lookup
            # Upsert (insert or update)
            response = self.client.table(self.table_name).upsert(data).execute()
            return tile_id
        except Exception as e:
            raise ValueError(f"Error saving tile to Supabase: {str(e)}")
    
    def load(self, tile_id: str) -> TileModel:
        """Load a tile from Supabase"""
        try:
            response = self.client.table(self.table_name).select("*").eq("tile_id", tile_id).execute()
            
            if not response.data or len(response.data) == 0:
                raise ValueError(f"Tile with ID {tile_id} not found")
            
            # Remove tile_id before creating model
            data = response.data[0]
            data.pop("tile_id", None)
            return TileModel(**data)
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Error loading tile {tile_id} from Supabase: {str(e)}")
    
    def get_all(self) -> List[TileModel]:
        """Get all tiles from Supabase"""
        try:
            response = self.client.table(self.table_name).select("*").execute()
            tiles = []
            for item in response.data:
                # Remove tile_id before creating model
                item.pop("tile_id", None)
                tiles.append(TileModel(**item))
            return tiles
        except Exception as e:
            print(f"Error loading tiles from Supabase: {str(e)}")
            return []
    
    def delete(self, tile_id: str) -> bool:
        """Delete a tile from Supabase"""
        try:
            response = self.client.table(self.table_name).delete().eq("tile_id", tile_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting tile {tile_id} from Supabase: {str(e)}")
            return False
    
    def update(self, tile: TileModel) -> bool:
        """Update an existing tile in Supabase"""
        try:
            tile_id = f"tile_{tile.position[0]}_{tile.position[1]}"
            data = tile.model_dump()
            response = self.client.table(self.table_name).update(data).eq("tile_id", tile_id).execute()
            return True
        except Exception as e:
            print(f"Error updating tile in Supabase: {str(e)}")
            return False

"""
Storage factory for creating storage adapters based on configuration.
"""

import os
from typing import Literal
from services.storage.file_storage_adapter import (
    FileGameStorageAdapter,
    FilePlayerStorageAdapter,
    FileTileStorageAdapter,
)
from services.storage.supabase_storage_adapter import (
    SupabaseGameStorageAdapter,
    SupabasePlayerStorageAdapter,
    SupabaseTileStorageAdapter,
    SupabaseTurnStorageAdapter,
)

StorageType = Literal["file", "supabase"]


class StorageConfig:
    """Configuration for storage adapters"""

    def __init__(self):
        # Get storage type from environment variable, default to file
        self.storage_type: StorageType = os.getenv("STORAGE_TYPE", "file").lower()

        # File storage configuration
        self.file_data_dir = os.getenv("FILE_DATA_DIR", None)

        # Supabase configuration
        self.supabase_url = os.getenv("SUPABASE_URL", "")
        self.supabase_key = os.getenv("SUPABASE_KEY", "")
        self.supabase_games_table = os.getenv("SUPABASE_GAMES_TABLE", "games")
        self.supabase_players_table = os.getenv("SUPABASE_PLAYERS_TABLE", "players")
        self.supabase_tiles_table = os.getenv("SUPABASE_TILES_TABLE", "tiles")
        self.supabase_turns_table = os.getenv("SUPABASE_TURNS_TABLE", "turns")

    def validate(self):
        """Validate configuration based on storage type"""
        if self.storage_type == "supabase":
            if not self.supabase_url or not self.supabase_key:
                raise ValueError(
                    "SUPABASE_URL and SUPABASE_KEY environment variables must be set "
                    "when using Supabase storage"
                )
        elif self.storage_type != "file":
            raise ValueError(
                f"Invalid storage type: {self.storage_type}. Must be 'file' or 'supabase'"
            )


class StorageFactory:
    """Factory for creating storage adapters"""

    def __init__(self, config: StorageConfig = None):
        """
        Initialize storage factory

        Args:
            config: Storage configuration. If None, creates default config from environment.
        """
        self.config = config or StorageConfig()
        self.config.validate()

    def create_game_storage(self):
        """Create a game storage adapter based on configuration"""
        if self.config.storage_type == "file":
            return FileGameStorageAdapter(data_dir=self.config.file_data_dir)
        elif self.config.storage_type == "supabase":
            return SupabaseGameStorageAdapter(
                supabase_url=self.config.supabase_url,
                supabase_key=self.config.supabase_key,
                table_name=self.config.supabase_games_table,
            )
        else:
            raise ValueError(f"Unsupported storage type: {self.config.storage_type}")

    def create_player_storage(self):
        """Create a player storage adapter based on configuration"""
        if self.config.storage_type == "file":
            return FilePlayerStorageAdapter(data_dir=self.config.file_data_dir)
        elif self.config.storage_type == "supabase":
            return SupabasePlayerStorageAdapter(
                supabase_url=self.config.supabase_url,
                supabase_key=self.config.supabase_key,
                table_name=self.config.supabase_players_table,
            )
        else:
            raise ValueError(f"Unsupported storage type: {self.config.storage_type}")

    def create_tile_storage(self):
        """Create a tile storage adapter based on configuration"""
        if self.config.storage_type == "file":
            return FileTileStorageAdapter(data_dir=self.config.file_data_dir)
        elif self.config.storage_type == "supabase":
            return SupabaseTileStorageAdapter(
                supabase_url=self.config.supabase_url,
                supabase_key=self.config.supabase_key,
                table_name=self.config.supabase_tiles_table,
            )
        else:
            raise ValueError(f"Unsupported storage type: {self.config.storage_type}")

    def create_turn_storage(self):
        """Create a turn storage adapter based on configuration"""
        if self.config.storage_type == "file":
            raise ValueError("Turn storage is not supported with file storage. Use Supabase storage.")
        elif self.config.storage_type == "supabase":
            return SupabaseTurnStorageAdapter(
                supabase_url=self.config.supabase_url,
                supabase_key=self.config.supabase_key,
                table_name=self.config.supabase_turns_table,
            )
        else:
            raise ValueError(f"Unsupported storage type: {self.config.storage_type}")


# Global storage factory instance
_storage_factory = None


def get_storage_factory() -> StorageFactory:
    """
    Get the global storage factory instance.
    Creates it if it doesn't exist.
    """
    global _storage_factory
    if _storage_factory is None:
        _storage_factory = StorageFactory()
    return _storage_factory


def set_storage_factory(factory: StorageFactory):
    """Set a custom storage factory (useful for testing)"""
    global _storage_factory
    _storage_factory = factory

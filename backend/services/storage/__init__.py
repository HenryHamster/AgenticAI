"""
Storage abstraction layer for interchangeable datastore implementations.

This module provides:
- Storage adapter interfaces (Protocol-based)
- File-based storage implementation
- Supabase storage implementation
- Storage factory for easy instantiation
"""

from services.storage.storage_adapter import (
    GameStorageAdapter,
    PlayerStorageAdapter,
    TileStorageAdapter
)
from services.storage.file_storage_adapter import (
    FileGameStorageAdapter,
    FilePlayerStorageAdapter,
    FileTileStorageAdapter
)
from services.storage.supabase_storage_adapter import (
    SupabaseGameStorageAdapter,
    SupabasePlayerStorageAdapter,
    SupabaseTileStorageAdapter
)
from services.storage.storage_factory import (
    StorageFactory,
    StorageConfig,
    get_storage_factory,
    set_storage_factory
)

__all__ = [
    # Interfaces
    "GameStorageAdapter",
    "PlayerStorageAdapter",
    "TileStorageAdapter",
    # File implementations
    "FileGameStorageAdapter",
    "FilePlayerStorageAdapter",
    "FileTileStorageAdapter",
    # Supabase implementations
    "SupabaseGameStorageAdapter",
    "SupabasePlayerStorageAdapter",
    "SupabaseTileStorageAdapter",
    # Factory
    "StorageFactory",
    "StorageConfig",
    "get_storage_factory",
    "set_storage_factory",
]

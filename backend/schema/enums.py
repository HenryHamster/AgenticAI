"""
Enums for type-safe schema definitions
"""

from enum import Enum


class GameStatus(str, Enum):
    """
    Game status enum for type-safe status tracking.
    
    Values:
    - PENDING: Game is created but not yet active (initialization phase)
    - ACTIVE: Game is currently in progress
    - COMPLETED: Game has ended successfully (win condition met or max turns reached)
    - ERRORED: Game has ended in failure (all players dead)
    - PAUSED: Game is temporarily paused (future use)
    - CANCELLED: Game was cancelled/abandoned (future use)
    """
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    ERRORED = "errored"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    
    def __str__(self) -> str:
        """Return the string value for easy serialization."""
        return self.value

"""
Game end and win conditions with extensible architecture.

This module provides an abstract base class for game conditions and concrete
implementations for various stopping conditions (max turns, all players dead,
currency goal reached, etc.).
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.app.Game import Game
    from src.app.Player import Player


class GameCondition(ABC):
    """
    Abstract base class for game end/win conditions.
    
    Subclasses must implement:
    - is_met(): Check if the condition is satisfied
    - get_reason(): Return a human-readable reason for the condition
    - get_priority(): Return priority (lower = checked first)
    """
    
    @abstractmethod
    def is_met(self, game: 'Game') -> bool:
        """
        Check if this condition is currently satisfied.
        
        Args:
            game: The Game instance to check
            
        Returns:
            True if the condition is met, False otherwise
        """
        pass
    
    @abstractmethod
    def get_reason(self, game: 'Game') -> str:
        """
        Get a human-readable description of why this condition was met.
        
        Args:
            game: The Game instance
            
        Returns:
            A descriptive string explaining the condition
        """
        pass
    
    @abstractmethod
    def get_priority(self) -> int:
        """
        Get the priority for checking this condition.
        
        Returns:
            Integer priority (lower values are checked first)
        """
        pass
    
    def get_winner_info(self, game: 'Game') -> Optional[dict]:
        """
        Optional: Get information about winners if this is a win condition.
        
        Args:
            game: The Game instance
            
        Returns:
            Dictionary with winner information, or None if not applicable
        """
        return None


class MaxTurnsCondition(GameCondition):
    """Check if maximum turns have been reached."""
    
    def is_met(self, game: 'Game') -> bool:
        max_turns = getattr(game, 'max_turns', None)
        if max_turns is None:
            return False
        return game.current_turn_number >= max_turns
    
    def get_reason(self, game: 'Game') -> str:
        max_turns = getattr(game, 'max_turns', 'N/A')
        return f"Maximum turns reached ({game.current_turn_number}/{max_turns})"
    
    def get_priority(self) -> int:
        return 10  # Check after win conditions


class AllPlayersDeadCondition(GameCondition):
    """Check if all players have died (health <= 0)."""
    
    def is_met(self, game: 'Game') -> bool:
        if not game.players:
            return False
        return all(player.values.health <= 0 for player in game.players.values())
    
    def get_reason(self, game: 'Game') -> str:
        return "All players have died"
    
    def get_priority(self) -> int:
        return 5  # Check this early as it's a definitive end


class CurrencyGoalCondition(GameCondition):
    """Check if any player has reached the currency goal."""
    
    def is_met(self, game: 'Game') -> bool:
        currency_target = getattr(game, 'currency_target', None)
        if currency_target is None:
            return False
        return any(player.values.money >= currency_target 
                   for player in game.players.values())
    
    def get_reason(self, game: 'Game') -> str:
        currency_target = getattr(game, 'currency_target', 'N/A')
        winners = self._get_winners(game)
        winner_names = ', '.join(winners)
        return f"Currency goal reached! Winner(s): {winner_names} (Goal: {currency_target})"
    
    def get_priority(self) -> int:
        return 1  # Check win conditions first
    
    def _get_winners(self, game: 'Game') -> list[str]:
        """Get list of player UIDs who have reached the goal."""
        currency_target = getattr(game, 'currency_target', None)
        if currency_target is None:
            return []
        return [uid for uid, player in game.players.items() 
                if player.values.money >= currency_target]
    
    def get_winner_info(self, game: 'Game') -> Optional[dict]:
        """Return information about winning players."""
        winners = self._get_winners(game)
        if not winners:
            return None
        
        # Get the winner with the most money (in case of ties)
        winner_data = {
            uid: game.players[uid].values.money 
            for uid in winners
        }
        top_winner = max(winner_data.items(), key=lambda x: x[1])
        
        return {
            'winner_uids': winners,
            'top_winner_uid': top_winner[0],
            'top_winner_money': top_winner[1],
            'all_winners': winner_data
        }


class GameConditionManager:
    """
    Manager for evaluating multiple game conditions.
    
    This class maintains a collection of conditions and checks them in priority order.
    """
    
    def __init__(self):
        self.conditions: list[GameCondition] = []
    
    def add_condition(self, condition: GameCondition) -> None:
        """
        Add a condition to check.
        
        Args:
            condition: GameCondition instance to add
        """
        self.conditions.append(condition)
        # Keep conditions sorted by priority
        self.conditions.sort(key=lambda c: c.get_priority())
    
    def check_conditions(self, game: 'Game') -> Optional[tuple[GameCondition, str]]:
        """
        Check all conditions in priority order.
        
        Args:
            game: The Game instance to check
            
        Returns:
            Tuple of (condition, reason) if any condition is met, None otherwise
        """
        for condition in self.conditions:
            if condition.is_met(game):
                reason = condition.get_reason(game)
                return (condition, reason)
        return None
    
    def remove_condition(self, condition_type: type) -> None:
        """
        Remove all conditions of a specific type.
        
        Args:
            condition_type: The class type to remove
        """
        self.conditions = [c for c in self.conditions if not isinstance(c, condition_type)]

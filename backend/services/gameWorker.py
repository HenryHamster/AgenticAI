"""
Game Worker - Runs game instances automatically
"""

import os
import sys
import asyncio
from typing import Optional
from datetime import datetime
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app.Game import Game
from services.gameInitializer import initialize_game
from schema.enums import GameStatus
from services.database.gameService import (
    load_game_from_database,
    update_game_in_database,
)


class GameWorker:
    """Worker to run game instances asynchronously"""
    
    def __init__(self, game_id: str, verbose: bool = False):
        """
        Initialize the game worker
        
        Args:
            game_id: ID of the game to run
            verbose: Enable verbose logging
        """
        self.game_id = game_id
        self.verbose = verbose
        self.game: Optional[Game] = None
        
    def _log(self, message: str, prefix: str = "[GameWorker]"):
        """Log message if verbose is enabled"""
        if self.verbose:
            print(f"{prefix} {message}", flush=True)
    
    def initialize_or_load_game(self):
        """Initialize game if pending, or load if already initialized"""
        try:
            # Fetch game configuration from database
            game_model = load_game_from_database(self.game_id)
            
            if game_model.status == GameStatus.PENDING:
                self._log(f"Game {self.game_id} is pending initialization...")
                self._log(f"Initializing with: players={game_model.total_players}, world_size={game_model.world_size}, model={game_model.model}")
                
                # Check if individual player configs are available
                player_configs = game_model.player_configs if hasattr(game_model, 'player_configs') else None
                if player_configs:
                    self._log(f"Using individual player configurations for {len(player_configs)} players")
                
                # Initialize the game using configuration from database
                self.game = initialize_game(
                    game_id=self.game_id,
                    num_players=game_model.total_players,
                    world_size=game_model.world_size,
                    model=game_model.model,
                    name=game_model.name,
                    description=game_model.description,
                    currency_target=game_model.currency_target,
                    starting_currency=game_model.starting_currency,
                    starting_health=game_model.starting_health,
                    max_turns=game_model.max_turns,
                    player_configs=player_configs,
                )
                
                # Transition from PENDING to ACTIVE
                self.game.status = GameStatus.ACTIVE
                self._log(f"Game initialized successfully with {len(self.game.players)} players")
                self._log(f"Game status changed from PENDING to ACTIVE")
                
            else:
                self._log(f"Loading existing game {self.game_id}...")
                
                # Create Game instance and load from database
                self.game = Game.__new__(Game)  # Create instance without calling __init__
                self.game.load(game_id=self.game_id)
                
                self._log(f"Game loaded successfully with {len(self.game.players)} players")
            
            return True
            
        except Exception as e:
            self._log(f"Failed to initialize/load game: {str(e)}", prefix="[ERROR]")
            raise
    
    def run(self):
        """Run the game for the specified number of turns"""
        if not self.game:
            raise ValueError("Game not initialized/loaded. Call initialize_or_load_game() first.")
        
        # Get max_turns from the game instance
        max_turns = getattr(self.game, 'max_turns', 10)
        self._log(f"Starting game run for {max_turns} turns...")
        
        for turn_num in range(1, max_turns + 1):
            try:
                self._log(f"=== Turn {turn_num}/{max_turns} - Begin ===")
                
                # Log pre-step snapshot if verbose
                if self.verbose:
                    for uid, player in sorted(self.game.get_all_players().items()):
                        self._log(
                            f"Player {uid}: pos={player.get_position()}, "
                            f"money={getattr(player.values, 'money', '?')}, "
                            f"health={getattr(player.values, 'health', '?')}"
                        )
                
                # Execute game step (this automatically saves after each step)
                self._log(f"Executing game.step() for turn {turn_num}...")
                self.game.step()
                
                self._log(f"=== Turn {turn_num}/{max_turns} - Complete ===")
                
            except Exception as e:
                self._log(f"Error during turn {turn_num}: {str(e)}", prefix="[ERROR]")
                # Update game status to error
                self._update_game_status("error")
                raise
        
        # Mark game as completed
        self._update_game_status("completed")
        self._log(f"Game run completed successfully after {max_turns} turns")
        
    def _update_game_status(self, status: str):
        """Update the game status in database"""
        try:
            game_model = load_game_from_database(self.game_id)
            # Convert string to GameStatus if needed for backward compatibility
            if isinstance(status, str):
                status = GameStatus(status)
            game_model.status = status
            update_game_in_database(game_model)
            self._log(f"Game status updated to: {status}")
        except Exception as e:
            self._log(f"Failed to update game status: {str(e)}", prefix="[ERROR]")


async def run_game_async(game_id: str, verbose: bool = False):
    """
    Asynchronously run a game
    
    Args:
        game_id: ID of the game to run
        verbose: Enable verbose logging
    """
    worker = GameWorker(game_id=game_id, verbose=verbose)
    
    # Run in executor to avoid blocking
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, worker.initialize_or_load_game)
    await loop.run_in_executor(None, worker.run)


def run_game_sync(game_id: str, verbose: bool = False):
    """
    Synchronously run a game
    
    Args:
        game_id: ID of the game to run
        verbose: Enable verbose logging
    """
    worker = GameWorker(game_id=game_id, verbose=verbose)
    worker.initialize_or_load_game()
    worker.run()

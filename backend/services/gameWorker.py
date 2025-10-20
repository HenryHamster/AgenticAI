"""
Game Worker - Runs game instances automatically
"""

import os
import sys
import asyncio
from typing import Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app.Game import Game
from services.database.gameService import load_game_from_database, update_game_in_database


class GameWorker:
    """Worker to run game instances asynchronously"""
    
    def __init__(self, game_id: str, max_turns: int = 10, verbose: bool = False):
        """
        Initialize the game worker
        
        Args:
            game_id: ID of the game to run
            max_turns: Number of turns to run (default: 10)
            verbose: Enable verbose logging
        """
        self.game_id = game_id
        self.max_turns = max_turns
        self.verbose = verbose
        self.game: Optional[Game] = None
        
    def _log(self, message: str, prefix: str = "[GameWorker]"):
        """Log message if verbose is enabled"""
        if self.verbose:
            print(f"{prefix} {message}", flush=True)
    
    def load_game(self):
        """Load the game from database"""
        try:
            self._log(f"Loading game {self.game_id}...")
            
            # Create Game instance and load from database
            self.game = Game.__new__(Game)  # Create instance without calling __init__
            self.game.load(game_id=self.game_id)
            
            self._log(f"Game loaded successfully with {len(self.game.players)} players")
            return True
            
        except Exception as e:
            self._log(f"Failed to load game: {str(e)}", prefix="[ERROR]")
            raise
    
    def run(self):
        """Run the game for the specified number of turns"""
        if not self.game:
            raise ValueError("Game not loaded. Call load_game() first.")
        
        self._log(f"Starting game run for {self.max_turns} turns...")
        
        for turn_num in range(1, self.max_turns + 1):
            try:
                self._log(f"=== Turn {turn_num}/{self.max_turns} - Begin ===")
                
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
                
                self._log(f"=== Turn {turn_num}/{self.max_turns} - Complete ===")
                
            except Exception as e:
                self._log(f"Error during turn {turn_num}: {str(e)}", prefix="[ERROR]")
                # Update game status to error
                self._update_game_status("error")
                raise
        
        # Mark game as completed
        self._update_game_status("completed")
        self._log(f"Game run completed successfully after {self.max_turns} turns")
        
    def _update_game_status(self, status: str):
        """Update the game status in database"""
        try:
            game_model = load_game_from_database(self.game_id)
            game_model.status = status
            update_game_in_database(game_model)
            self._log(f"Game status updated to: {status}")
        except Exception as e:
            self._log(f"Failed to update game status: {str(e)}", prefix="[ERROR]")


async def run_game_async(game_id: str, max_turns: int = 10, verbose: bool = False):
    """
    Asynchronously run a game
    
    Args:
        game_id: ID of the game to run
        max_turns: Number of turns to run
        verbose: Enable verbose logging
    """
    worker = GameWorker(game_id=game_id, max_turns=max_turns, verbose=verbose)
    
    # Run in executor to avoid blocking
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, worker.load_game)
    await loop.run_in_executor(None, worker.run)


def run_game_sync(game_id: str, max_turns: int = 10, verbose: bool = False):
    """
    Synchronously run a game
    
    Args:
        game_id: ID of the game to run
        max_turns: Number of turns to run
        verbose: Enable verbose logging
    """
    worker = GameWorker(game_id=game_id, max_turns=max_turns, verbose=verbose)
    worker.load_game()
    worker.run()

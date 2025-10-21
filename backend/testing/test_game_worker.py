#!/usr/bin/env python3
"""
Test script for the game worker
Tests that the worker can run an existing game
"""

import os
import sys
import uuid

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from services.database.gameService import create_game
from services.gameWorker import run_game_sync


def test_worker():
    """Test the game worker with a newly created game"""
    print("=" * 60)
    print("Testing Game Worker")
    print("=" * 60)
    
    # Create a test game
    game_id = f"test_game_{uuid.uuid4().hex[:8]}"
    print(f"\n[1/3] Creating game with ID: {game_id}")
    
    try:
        # Create game with default settings (2 players, mock AI)
        create_game(game_id)
        print(f"✓ Game created successfully")
    except Exception as e:
        print(f"✗ Failed to create game: {e}")
        return False
    
    # Run the game worker
    print(f"\n[2/3] Running game worker (1 round)...")
    try:
        run_game_sync(game_id=game_id, rounds=1, verbose=True)
        print(f"✓ Game worker completed successfully")
    except Exception as e:
        print(f"✗ Worker failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Verify the game was updated
    print(f"\n[3/3] Verifying game state...")
    try:
        from services.database.gameService import load_game_from_database
        game_model = load_game_from_database(game_id)
        print(f"✓ Game status: {game_model.status}")
        print(f"✓ Game ID: {game_model.id}")
        print(f"✓ Game name: {game_model.name}")
    except Exception as e:
        print(f"✗ Failed to verify game: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_worker()
    sys.exit(0 if success else 1)

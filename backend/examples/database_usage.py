#!/usr/bin/env python3
"""
Example script demonstrating database layer usage.

This shows how to:
1. Create and save a game to the database
2. Load a game from the database
3. Update game state and persist changes
4. List and manage multiple game sessions

Usage:
    python3 examples/database_usage.py
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.database.game_repository import GameRepository
from src.app.Game import Game


def example_1_create_and_save():
    """Example 1: Create a new game and save it."""
    print("\n" + "="*60)
    print("Example 1: Create and Save a Game")
    print("="*60)
    
    # Create player configuration
    player_info = {
        "player1": {
            "position": [0, 0],
            "UID": "player1",
            "model": "mock",  # Use mock to avoid API calls
            "player_class": "human",
            "values": {"money": 100, "health": 100}
        },
        "player2": {
            "position": [1, 1],
            "UID": "player2",
            "model": "mock",
            "player_class": "human",
            "values": {"money": 50, "health": 90}
        }
    }
    
    dm_info = {"model": "mock"}
    
    # Create game instance
    print("Creating game...")
    game = Game(player_info, dm_info=dm_info)
    print(f"✓ Game created with {len(game.players)} players")
    print(f"  - Player 1 at {game.players['player1'].get_position()}")
    print(f"  - Player 2 at {game.players['player2'].get_position()}")
    
    # Save to database
    print("\nSaving to database...")
    repo = GameRepository()
    session = repo.save_game(game, session_name="Example Game 1")
    
    print(f"✓ Game saved successfully!")
    print(f"  - Session ID: {session.id}")
    print(f"  - Session Name: {session.name}")
    print(f"  - Players: {session.num_players}")
    
    return session.id


def example_2_load_game(session_id):
    """Example 2: Load a game from the database."""
    print("\n" + "="*60)
    print("Example 2: Load a Game")
    print("="*60)
    
    repo = GameRepository()
    
    print(f"Loading game session {session_id}...")
    game = repo.load_game(session_id)
    
    print(f"✓ Game loaded successfully!")
    print(f"  - Number of players: {len(game.players)}")
    print(f"  - Number of tiles: {len(game.tiles)}")
    
    # Display player information
    for uid, player in game.players.items():
        print(f"\n  Player: {uid}")
        print(f"    Position: {player.get_position()}")
        print(f"    Money: {player.values.money}")
        print(f"    Health: {player.values.health}")
    
    return game


def example_3_update_game(session_id):
    """Example 3: Load, modify, and save a game."""
    print("\n" + "="*60)
    print("Example 3: Update Game State")
    print("="*60)
    
    repo = GameRepository()
    
    # Load the game
    print("Loading game...")
    game = repo.load_game(session_id)
    
    # Show current state
    player1 = game.players["player1"]
    print(f"Before update:")
    print(f"  - Player1 position: {player1.get_position()}")
    print(f"  - Player1 money: {player1.values.money}")
    
    # Modify game state
    print("\nModifying game state...")
    player1.update_position((2, 1))  # Move player
    player1.values.update_money(150)  # Add money
    
    # Save changes
    print("Saving changes...")
    repo.save_game(game, session_id=session_id)
    
    # Verify changes persisted
    reloaded_game = repo.load_game(session_id)
    reloaded_player1 = reloaded_game.players["player1"]
    
    print(f"\nAfter update:")
    print(f"  - Player1 position: {reloaded_player1.get_position()}")
    print(f"  - Player1 money: {reloaded_player1.values.money}")
    print("✓ Changes persisted successfully!")


def example_4_list_sessions():
    """Example 4: List all game sessions."""
    print("\n" + "="*60)
    print("Example 4: List All Sessions")
    print("="*60)
    
    repo = GameRepository()
    
    # Get total count
    count = repo.get_session_count()
    print(f"Total game sessions: {count}")
    
    # List all sessions
    sessions = repo.list_sessions()
    
    if not sessions:
        print("No game sessions found.")
        return
    
    print("\nGame Sessions:")
    print("-" * 60)
    
    for session in sessions:
        print(f"\nID: {session.id}")
        print(f"Name: {session.name or '(unnamed)'}")
        print(f"Players: {session.num_players}")
        print(f"Turns: {session.turn_count}")
        print(f"Created: {session.created_at}")
        print(f"Updated: {session.updated_at}")


def example_5_metadata_update():
    """Example 5: Update session metadata."""
    print("\n" + "="*60)
    print("Example 5: Update Session Metadata")
    print("="*60)
    
    repo = GameRepository()
    
    # Get first session
    sessions = repo.list_sessions(limit=1)
    if not sessions:
        print("No sessions available to update")
        return
    
    session_id = sessions[0].id
    print(f"Updating metadata for session {session_id}...")
    
    # Update name and turn count
    updated = repo.update_session_metadata(
        session_id=session_id,
        name="Updated Game Name",
        turn_count=10
    )
    
    if updated:
        print(f"✓ Metadata updated successfully!")
        print(f"  - New name: {updated.name}")
        print(f"  - Turn count: {updated.turn_count}")
    else:
        print("Failed to update metadata")


def example_6_turn_tracking():
    """Example 6: Track game state across turns."""
    print("\n" + "="*60)
    print("Example 6: Turn Tracking")
    print("="*60)
    
    # Create a new game
    player_info = {
        "player1": {
            "position": [0, 0],
            "UID": "player1",
            "model": "mock",
            "player_class": "human",
            "values": {"money": 100, "health": 100}
        }
    }
    
    dm_info = {"model": "mock"}
    game = Game(player_info, dm_info=dm_info)
    
    repo = GameRepository()
    
    # Save initial game session
    session = repo.save_game(game, session_name="Turn Tracking Demo")
    session_id = session.id
    print(f"Created game session {session_id}")
    
    # Simulate 5 turns
    print("\nSimulating 5 turns...")
    for turn_num in range(1, 6):
        # Modify game state (simulate gameplay)
        game.players["player1"].values.update_money(25)
        game.players["player1"].update_position((1, 0))
        
        # Save the turn
        repo.save_turn(
            game,
            session_id=session_id,
            turn_number=turn_num,
        )
        
        money = game.players["player1"].values.money
        pos = game.players["player1"].get_position()
        print(f"  Turn {turn_num}: Position {pos}, Money: {money}")
    
    print(f"\n✓ Saved 5 turns to database")
    
    # Retrieve all turns
    print("\nRetrieving turn history...")
    turns = repo.get_turns(session_id)
    print(f"Found {len(turns)} turns")
    
    for turn in turns:
        print(f"  Turn {turn.turn_number}: created at {turn.created_at}")
    
    # Load game state from turn 3
    print("\nLoading game state from turn 3...")
    game_turn_3 = repo.load_game_from_turn(session_id, 3)
    player = game_turn_3.players["player1"]
    print(f"  Position: {player.get_position()}")
    print(f"  Money: {player.values.money}")
    print(f"  Health: {player.values.health}")
    
    # Get latest turn
    latest = repo.get_latest_turn(session_id)
    print(f"\n✓ Latest turn is turn {latest.turn_number}")
    
    return session_id


def example_7_turn_replay():
    """Example 7: Replay game from any turn."""
    print("\n" + "="*60)
    print("Example 7: Turn Replay")
    print("="*60)
    
    # Get the most recent session with turns
    repo = GameRepository()
    sessions = repo.list_sessions(limit=1)
    
    if not sessions:
        print("No sessions available for replay")
        return
    
    session_id = sessions[0].id
    turn_count = repo.get_turn_count(session_id)
    
    if turn_count == 0:
        print(f"Session {session_id} has no turns")
        return
    
    print(f"Replaying session {session_id} ({turn_count} turns)")
    print("-" * 60)
    
    # Replay each turn
    for turn_num in range(1, min(turn_count + 1, 4)):  # Show first 3 turns
        turn = repo.get_turn(session_id, turn_num)
        game_state = repo.load_game_from_turn(session_id, turn_num)
        
        print(f"\nTurn {turn_num}:")
        print(f"  Timestamp: {turn.created_at}")
        
        # Show player states
        for uid, player in game_state.players.items():
            print(f"  Player {uid}:")
            print(f"    Position: {player.get_position()}")
            print(f"    Money: {player.values.money}")
            print(f"    Health: {player.values.health}")
    
    print("\n✓ Replay complete")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print(" Database Layer Usage Examples")
    print("="*70)
    print("\nThis script demonstrates how to use the database layer for")
    print("persisting game state with SQLAlchemy and SQLite.")
    
    try:
        # Example 1: Create and save
        session_id = example_1_create_and_save()
        
        # Example 2: Load
        game = example_2_load_game(session_id)
        
        # Example 3: Update
        example_3_update_game(session_id)
        
        # Example 4: List all
        example_4_list_sessions()
        
        # Example 5: Metadata
        example_5_metadata_update()
        
        # Example 6: Turn tracking (NEW)
        turn_session_id = example_6_turn_tracking()
        
        # Example 7: Turn replay (NEW)
        example_7_turn_replay()
        
        print("\n" + "="*70)
        print("✅ All examples completed successfully!")
        print("="*70)
        print(f"\nDatabase location: data/game_state.db")
        print("You can inspect the database using any SQLite browser.")
        print("\nNew features demonstrated:")
        print("  - Turn-by-turn state tracking")
        print("  - Loading game state from specific turns")
        print("  - Turn history replay")
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ Error occurred!")
        print("="*70)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

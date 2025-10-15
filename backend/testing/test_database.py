#!/usr/bin/env python3
"""
Test script for database layer.
Tests SQLAlchemy models, database operations, and game persistence.

Usage:
    python testing/test_database.py
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.database.db import DatabaseManager
from src.database.game_repository import GameRepository
from src.database.models import GameSession
from src.app.Game import Game
from src.app.Player import Player


def test_database_creation():
    """Test that database and tables are created correctly."""
    print("\n=== Test 1: Database Creation ===")
    
    # Use a test database
    test_db_path = "testing/test_game_state.db"
    
    # Remove old test db if exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Create database manager
    db_manager = DatabaseManager(test_db_path)
    
    # Check that the database file was created
    assert os.path.exists(test_db_path), "Database file not created"
    print(f"✓ Database created at {test_db_path}")
    
    # Check that we can get a session
    session = db_manager.get_session()
    assert session is not None, "Could not create database session"
    session.close()
    print("✓ Database session created successfully")
    
    return db_manager


def test_game_session_model(db_manager):
    """Test GameSession model CRUD operations."""
    print("\n=== Test 2: GameSession Model ===")
    
    with db_manager.session_scope() as session:
        # Create a test game session
        game_state = {
            "players": {
                "player1": {
                    "UID": "player1",
                    "position": [0, 0],
                    "player_class": "human",
                    "model": "gpt-4.1-nano",
                    "values": {"money": 100, "health": 100}
                }
            },
            "dm": {"model": "gpt-4.1-nano"},
            "tiles": [
                {"position": [0, 0], "description": "A peaceful starting area."},
                {"position": [1, 0], "description": "A dense forest."}
            ]
        }
        
        game_session = GameSession(
            name="Test Game 1",
            game_state="{}",  # Will be set properly below
            turn_count=0,
            num_players=1
        )
        game_session.set_game_state_dict(game_state)
        
        session.add(game_session)
        session.flush()
        
        session_id = game_session.id
        print(f"✓ Created GameSession with ID: {session_id}")
        
        # Query it back
        retrieved = session.query(GameSession).filter(
            GameSession.id == session_id
        ).first()
        
        assert retrieved is not None, "Could not retrieve game session"
        assert retrieved.name == "Test Game 1"
        assert retrieved.num_players == 1
        print("✓ Retrieved GameSession successfully")
        
        # Check game state
        state_dict = retrieved.get_game_state_dict()
        assert "players" in state_dict
        assert "player1" in state_dict["players"]
        print("✓ Game state stored and retrieved correctly")
        
        return session_id


def test_game_repository_save_and_load(db_manager):
    """Test saving and loading a Game through the repository."""
    print("\n=== Test 3: Game Repository Save/Load ===")
    
    # Create a simple game
    player_info = {
        "player1": {
            "position": [0, 0],
            "UID": "player1",
            "model": "mock",
            "player_class": "human",
            "values": {"money": 50, "health": 100}
        },
        "player2": {
            "position": [1, 1],
            "UID": "player2",
            "model": "mock",
            "player_class": "human",
            "values": {"money": 75, "health": 90}
        }
    }
    
    dm_info = {"model": "mock"}
    
    print("Creating game instance...")
    game = Game(player_info, dm_info=dm_info)
    
    # Verify game was created
    assert len(game.players) == 2
    assert game.players["player1"].get_position() == (0, 0)
    print("✓ Game created with 2 players")
    
    # Save to database
    repo = GameRepository(db_manager)
    print("Saving game to database...")
    saved_session = repo.save_game(game, session_name="Test Game Repository")
    
    session_id = saved_session.id
    print(f"✓ Game saved with session ID: {session_id}")
    
    # Load from database
    print("Loading game from database...")
    loaded_game = repo.load_game(session_id)
    
    # Verify loaded game
    assert len(loaded_game.players) == 2
    assert loaded_game.players["player1"].get_position() == (0, 0)
    assert loaded_game.players["player2"].get_position() == (1, 1)
    assert loaded_game.players["player1"].values.money == 50
    assert loaded_game.players["player2"].values.health == 90
    print("✓ Game loaded successfully with all data intact")
    
    return session_id


def test_game_repository_update(db_manager, session_id):
    """Test updating an existing game session."""
    print("\n=== Test 4: Game Repository Update ===")
    
    repo = GameRepository(db_manager)
    
    # Load the game
    game = repo.load_game(session_id)
    
    # Modify the game state
    game.players["player1"].values.update_money(50)  # Add 50 money
    game.players["player1"].update_position((1, 0))  # Move player
    
    print(f"Modified player1: money={game.players['player1'].values.money}, pos={game.players['player1'].get_position()}")
    
    # Save the updated game
    repo.save_game(game, session_id=session_id)
    print("✓ Updated game saved to database")
    
    # Load again and verify changes
    reloaded_game = repo.load_game(session_id)
    assert reloaded_game.players["player1"].values.money == 100  # 50 + 50
    assert reloaded_game.players["player1"].get_position() == (1, 0)
    print("✓ Changes persisted correctly")


def test_repository_list_and_delete(db_manager):
    """Test listing and deleting sessions."""
    print("\n=== Test 5: List and Delete Sessions ===")
    
    repo = GameRepository(db_manager)
    
    # List sessions
    sessions = repo.list_sessions()
    initial_count = len(sessions)
    print(f"✓ Found {initial_count} game session(s)")
    
    for session in sessions:
        print(f"  - Session {session.id}: {session.name} ({session.num_players} players)")
    
    # Get count
    count = repo.get_session_count()
    assert count == initial_count
    print(f"✓ Session count verified: {count}")
    
    # Delete first session
    if sessions:
        delete_id = sessions[0].id
        deleted = repo.delete_session(delete_id)
        assert deleted, "Failed to delete session"
        print(f"✓ Deleted session {delete_id}")
        
        # Verify deletion
        new_count = repo.get_session_count()
        assert new_count == initial_count - 1
        print(f"✓ Session count after deletion: {new_count}")


def test_tiles_in_game_state(db_manager):
    """Test that tiles are properly stored in the game state."""
    print("\n=== Test 6: Tiles Storage ===")
    
    # Create game with some tiles
    player_info = {
        "player1": {
            "position": [0, 0],
            "UID": "player1",
            "model": "mock",
            "player_class": "human",
            "values": {"money": 0, "health": 100}
        }
    }
    
    dm_info = {"model": "mock"}
    game = Game(player_info, dm_info=dm_info)
    
    # Count tiles (should be based on GameConfig.world_size)
    num_tiles = len(game.tiles)
    print(f"Game created with {num_tiles} tiles")
    
    # Save and load
    repo = GameRepository(db_manager)
    saved_session = repo.save_game(game, session_name="Tile Test")
    
    loaded_game = repo.load_game(saved_session.id)
    
    # Verify tiles were preserved
    assert len(loaded_game.tiles) == num_tiles
    print(f"✓ All {num_tiles} tiles preserved in database")
    
    # Check a specific tile
    tile_0_0 = loaded_game.get_tile((0, 0))
    assert tile_0_0 is not None
    assert tile_0_0.position == (0, 0)
    print(f"✓ Tile at (0,0): {tile_0_0.description[:50]}...")


def test_turn_tracking(db_manager):
    """Test turn tracking functionality."""
    print("\n=== Test 7: Turn Tracking ===")
    
    # Create a game session
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
    
    repo = GameRepository(db_manager)
    session = repo.save_game(game, session_name="Turn Test Game")
    session_id = session.id
    print(f"✓ Created game session {session_id}")
    
    # Simulate 3 turns
    for turn_num in range(1, 4):
        # Modify game state
        game.players["player1"].values.update_money(10 * turn_num)
        game.players["player1"].update_position((1, 0))  # Move 1 tile to the right each turn
        
        # Save turn
        turn = repo.save_turn(
            game,
            session_id=session_id,
            turn_number=turn_num,
        )
        print(f"✓ Saved turn {turn_num} (ID: {turn.id})")
    
    # Get all turns
    turns = repo.get_turns(session_id)
    assert len(turns) == 3, f"Expected 3 turns, got {len(turns)}"
    print(f"✓ Retrieved {len(turns)} turns")
    
    # Verify turn data
    turn_2 = repo.get_turn(session_id, 2)
    assert turn_2 is not None
    assert turn_2.turn_number == 2
    assert turn_2.verdict == "Turn 2 completed successfully"
    print("✓ Turn 2 data verified")
    
    # Get latest turn
    latest = repo.get_latest_turn(session_id)
    assert latest.turn_number == 3
    print("✓ Latest turn is turn 3")
    
    # Load game from turn 2
    game_turn_2 = repo.load_game_from_turn(session_id, 2)
    assert game_turn_2.players["player1"].get_position() == (2, 0)
    assert game_turn_2.players["player1"].values.money == 130  # 100 + 10 + 20
    print("✓ Loaded game state from turn 2")
    
    # Get turn count
    count = repo.get_turn_count(session_id)
    assert count == 3
    print(f"✓ Turn count: {count}")
    
    return session_id


def test_turn_rollback(db_manager, session_id):
    """Test deleting turns after a specific turn number."""
    print("\n=== Test 8: Turn Rollback ===")
    
    repo = GameRepository(db_manager)
    
    # Delete turns after turn 1
    deleted = repo.delete_turns_after(session_id, 1)
    print(f"✓ Deleted {deleted} turns after turn 1")
    
    # Verify only turn 1 remains
    remaining_turns = repo.get_turns(session_id)
    assert len(remaining_turns) == 1
    assert remaining_turns[0].turn_number == 1
    print("✓ Only turn 1 remains")
    
    # Verify session turn_count updated
    session = repo.get_session(session_id)
    assert session.turn_count == 1
    print("✓ Session turn_count updated to 1")


def test_turn_relationship(db_manager):
    """Test the relationship between GameSession and Turn."""
    print("\n=== Test 9: Turn-Session Relationship ===")
    
    from src.database.models import GameSession, Turn
    
    # Create a session with turns
    player_info = {"player1": {"position": [0, 0], "UID": "player1", "model": "mock"}}
    game = Game(player_info, dm_info={"model": "mock"})
    
    repo = GameRepository(db_manager)
    session = repo.save_game(game, session_name="Relationship Test")
    
    # Add turns
    for i in range(1, 4):
        repo.save_turn(game, session.id, i)
    
    # Verify relationship via SQLAlchemy
    with db_manager.session_scope() as db_session:
        loaded_session = db_session.query(GameSession).filter(
            GameSession.id == session.id
        ).first()
        
        # Access turns via relationship
        assert len(loaded_session.turns) == 3
        print(f"✓ Session has {len(loaded_session.turns)} turns via relationship")
        
        # Verify each turn has back-reference to session
        for turn in loaded_session.turns:
            assert turn.game_session_id == session.id
            assert turn.game_session.id == session.id
        print("✓ Turn back-references verified")
    
    # Test cascade delete
    deleted = repo.delete_session(session.id)
    assert deleted
    print("✓ Session deleted")
    
    # Verify turns were also deleted (cascade)
    with db_manager.session_scope() as db_session:
        orphaned_turns = db_session.query(Turn).filter(
            Turn.game_session_id == session.id
        ).count()
        assert orphaned_turns == 0
        print("✓ Turns cascade-deleted with session")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Database Layer Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Database creation
        db_manager = test_database_creation()
        
        # Test 2: GameSession model
        test_session_id = test_game_session_model(db_manager)
        
        # Test 3: Repository save/load
        repo_session_id = test_game_repository_save_and_load(db_manager)
        
        # Test 4: Repository update
        test_game_repository_update(db_manager, repo_session_id)
        
        # Test 5: List and delete
        test_repository_list_and_delete(db_manager)
        
        # Test 6: Tiles storage
        test_tiles_in_game_state(db_manager)
        
        # Test 7: Turn tracking (NEW)
        turn_test_session_id = test_turn_tracking(db_manager)
        
        # Test 8: Turn rollback (NEW)
        test_turn_rollback(db_manager, turn_test_session_id)
        
        # Test 9: Turn-session relationship (NEW)
        test_turn_relationship(db_manager)
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED!")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# Database Layer Documentation

This directory contains the SQLite database implementation using SQLAlchemy ORM for game state persistence.

## Architecture

### Files

- **`models.py`** - SQLAlchemy ORM models
  - `GameSession`: Stores complete game state as JSON
  - `Turn`: Stores game state snapshot for each turn (one-to-many with GameSession)

- **`db.py`** - Database engine and session management
  - `DatabaseManager`: Handles SQLite connections and transactions
  - `get_db_manager()`: Singleton accessor for global database instance
  - `get_session()`: Quick access to database sessions

- **`game_repository.py`** - Repository pattern for CRUD operations
  - `GameRepository`: High-level interface for game persistence
  - Session methods: `save_game()`, `load_game()`, `list_sessions()`, `delete_session()`, etc.
  - Turn methods: `save_turn()`, `get_turns()`, `load_game_from_turn()`, `delete_turns_after()`, etc.

- **`fileManager.py`** - Legacy file-based persistence (preserved for compatibility)

## Database Schema

### GameSession Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key (auto-increment) |
| `name` | String(255) | Optional session name |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |
| `game_state` | Text | JSON blob with complete game state |
| `turn_count` | Integer | Number of turns played |
| `num_players` | Integer | Number of players in game |

### Turn Table (NEW)

Stores historical snapshots of game state for each turn.

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key (auto-increment) |
| `game_session_id` | Integer | Foreign key to `game_sessions.id` |
| `turn_number` | Integer | Turn number (1-indexed) |
| `created_at` | DateTime | When this turn was saved |
| `game_state` | Text | JSON snapshot of complete game state |
| `verdict` | Text | Optional DM verdict/narration for this turn |

**Relationship**: One GameSession has many Turns (cascade delete)

### Game State JSON Structure

The `game_state` column contains a JSON blob with:
```json
{
  "players": {
    "player1": {
      "UID": "player1",
      "position": [0, 0],
      "player_class": "human",
      "model": "gpt-4.1-nano",
      "values": {"money": 100, "health": 100}
    }
  },
  "dm": {
    "model": "gpt-4.1-nano"
  },
  "tiles": [
    {
      "position": [0, 0],
      "description": "A peaceful starting area."
    }
  ]
}
```

## Installation

1. Install SQLAlchemy (already added to requirements.txt):
```bash
pip install -r requirements.txt
```

2. The database will be created automatically at `data/game_state.db` on first use.

## Usage Examples

### Basic Usage

```python
from src.database.game_repository import GameRepository
from src.app.Game import Game

# Create a repository
repo = GameRepository()

# Create a game
player_info = {
    "player1": {
        "position": [0, 0],
        "UID": "player1",
        "model": "gpt-4.1-nano",
        "player_class": "human",
        "values": {"money": 0, "health": 100}
    }
}
game = Game(player_info)

# Save to database
session = repo.save_game(game, session_name="My First Game")
print(f"Game saved with ID: {session.id}")

# Load from database
loaded_game = repo.load_game(session.id)
```

### Updating an Existing Game

```python
# Load game
game = repo.load_game(session_id=1)

# Modify game state
game.players["player1"].values.update_money(50)
game.players["player1"].update_position((1, 0))

# Save changes (updates existing session)
repo.save_game(game, session_id=1)
```

### Listing All Games

```python
# Get all sessions
sessions = repo.list_sessions()

for session in sessions:
    print(f"Session {session.id}: {session.name}")
    print(f"  Players: {session.num_players}")
    print(f"  Updated: {session.updated_at}")
```

### Deleting a Game

```python
# Delete by ID
deleted = repo.delete_session(session_id=1)
print(f"Deleted: {deleted}")
```

### Turn Tracking (NEW)

Track game state progression through turns:

```python
# Create a game session
game = Game(player_info)
session = repo.save_game(game, session_name="Campaign 1")

# Play turns and save each one
for turn_num in range(1, 6):
    # Simulate gameplay
    game.players["player1"].values.update_money(25)
    
    # Save turn snapshot
    repo.save_turn(
        game,
        session_id=session.id,
        turn_number=turn_num,
        verdict="Player moved forward and found treasure"
    )

# Get all turns for a session
turns = repo.get_turns(session.id)
print(f"Recorded {len(turns)} turns")

# Load game state from a specific turn
game_turn_3 = repo.load_game_from_turn(session.id, turn_number=3)

# Get the latest turn
latest_turn = repo.get_latest_turn(session.id)
print(f"Latest turn: {latest_turn.turn_number}")
```

### Turn Replay

Replay a game from any point:

```python
# Get specific turn
turn = repo.get_turn(session_id=1, turn_number=5)
print(f"Turn {turn.turn_number}: {turn.verdict}")

# Load game at that turn
game_at_turn_5 = repo.load_game_from_turn(session_id=1, turn_number=5)

# Rollback to earlier turn (delete later turns)
deleted_count = repo.delete_turns_after(session_id=1, turn_number=5)
print(f"Deleted {deleted_count} turns after turn 5")
```

### Advanced: Custom Database Path

```python
from src.database.db import DatabaseManager
from src.database.game_repository import GameRepository

# Use custom database location
db_manager = DatabaseManager("custom/path/game.db")
repo = GameRepository(db_manager)
```

### Advanced: Direct Session Management

```python
from src.database.db import get_db_manager

db_manager = get_db_manager()

# Manual transaction control
with db_manager.session_scope() as session:
    # Perform operations
    game_session = session.query(GameSession).filter_by(id=1).first()
    # Changes are automatically committed at the end of the block
```

## Testing

Run the test suite to verify the database layer:

```bash
python3 testing/test_database.py
```

The test suite covers:
- Database creation and initialization
- GameSession model operations
- Repository save/load functionality
- Game state updates
- Session listing and deletion
- Tile storage within game state
- Turn tracking and history (NEW)
- Turn rollback functionality (NEW)
- Turn-session relationship and cascade delete (NEW)

## Design Decisions

### Why JSON Storage?

We use a JSON blob approach for game state storage because:

1. **Simplicity**: One write operation saves the entire game
2. **Flexibility**: Easy to add new game state fields without migrations
3. **Consistency**: Matches the existing `Savable` interface in the codebase
4. **Performance**: Sufficient for turn-based games with moderate state size

### Alternative: Normalized Schema

For larger games or analytics needs, consider normalizing to separate tables:
- `players` table with foreign key to `game_sessions`
- `tiles` table with foreign key to `game_sessions`
- Enables efficient queries like "find all games where player has >1000 money"

This can be added later without breaking existing code.

### Turn Tracking Design

Each turn stores a complete snapshot of the game state:

**Benefits:**
- **Time travel**: Load game from any past turn
- **Replay**: Review entire game history
- **Debugging**: Inspect state at specific points
- **Rollback**: Undo turns if needed

**Trade-offs:**
- **Storage**: Each turn duplicates full game state (mitigated by SQLite compression)
- **Write cost**: One insert per turn (fast for SQLite)

**Alternative approaches:**
- **Delta storage**: Store only changes between turns (more complex, harder to query)
- **Periodic snapshots**: Store every Nth turn (lose granularity)

The full snapshot approach was chosen for simplicity and reliability.

## Migration from File-Based Storage

The original `fileManager.py` is preserved for backward compatibility. To migrate:

```python
from src.database.fileManager import FileManager
from src.database.game_repository import GameRepository
from src.app.Game import Game

# Load from old JSON file
file_manager = FileManager()
game_dict = file_manager.loadJSON("game_save.json")

# Create game from loaded data
game = Game(game_dict["players"], dm_info=game_dict.get("dm"))
game.load(game_dict)

# Save to database
repo = GameRepository()
repo.save_game(game, session_name="Migrated Game")
```

## Database Location

By default, the database is created at:
- **Path**: `data/game_state.db`
- **Relative to**: Backend root directory

This directory is created automatically if it doesn't exist.

## Thread Safety

The database layer uses SQLAlchemy's connection pooling with `StaticPool` configured for SQLite. Each operation gets its own session via `session_scope()` context manager, ensuring thread-safe transactions.

## Future Enhancements

Potential improvements:
- [ ] Add database migrations with Alembic
- [ ] Implement query methods (e.g., find games by player count, date range)
- [ ] Add indexes for common queries (game_session_id + turn_number)
- [ ] Support for PostgreSQL/MySQL in production
- [ ] Automatic backup/restore functionality
- [ ] Turn analysis (avg money per turn, player progression stats)
- [ ] Turn compression (optional delta encoding for very long games)
- [ ] Turn annotations (player notes, bookmarks)

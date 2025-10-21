# Storage Abstraction Layer

This module provides a flexible storage abstraction layer that enables seamless switching between different datastore implementations.

## Features

- **Pluggable Storage Backends**: Easy switching between file-based and Supabase storage
- **Protocol-Based Interfaces**: Type-safe storage adapter contracts
- **Environment-Based Configuration**: Simple configuration via environment variables
- **No Code Changes Required**: Switch storage backends without modifying service code

## Supported Storage Backends

### 1. File Storage (Default)
- **Type**: `file`
- **Description**: JSON file-based storage in the local filesystem
- **Use Case**: Development, testing, single-machine deployments
- **Configuration**:
  ```bash
  STORAGE_TYPE=file
  FILE_DATA_DIR=/path/to/data  # Optional, defaults to backend/data
  ```

### 2. Supabase Storage
- **Type**: `supabase`
- **Description**: PostgreSQL-backed storage via Supabase
- **Use Case**: Production, full-stack applications, multi-user environments
- **Configuration**:
  ```bash
  STORAGE_TYPE=supabase
  SUPABASE_URL=https://your-project.supabase.co
  SUPABASE_KEY=your-anon-or-service-key
  SUPABASE_GAMES_TABLE=games      # Optional, defaults to "games"
  SUPABASE_PLAYERS_TABLE=players  # Optional, defaults to "players"
  SUPABASE_TILES_TABLE=tiles      # Optional, defaults to "tiles"
  ```

## Usage

### Basic Usage

The storage abstraction layer is automatically used by all database services. No code changes are required in your application code.

```python
from services.database import gameService, playerService, tileService

# All of these automatically use the configured storage backend
game = gameService.load_game_from_database(game_id)
player = playerService.load_player_from_database(player_id)
tiles = tileService.get_all_tiles_from_database()
```

### Advanced Usage

If you need direct access to storage adapters:

```python
from services.storage import get_storage_factory

# Get storage factory
factory = get_storage_factory()

# Create storage adapters
game_storage = factory.create_game_storage()
player_storage = factory.create_player_storage()
tile_storage = factory.create_tile_storage()

# Use storage adapters directly
game = game_storage.load("game_123")
games = game_storage.get_all()
game_storage.save(game_model)
```

### Custom Configuration

For testing or custom setups:

```python
from services.storage import StorageConfig, StorageFactory, set_storage_factory

# Create custom configuration
config = StorageConfig()
config.storage_type = "file"
config.file_data_dir = "/custom/path"

# Create and set custom factory
factory = StorageFactory(config)
set_storage_factory(factory)
```

## Setting Up Supabase

To use Supabase storage, you need to:

1. **Create a Supabase Project**: Visit [supabase.com](https://supabase.com) and create a new project

2. **Create Tables**: Run the following SQL in your Supabase SQL editor:

```sql
-- Games table
CREATE TABLE games (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,
    game_state JSONB NOT NULL,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

-- Players table
CREATE TABLE players (
    uid TEXT PRIMARY KEY,
    position INTEGER[] NOT NULL,
    model TEXT NOT NULL,
    player_class TEXT NOT NULL,
    values JSONB NOT NULL,
    responses TEXT[] NOT NULL
);

-- Tiles table
CREATE TABLE tiles (
    tile_id TEXT PRIMARY KEY,
    position INTEGER[] NOT NULL,
    description TEXT
);

-- Optional: Create indexes for better performance
CREATE INDEX idx_games_status ON games(status);
CREATE INDEX idx_players_position ON players USING GIN(position);
CREATE INDEX idx_tiles_position ON tiles USING GIN(position);
```

3. **Get Your Credentials**:
   - Navigate to Project Settings → API
   - Copy your Project URL and anon/service key

4. **Install Dependencies**:
```bash
pip install supabase
```

5. **Set Environment Variables**:
```bash
export STORAGE_TYPE=supabase
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_KEY=your-key
```

## Environment Setup

### Development (.env file)

Create a `.env` file in your backend directory:

```bash
# File Storage (Development)
STORAGE_TYPE=file
FILE_DATA_DIR=./data

# OR Supabase Storage (Production)
# STORAGE_TYPE=supabase
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your-anon-key
# SUPABASE_GAMES_TABLE=games
# SUPABASE_PLAYERS_TABLE=players
# SUPABASE_TILES_TABLE=tiles
```

### Production

Set environment variables in your deployment platform:
- Heroku: `heroku config:set STORAGE_TYPE=supabase ...`
- Docker: Use environment variables in docker compose.yml or Dockerfile
- AWS/GCP/Azure: Configure through platform-specific environment variable settings

## Architecture

```
services/storage/
├── __init__.py                    # Public API exports
├── storage_adapter.py             # Protocol definitions (interfaces)
├── file_storage_adapter.py        # File-based implementation
├── supabase_storage_adapter.py    # Supabase implementation
├── storage_factory.py             # Factory for creating adapters
└── README.md                      # This file

services/database/
├── gameService.py                 # Uses storage abstraction
├── playerService.py               # Uses storage abstraction
└── tileService.py                 # Uses storage abstraction
```

## Adding New Storage Backends

To add a new storage backend:

1. **Create Adapter Implementation**: Create a new file like `mongodb_storage_adapter.py`
2. **Implement Protocols**: Implement `GameStorageAdapter`, `PlayerStorageAdapter`, and `TileStorageAdapter`
3. **Update Factory**: Add your implementation to `storage_factory.py`
4. **Update Config**: Add configuration options to `StorageConfig`

Example:
```python
# mongodb_storage_adapter.py
class MongoDBGameStorageAdapter:
    def __init__(self, connection_string: str):
        self.client = MongoClient(connection_string)
    
    def save(self, game: GameModel) -> str:
        # Implementation
        pass
    
    def load(self, game_id: str) -> GameModel:
        # Implementation
        pass
    # ... other methods

# Add to storage_factory.py
def create_game_storage(self):
    if self.config.storage_type == "mongodb":
        return MongoDBGameStorageAdapter(
            connection_string=self.config.mongodb_connection_string
        )
    # ... existing implementations
```

## Testing

The storage abstraction layer makes testing easier:

```python
from services.storage import StorageConfig, StorageFactory, set_storage_factory

# Use file storage for tests
config = StorageConfig()
config.storage_type = "file"
config.file_data_dir = "/tmp/test_data"

factory = StorageFactory(config)
set_storage_factory(factory)

# Run your tests...
```

## Troubleshooting

### Issue: "Supabase client not available"
**Solution**: Install the supabase package: `pip install supabase`

### Issue: "SUPABASE_URL and SUPABASE_KEY must be set"
**Solution**: Ensure environment variables are set correctly

### Issue: File permission errors
**Solution**: Ensure the data directory has proper write permissions

### Issue: Supabase connection errors
**Solution**: 
- Verify your Supabase URL and key are correct
- Check network connectivity
- Ensure your Supabase project is active

## License

This module is part of the AgenticAI project.

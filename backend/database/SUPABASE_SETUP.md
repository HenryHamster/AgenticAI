# Supabase Setup Guide

This guide walks you through setting up your Supabase database for AgenticAI.

## Quick Setup (5 minutes)

### Step 1: Create a Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign in or create an account
3. Click **"New Project"**
4. Fill in project details:
   - **Name**: AgenticAI (or your preferred name)
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Choose closest to your users
5. Click **"Create new project"** and wait ~2 minutes for provisioning

### Step 2: Get Your Credentials

1. In your Supabase dashboard, go to **Settings** → **API**
2. Copy these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: For frontend/public access
   - **service_role key**: For backend access (⚠️ keep secret!)

### Step 3: Initialize the Database

**Option A: Using Supabase Dashboard (Recommended)**

1. In your Supabase dashboard, go to **SQL Editor**
2. Click **"New Query"**
3. Copy the contents of `backend/database/supabase_schema.sql`
4. Paste into the SQL editor
5. Click **"Run"** (or press Cmd+Enter / Ctrl+Enter)
6. ✅ You should see success messages for all tables

**Option B: Using Supabase CLI**

```bash
# Install Supabase CLI
npm install -g supabase

# Login
supabase login

# Link to your project
supabase link --project-ref your-project-ref

# Run migrations
supabase db push
```

### Step 4: Configure Your Application

1. Copy the example environment file:
   ```bash
   cp backend/.env.example backend/.env
   ```

2. Edit `backend/.env` and add your Supabase credentials:
   ```bash
   STORAGE_TYPE=supabase
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=your-service-role-key  # Use service_role key for backend!
   ```

3. Install the Supabase Python client:
   ```bash
   pip install supabase
   ```

### Step 5: Verify the Setup

Run this Python script to test the connection:

```python
from services.storage import get_storage_factory, StorageConfig

# Test connection
factory = get_storage_factory()
game_storage = factory.create_game_storage()

# Should work without errors
print("✅ Supabase connection successful!")
```

Or from your application:
```python
from services.database import gameService, turnService
from schema.gameModel import GameModel, GameStateModel
from schema.turnModel import TurnModel

# Create a test game
test_game = GameModel(
    id="test-game-1",
    name="Test Game",
    status="active"
)

# Save to Supabase
game_id = gameService.save_game_to_database(test_game)
print(f"✅ Game saved: {game_id}")

# Create initial turn with game state
initial_turn = TurnModel(
    game_id=game_id,
    turn_number=0,
    game_state=GameStateModel()
)
turn_id = turnService.save_turn_to_database(initial_turn)
print(f"✅ Initial turn saved: {turn_id}")

# Load back
loaded_game = gameService.load_game_from_database(game_id)
print(f"✅ Game loaded: {loaded_game.name}")
```

## Database Schema Overview

The schema creates four main tables:

### 📦 `games` Table
- **id** (TEXT): Primary key, game identifier
- **name** (TEXT): Game name
- **description** (TEXT): Game description
- **status** (TEXT): Game status (pending, active, completed, error, etc.)
- **model** (TEXT): AI model used (default: 'mock')
- **world_size** (INTEGER): World grid size (default: 1)
- **winner_player_name** (TEXT): Name of winning player (if any)
- **currency_target** (INTEGER): Currency needed to win
- **max_turns** (INTEGER): Maximum number of turns
- **total_players** (INTEGER): Total number of players
- **starting_currency** (INTEGER): Starting currency for each player (default: 0)
- **starting_health** (INTEGER): Starting health for each player (default: 100)
- **player_configs** (JSONB): Individual player configurations (name, starting_health, starting_currency per player)
- **game_duration** (INTERVAL): Game duration
- **created_at** (TIMESTAMPTZ): Timestamp
- **updated_at** (TIMESTAMPTZ): Auto-updated timestamp

### 🔄 `turns` Table
- **id** (BIGSERIAL): Primary key, auto-incrementing turn ID
- **game_id** (TEXT): Foreign key to games table
- **turn_number** (INTEGER): Sequential turn number within a game
- **game_state** (JSONB): Full game state snapshot for this turn
- **created_at** (TIMESTAMPTZ): Timestamp
- **Indexes**: Optimized for querying turns by game_id and turn_number
- **Constraint**: Unique combination of (game_id, turn_number)

### 👤 `players` Table
- **uid** (TEXT): Primary key, player identifier
- **position** (INTEGER[]): Player position [x, y]
- **model** (TEXT): AI model used
- **player_class** (TEXT): Player class
- **values** (JSONB): Player stats (health, money, etc.)
- **responses** (TEXT[]): Array of player responses
- **created_at** (TIMESTAMPTZ): Timestamp
- **updated_at** (TIMESTAMPTZ): Auto-updated timestamp

### 🗺️ `tiles` Table
- **tile_id** (TEXT): Primary key, tile identifier
- **position** (INTEGER[]): Tile position [x, y]
- **description** (TEXT): Tile description
- **created_at** (TIMESTAMPTZ): Timestamp
- **updated_at** (TIMESTAMPTZ): Auto-updated timestamp

## Security Notes

### Row Level Security (RLS)

The schema includes basic RLS policies:
- **Public read access**: Anyone can read data (adjust as needed)
- **Service role full access**: Your backend has full CRUD access

### Recommended for Production:

1. **Use service_role key** for backend operations (has full access)
2. **Use anon key** for frontend operations (restricted by RLS policies)
3. **Customize RLS policies** based on your auth requirements:

```sql
-- Example: Only authenticated users can read
DROP POLICY "Allow public read access on games" ON games;

CREATE POLICY "Allow authenticated read access on games"
    ON games FOR SELECT
    TO authenticated
    USING (true);

-- Example: Users can only modify their own data
CREATE POLICY "Users can update their own players"
    ON players FOR UPDATE
    TO authenticated
    USING (auth.uid() = uid)
    WITH CHECK (auth.uid() = uid);
```

## Useful Supabase Features

### Real-time Subscriptions

Enable real-time for multiplayer features:

```python
# In your frontend/client code
# Subscribe to new turns for live game updates
supabase.channel('turn-updates')
  .on('postgres_changes', 
      { event: 'INSERT', schema: 'public', table: 'turns' },
      (payload) => console.log('New turn:', payload))
  .subscribe()

# Subscribe to game status changes
supabase.channel('game-updates')
  .on('postgres_changes', 
      { event: '*', schema: 'public', table: 'games' },
      (payload) => console.log('Game updated:', payload))
  .subscribe()
```

### Database Backups

1. Go to **Database** → **Backups**
2. Supabase automatically creates daily backups (free tier: 7 days retention)
3. You can restore to any backup point

### Performance Monitoring

1. Go to **Database** → **Query Performance**
2. Monitor slow queries
3. Add indexes as needed

## Troubleshooting

### Connection Error: "Invalid API key"
- ✅ Make sure you're using the **service_role** key for backend
- ✅ Check that your key doesn't have extra spaces

### Connection Error: "Failed to connect"
- ✅ Verify your `SUPABASE_URL` is correct
- ✅ Check your internet connection
- ✅ Verify your Supabase project is active

### Import Error: "No module named 'supabase'"
```bash
pip install supabase
```

### Table Already Exists
- The schema uses `CREATE TABLE IF NOT EXISTS`, so it's safe to re-run
- To start fresh: Drop tables in Supabase dashboard → Database → Tables

### RLS Blocking Operations
- If operations fail with permission errors, temporarily disable RLS:
```sql
ALTER TABLE games DISABLE ROW LEVEL SECURITY;
```

## Migration from File Storage

Your existing file data can be migrated:

```python
from services.storage import FileGameStorageAdapter, SupabaseGameStorageAdapter
import os

# Setup adapters
file_storage = FileGameStorageAdapter()
supabase_storage = SupabaseGameStorageAdapter(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_KEY")
)

# Migrate all games
games = file_storage.get_all()
for game in games:
    supabase_storage.save(game)
    print(f"Migrated: {game.id}")

print(f"✅ Migrated {len(games)} games to Supabase")
```

## Next Steps

1. ✅ Complete the setup above
2. 📚 Read the [Storage Abstraction Layer README](../services/storage/README.md)
3. 🧪 Test with sample data
4. 🚀 Deploy your application with Supabase backend

## Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [PostgreSQL JSON Functions](https://www.postgresql.org/docs/current/functions-json.html)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)

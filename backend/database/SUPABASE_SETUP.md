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

# Supabase Quick Start Guide

## 🚀 Initialize Your Supabase Database (5 minutes)

### Method 1: Via Supabase Dashboard (Easiest)

1. **Login to Supabase**
   - Go to [supabase.com](https://supabase.com) and login
   - Select your project

2. **Run the Schema**
   - Click **SQL Editor** in the left sidebar
   - Click **New Query**
   - Copy all contents from `backend/database/supabase_schema.sql`
   - Paste into the editor
   - Click **RUN** or press `Cmd+Enter` / `Ctrl+Enter`
   - ✅ You should see success messages

3. **Get Your Credentials**
   - Go to **Settings** → **API**
   - Copy:
     - **Project URL**: `https://xxxxx.supabase.co`
     - **service_role** secret key (⚠️ keep this secret!)

4. **Configure Your App**
   ```bash
   # Create .env file
   cp backend/.env.example backend/.env
   
   # Edit backend/.env and add:
   STORAGE_TYPE=supabase
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=your-service-role-key-here
   ```

5. **Install Supabase Client**
   ```bash
   pip install supabase
   ```

6. **Verify Setup**
   ```bash
   make supabase-setup-check
   make storage-status
   ```

### Method 2: Using Makefile Commands

```bash
# View instructions
make supabase-init

# Check your configuration
make supabase-setup-check

# View current storage status
make storage-status

# Open full documentation
make supabase-docs
```

## 📋 SQL Schema Summary

The schema creates:
- ✅ **3 tables**: `games`, `players`, `tiles`
- ✅ **Indexes** for performance
- ✅ **Auto-updating timestamps**
- ✅ **Row Level Security (RLS)** policies
- ✅ **Helpful views** for querying

## 🔧 Environment Variables

```bash
# Supabase Configuration
STORAGE_TYPE=supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# Optional: Custom table names
SUPABASE_GAMES_TABLE=games
SUPABASE_PLAYERS_TABLE=players
SUPABASE_TILES_TABLE=tiles
```

## ✅ Verify Everything Works

```python
# Test in Python
from services.database import gameService
from schema.gameModel import GameModel, GameStateModel

# Create a test game
game = GameModel(
    id="test-1",
    name="Test Game",
    status="active",
    game_state=GameStateModel()
)

# Save to Supabase
game_id = gameService.save_game_to_database(game)
print(f"✅ Saved: {game_id}")

# Load it back
loaded = gameService.load_game_from_database(game_id)
print(f"✅ Loaded: {loaded.name}")
```

Or use the Makefile:
```bash
make storage-status
```

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid API key" | Make sure you're using the **service_role** key, not anon key |
| "Module not found: supabase" | Run: `pip install supabase` |
| "Failed to connect" | Check your `SUPABASE_URL` is correct |
| Tables already exist | The schema uses `IF NOT EXISTS`, safe to re-run |

## 📚 Full Documentation

- **Setup Guide**: `backend/database/SUPABASE_SETUP.md`
- **Storage Docs**: `backend/services/storage/README.md`
- **Migration Guide**: `backend/services/storage/MIGRATION_GUIDE.md`
- **SQL Schema**: `backend/database/supabase_schema.sql`

## 🎯 What's Next?

1. ✅ Initialize database (above)
2. 🧪 Test with sample data
3. 🚀 Deploy your app
4. 📊 Monitor in Supabase dashboard

## 💡 Pro Tips

- Use **service_role key** for backend operations
- Enable real-time subscriptions for multiplayer features
- Check **Database → Query Performance** for optimization
- Supabase provides automatic daily backups

---

**Need Help?** Check the full setup guide: `backend/database/SUPABASE_SETUP.md`

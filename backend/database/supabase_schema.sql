-- Supabase Database Schema for AgenticAI
-- Run this in your Supabase SQL Editor to initialize the database

-- ==============================================
-- Games Table
-- ==============================================
CREATE TABLE IF NOT EXISTS games (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL DEFAULT 'Untitled Game',
    description TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active',
    world_size INTEGER NOT NULL DEFAULT 1,
    winner_player_name TEXT,
    currency_target INTEGER,
    number_of_turns INTEGER,
    total_players INTEGER,
    game_duration INTERVAL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster status filtering
CREATE INDEX IF NOT EXISTS idx_games_status ON games(status);

-- Index for faster date sorting
CREATE INDEX IF NOT EXISTS idx_games_created_at ON games(created_at DESC);

-- Trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_games_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_games_updated_at ON games;

CREATE TRIGGER trigger_games_updated_at
    BEFORE UPDATE ON games
    FOR EACH ROW
    EXECUTE FUNCTION update_games_updated_at();

-- ==============================================
-- Turns Table
-- ==============================================
CREATE TABLE IF NOT EXISTS turns (
    id BIGSERIAL PRIMARY KEY,
    game_id TEXT NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    turn_number INTEGER NOT NULL,
    game_state JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(game_id, turn_number)
);

-- Index for faster game_id filtering
CREATE INDEX IF NOT EXISTS idx_turns_game_id ON turns(game_id);

-- Index for faster turn_number sorting per game
CREATE INDEX IF NOT EXISTS idx_turns_game_turn ON turns(game_id, turn_number DESC);

-- Index for faster date sorting
CREATE INDEX IF NOT EXISTS idx_turns_created_at ON turns(created_at DESC);

-- ==============================================
-- Players Table
-- ==============================================
CREATE TABLE IF NOT EXISTS players (
    uid TEXT PRIMARY KEY,
    position INTEGER[] NOT NULL,
    model TEXT NOT NULL DEFAULT 'gpt-4.1-nano',
    player_class TEXT NOT NULL DEFAULT 'human',
    values JSONB NOT NULL DEFAULT '{"money": 0, "health": 100}'::jsonb,
    responses TEXT[] NOT NULL DEFAULT '{}'::text[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for spatial queries (if you need to find players by position)
CREATE INDEX IF NOT EXISTS idx_players_position ON players USING GIN(position);

-- Index for filtering by class
CREATE INDEX IF NOT EXISTS idx_players_class ON players(player_class);

-- Trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_players_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_players_updated_at ON players;

CREATE TRIGGER trigger_players_updated_at
    BEFORE UPDATE ON players
    FOR EACH ROW
    EXECUTE FUNCTION update_players_updated_at();

-- ==============================================
-- Tiles Table
-- ==============================================
CREATE TABLE IF NOT EXISTS tiles (
    tile_id TEXT PRIMARY KEY,
    position INTEGER[] NOT NULL,
    description TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for spatial queries
CREATE INDEX IF NOT EXISTS idx_tiles_position ON tiles USING GIN(position);

-- Unique constraint to prevent duplicate positions (using btree for uniqueness)
CREATE UNIQUE INDEX IF NOT EXISTS idx_tiles_position_unique ON tiles(position);

-- Trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_tiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_tiles_updated_at ON tiles;

CREATE TRIGGER trigger_tiles_updated_at
    BEFORE UPDATE ON tiles
    FOR EACH ROW
    EXECUTE FUNCTION update_tiles_updated_at();

-- ==============================================
-- Row Level Security (RLS) Policies
-- ==============================================

-- Disable RLS on all tables (for development/testing)
ALTER TABLE games DISABLE ROW LEVEL SECURITY;
ALTER TABLE turns DISABLE ROW LEVEL SECURITY;
ALTER TABLE players DISABLE ROW LEVEL SECURITY;
ALTER TABLE tiles DISABLE ROW LEVEL SECURITY;

-- Public read access (adjust based on your security requirements)
DROP POLICY IF EXISTS "Allow public read access on games" ON games;

CREATE POLICY "Allow public read access on games"
    ON games FOR SELECT
    TO public
    USING (true);

DROP POLICY IF EXISTS "Allow public read access on turns" ON turns;

CREATE POLICY "Allow public read access on turns"
    ON turns FOR SELECT
    TO public
    USING (true);

DROP POLICY IF EXISTS "Allow public read access on players" ON players;

CREATE POLICY "Allow public read access on players"
    ON players FOR SELECT
    TO public
    USING (true);

DROP POLICY IF EXISTS "Allow public read access on tiles" ON tiles;

CREATE POLICY "Allow public read access on tiles"
    ON tiles FOR SELECT
    TO public
    USING (true);

-- Service role full access (for your backend)
-- Note: The service role bypasses RLS by default, but we can be explicit
DROP POLICY IF EXISTS "Allow service role full access on games" ON games;

CREATE POLICY "Allow service role full access on games"
    ON games FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS "Allow service role full access on turns" ON turns;

CREATE POLICY "Allow service role full access on turns"
    ON turns FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS "Allow service role full access on players" ON players;

CREATE POLICY "Allow service role full access on players"
    ON players FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS "Allow service role full access on tiles" ON tiles;

CREATE POLICY "Allow service role full access on tiles"
    ON tiles FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- ==============================================
-- Optional: Helpful Views
-- ==============================================

-- View for active games with latest turn info
DROP VIEW IF EXISTS active_games;

CREATE VIEW active_games AS
SELECT 
    g.id,
    g.name,
    g.description,
    g.status,
    g.created_at,
    g.updated_at,
    COALESCE(
        (SELECT MAX(turn_number) FROM turns WHERE game_id = g.id),
        0
    ) as latest_turn_number
FROM games g
WHERE status = 'active'
ORDER BY created_at DESC;

-- ==============================================
-- Optional: Sample Data (for testing)
-- ==============================================

-- Uncomment to insert sample data
-- INSERT INTO games (id, name, description, status)
-- VALUES (
--     'sample-game-1',
--     'Sample Adventure',
--     'A sample game for testing',
--     'active'
-- );
--
-- INSERT INTO turns (game_id, turn_number, game_state)
-- VALUES (
--     'sample-game-1',
--     0,
--     '{
--         "players": {},
--         "dm": {},
--         "tiles": [],
--         "player_responses": {},
--         "dungeon_master_verdict": ""
--     }'::jsonb
-- );

-- ==============================================
-- Verification Queries
-- ==============================================

-- Run these to verify your setup
-- SELECT * FROM games;
-- SELECT * FROM players;
-- SELECT * FROM tiles;

-- Check table structures
-- SELECT 
--     table_name,
--     column_name,
--     data_type,
--     is_nullable
-- FROM information_schema.columns
-- WHERE table_schema = 'public'
--     AND table_name IN ('games', 'players', 'tiles')
-- ORDER BY table_name, ordinal_position;

-- ==============================================
-- Database Migrations (for existing databases)
-- ==============================================

-- Add world_size column if it doesn't exist (safe for existing databases)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'games' 
        AND column_name = 'world_size'
    ) THEN
        ALTER TABLE games ADD COLUMN world_size INTEGER NOT NULL DEFAULT 1;
    END IF;
END $$;

-- Add winner_player_name column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'games' 
        AND column_name = 'winner_player_name'
    ) THEN
        ALTER TABLE games ADD COLUMN winner_player_name TEXT;
    END IF;
END $$;

-- Add currency_target column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'games' 
        AND column_name = 'currency_target'
    ) THEN
        ALTER TABLE games ADD COLUMN currency_target INTEGER;
    END IF;
END $$;

-- Add number_of_turns column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'games' 
        AND column_name = 'number_of_turns'
    ) THEN
        ALTER TABLE games ADD COLUMN number_of_turns INTEGER;
    END IF;
END $$;

-- Add total_players column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'games' 
        AND column_name = 'total_players'
    ) THEN
        ALTER TABLE games ADD COLUMN total_players INTEGER;
    END IF;
END $$;

-- Add game_duration column if it doesn't exist (stored as interval for time duration)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'games' 
        AND column_name = 'game_duration'
    ) THEN
        ALTER TABLE games ADD COLUMN game_duration INTERVAL;
    END IF;
END $$;

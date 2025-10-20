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
    game_state JSONB NOT NULL DEFAULT '{}'::jsonb,
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

CREATE TRIGGER trigger_games_updated_at
    BEFORE UPDATE ON games
    FOR EACH ROW
    EXECUTE FUNCTION update_games_updated_at();

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

CREATE TRIGGER trigger_tiles_updated_at
    BEFORE UPDATE ON tiles
    FOR EACH ROW
    EXECUTE FUNCTION update_tiles_updated_at();

-- ==============================================
-- Row Level Security (RLS) Policies
-- ==============================================

-- Enable RLS on all tables
ALTER TABLE games ENABLE ROW LEVEL SECURITY;
ALTER TABLE players ENABLE ROW LEVEL SECURITY;
ALTER TABLE tiles ENABLE ROW LEVEL SECURITY;

-- Public read access (adjust based on your security requirements)
CREATE POLICY "Allow public read access on games"
    ON games FOR SELECT
    TO public
    USING (true);

CREATE POLICY "Allow public read access on players"
    ON players FOR SELECT
    TO public
    USING (true);

CREATE POLICY "Allow public read access on tiles"
    ON tiles FOR SELECT
    TO public
    USING (true);

-- Service role full access (for your backend)
-- Note: The service role bypasses RLS by default, but we can be explicit
CREATE POLICY "Allow service role full access on games"
    ON games FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow service role full access on players"
    ON players FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow service role full access on tiles"
    ON tiles FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- ==============================================
-- Optional: Helpful Views
-- ==============================================

-- View for active games
CREATE OR REPLACE VIEW active_games AS
SELECT 
    id,
    name,
    description,
    status,
    created_at,
    updated_at,
    jsonb_array_length(game_state->'players') as player_count
FROM games
WHERE status = 'active'
ORDER BY created_at DESC;

-- ==============================================
-- Optional: Sample Data (for testing)
-- ==============================================

-- Uncomment to insert sample data
-- INSERT INTO games (id, name, description, status, game_state)
-- VALUES (
--     'sample-game-1',
--     'Sample Adventure',
--     'A sample game for testing',
--     'active',
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

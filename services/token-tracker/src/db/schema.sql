-- Token Tracker Database Schema

-- Providers (anthropic, kimi, minimax, openai-codex, etc.)
CREATE TABLE IF NOT EXISTS providers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    display_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Models
CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY,
    provider_id INTEGER NOT NULL REFERENCES providers(id),
    model_id TEXT NOT NULL,
    display_name TEXT,
    cost_input_per_1m REAL DEFAULT 0,
    cost_output_per_1m REAL DEFAULT 0,
    cost_cache_read_per_1m REAL DEFAULT 0,
    cost_cache_write_per_1m REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider_id, model_id)
);

-- Sources (openclaw, droid, codex, gemini, claude)
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    display_name TEXT
);

-- Sessions
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    session_id TEXT NOT NULL,
    agent_id TEXT,
    started_at TIMESTAMP,
    cwd TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_id, session_id)
);

-- Usage records (main tracking table)
CREATE TABLE IF NOT EXISTS usage (
    id INTEGER PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(id),
    model_id INTEGER NOT NULL REFERENCES models(id),
    source_id INTEGER NOT NULL REFERENCES sources(id),
    
    -- Token counts
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cache_read_tokens INTEGER DEFAULT 0,
    cache_write_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    
    -- Cost (in USD)
    cost_input REAL DEFAULT 0,
    cost_output REAL DEFAULT 0,
    cost_cache_read REAL DEFAULT 0,
    cost_cache_write REAL DEFAULT 0,
    cost_total REAL DEFAULT 0,
    
    -- Metadata
    stop_reason TEXT,
    message_id TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- For deduplication
    UNIQUE(source_id, session_id, message_id)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_usage_recorded_at ON usage(recorded_at);
CREATE INDEX IF NOT EXISTS idx_usage_model_id ON usage(model_id);
CREATE INDEX IF NOT EXISTS idx_usage_source_id ON usage(source_id);
CREATE INDEX IF NOT EXISTS idx_usage_session_id ON usage(session_id);

-- Daily aggregates (materialized view pattern)
CREATE TABLE IF NOT EXISTS daily_usage (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    model_id INTEGER NOT NULL REFERENCES models(id),
    source_id INTEGER NOT NULL REFERENCES sources(id),
    
    request_count INTEGER DEFAULT 0,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cache_read_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    cost_total REAL DEFAULT 0,
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, model_id, source_id)
);

-- Ingest state for incremental processing
CREATE TABLE IF NOT EXISTS ingest_state (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    file_path TEXT NOT NULL,
    last_position INTEGER DEFAULT 0,
    last_message_id TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source, file_path)
);

-- Seed data: Providers
INSERT OR IGNORE INTO providers (name, display_name) VALUES
    ('anthropic', 'Anthropic'),
    ('kimi', 'Moonshot (Kimi)'),
    ('minimax-portal', 'MiniMax'),
    ('openai-codex', 'OpenAI Codex'),
    ('openai', 'OpenAI'),
    ('google', 'Google');

-- Seed data: Sources
INSERT OR IGNORE INTO sources (name, display_name) VALUES
    ('openclaw', 'OpenClaw Gateway'),
    ('droid', 'Factory Droid'),
    ('codex', 'Codex CLI'),
    ('gemini', 'Gemini CLI'),
    ('claude', 'Claude Code');

-- Seed data: Models
INSERT OR IGNORE INTO models (provider_id, model_id, display_name) 
SELECT p.id, 'claude-opus-4-5-20251101', 'Claude Opus 4.5' FROM providers p WHERE p.name = 'anthropic';
INSERT OR IGNORE INTO models (provider_id, model_id, display_name) 
SELECT p.id, 'kimi-k2-0711', 'Kimi K2.5' FROM providers p WHERE p.name = 'kimi';
INSERT OR IGNORE INTO models (provider_id, model_id, display_name) 
SELECT p.id, 'kimi-for-coding', 'Kimi K2.5 Turbo' FROM providers p WHERE p.name = 'kimi';
INSERT OR IGNORE INTO models (provider_id, model_id, display_name) 
SELECT p.id, 'MiniMax-M2.1', 'MiniMax M2.1' FROM providers p WHERE p.name = 'minimax-portal';
INSERT OR IGNORE INTO models (provider_id, model_id, display_name) 
SELECT p.id, 'MiniMax-M2.1-lightning', 'MiniMax M2.1 Lightning' FROM providers p WHERE p.name = 'minimax-portal';
INSERT OR IGNORE INTO models (provider_id, model_id, display_name) 
SELECT p.id, 'gpt-5.2', 'GPT-5.2' FROM providers p WHERE p.name = 'openai-codex';

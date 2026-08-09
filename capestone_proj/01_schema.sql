-- Schema DDL for AI Stock Market Research Assistant
-- Database: Lakebase (PostgreSQL with pgvector)

CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2. Companies Table
CREATE TABLE IF NOT EXISTS companies (
    ticker TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    sector TEXT,
    industry TEXT,
    description TEXT,
    market_cap NUMERIC,
    pe_ratio NUMERIC,
    dividend_yield NUMERIC,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3. Watchlists Table
CREATE TABLE IF NOT EXISTS watchlists (
    watchlist_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4. Watchlist Tickers Junction Table
CREATE TABLE IF NOT EXISTS watchlist_tickers (
    watchlist_id TEXT NOT NULL REFERENCES watchlists(watchlist_id) ON DELETE CASCADE,
    ticker TEXT NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    target_buy_price NUMERIC,
    target_sell_price NUMERIC,
    notes TEXT,
    added_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (watchlist_id, ticker)
);

-- 5. Price Snapshots Table
CREATE TABLE IF NOT EXISTS price_snapshots (
    id SERIAL PRIMARY KEY,
    ticker TEXT NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    open_price NUMERIC,
    high_price NUMERIC,
    low_price NUMERIC,
    close_price NUMERIC NOT NULL,
    volume BIGINT,
    snapshot_time TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_price_snapshots_ticker_time ON price_snapshots(ticker, snapshot_time DESC);

-- 6. News Articles Table
CREATE TABLE IF NOT EXISTS news_articles (
    article_id TEXT PRIMARY KEY,
    ticker TEXT NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    article_url TEXT,
    publisher TEXT,
    author TEXT,
    published_utc TIMESTAMPTZ,
    sentiment TEXT,
    sentiment_reasoning TEXT,
    synced_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_news_articles_ticker ON news_articles(ticker);

-- 7. News Embeddings Table (pgvector 384 dimensions for sentence-transformers/all-MiniLM-L6-v2)
CREATE TABLE IF NOT EXISTS news_embeddings (
    embedding_id TEXT PRIMARY KEY,
    article_id TEXT NOT NULL REFERENCES news_articles(article_id) ON DELETE CASCADE,
    ticker TEXT NOT NULL,
    chunk_index INT NOT NULL DEFAULT 0,
    chunk_text TEXT NOT NULL,
    embedding VECTOR(384) NOT NULL,
    model_name TEXT NOT NULL DEFAULT 'all-MiniLM-L6-v2',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_news_embeddings_vector 
ON news_embeddings USING hnsw (embedding vector_cosine_ops);

-- 8. Research Notes Table (Agent Action Target)
CREATE TABLE IF NOT EXISTS research_notes (
    note_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    ticker TEXT NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT[],
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 9. Analysis Reports Table (Agent Action Target)
CREATE TABLE IF NOT EXISTS analysis_reports (
    report_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    ticker TEXT NOT NULL REFERENCES companies(ticker) ON DELETE CASCADE,
    recommendation TEXT NOT NULL, -- 'BUY', 'HOLD', 'SELL'
    summary TEXT NOT NULL,
    bull_case TEXT,
    bear_case TEXT,
    generated_by TEXT NOT NULL DEFAULT 'AI_Copilot',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 10. Agent Tool Call Audit Logs Table (Agent & CDF Analytics Target)
CREATE TABLE IF NOT EXISTS agent_tool_calls (
    call_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL DEFAULT 'default_user',
    tool_name TEXT NOT NULL,
    parameters TEXT,
    result_summary TEXT,
    status TEXT NOT NULL DEFAULT 'SUCCESS',
    execution_time_ms NUMERIC DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_agent_tool_calls_tool ON agent_tool_calls(tool_name, created_at DESC);

-- Seed Default User
INSERT INTO users (user_id, username, email)
VALUES ('default_user', 'demo_trader', 'trader@example.com')
ON CONFLICT (user_id) DO NOTHING;

-- Seed Default Watchlist
INSERT INTO watchlists (watchlist_id, user_id, name, description)
VALUES ('default_watchlist', 'default_user', 'Main Portfolio Watchlist', 'Primary stock research watchlist')
ON CONFLICT (watchlist_id) DO NOTHING;

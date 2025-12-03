-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    provider TEXT,
    provider_id TEXT,
    avatar_url TEXT,
    preferences TEXT DEFAULT '{}', -- JSON
    last_login INTEGER, -- Timestamp
    created_at INTEGER DEFAULT (unixepoch()),
    updated_at INTEGER DEFAULT (unixepoch())
);

-- Legislative Bills Table
CREATE TABLE IF NOT EXISTS legislative_bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    stage TEXT NOT NULL,
    jurisdiction TEXT NOT NULL,
    committees TEXT DEFAULT '[]', -- JSON array
    sectors TEXT DEFAULT '[]', -- JSON array
    summary TEXT,
    next_action_date TEXT, -- ISO Date string
    sentiment_score REAL,
    probability_of_enactment REAL,
    last_updated INTEGER DEFAULT (unixepoch()),
    created_at INTEGER DEFAULT (unixepoch()),
    updated_at INTEGER DEFAULT (unixepoch())
);

-- Trade Disclosures Table
CREATE TABLE IF NOT EXISTS trade_disclosures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filing_id TEXT NOT NULL UNIQUE,
    source TEXT DEFAULT 'sec.filings',
    member TEXT NOT NULL,
    chamber TEXT NOT NULL,
    ticker TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    transaction_date INTEGER, -- Timestamp
    amount_range TEXT NOT NULL,
    related_bill TEXT,
    created_at INTEGER DEFAULT (unixepoch()),
    updated_at INTEGER DEFAULT (unixepoch())
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_bills_bill_id ON legislative_bills(bill_id);
CREATE INDEX IF NOT EXISTS idx_trades_ticker ON trade_disclosures(ticker);
CREATE INDEX IF NOT EXISTS idx_trades_member ON trade_disclosures(member);

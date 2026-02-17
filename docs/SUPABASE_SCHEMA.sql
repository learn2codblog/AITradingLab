"""
Database Schema and Setup Script for Supabase
Run this once to create all required tables and RLS policies
"""

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255),
    login_method VARCHAR(50) DEFAULT 'email', -- 'email', 'google', 'microsoft', 'yahoo'
    picture_url TEXT,
    created_at TIMESTAMP DEFAULT current_timestamp,
    updated_at TIMESTAMP DEFAULT current_timestamp,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- User Profiles
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    bio TEXT,
    risk_tolerance VARCHAR(50), -- 'conservative', 'moderate', 'aggressive'
    investment_horizon VARCHAR(50), -- 'short', 'medium', 'long'
    trading_style VARCHAR(50), -- 'day_trading', 'swing', 'position'
    initial_capital DECIMAL(12, 2),
    trading_experience VARCHAR(50), -- 'beginner', 'intermediate', 'advanced'
    notifications_enabled BOOLEAN DEFAULT true,
    dark_mode BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT current_timestamp,
    updated_at TIMESTAMP DEFAULT current_timestamp
);

-- Kite API Credentials
CREATE TABLE IF NOT EXISTS kite_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    api_key VARCHAR(255) NOT NULL,
    api_secret VARCHAR(255) NOT NULL,
    access_token TEXT,
    public_token TEXT,
    is_connected BOOLEAN DEFAULT false,
    connected_at TIMESTAMP,
    disconnected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT current_timestamp,
    updated_at TIMESTAMP DEFAULT current_timestamp
);

-- Activity Logs
CREATE TABLE IF NOT EXISTS activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL, -- 'login', 'trade', 'backtest', 'settings_change', etc
    description TEXT,
    action_details JSONB,
    status VARCHAR(50) DEFAULT 'success', -- 'success', 'pending', 'failed'
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT current_timestamp,
    created_at TIMESTAMP DEFAULT current_timestamp
);

-- Trading Activity (separate from generic activity_logs)
CREATE TABLE IF NOT EXISTS trading_activity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL, -- 'analysis', 'ai_analysis', 'backtest_run', 'screener_run', 'portfolio_update', 'trade'
    symbol VARCHAR(50),
    source VARCHAR(50), -- 'analysis', 'ai', 'backtest', 'screener', 'portfolio'
    details JSONB,
    status VARCHAR(50) DEFAULT 'success',
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT current_timestamp,
    created_at TIMESTAMP DEFAULT current_timestamp
);

-- Portfolios
CREATE TABLE IF NOT EXISTS portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    portfolio_name VARCHAR(255) NOT NULL,
    config_data JSONB,
    created_at TIMESTAMP DEFAULT current_timestamp,
    updated_at TIMESTAMP DEFAULT current_timestamp
);

-- Backtest Results
CREATE TABLE IF NOT EXISTS backtest_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    test_name VARCHAR(255) NOT NULL,
    strategy_type VARCHAR(100),
    symbol VARCHAR(50),
    result_data JSONB,
    performance_metrics JSONB,
    created_at TIMESTAMP DEFAULT current_timestamp
);

-- Backtest Trades
CREATE TABLE IF NOT EXISTS backtest_trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    backtest_id UUID NOT NULL REFERENCES backtest_results(id) ON DELETE CASCADE,
    symbol VARCHAR(50),
    strategy_type VARCHAR(100),
    side VARCHAR(10), -- 'long' or 'short'
    entry_time TIMESTAMP,
    exit_time TIMESTAMP,
    entry_price DECIMAL(18, 6),
    exit_price DECIMAL(18, 6),
    shares INTEGER,
    pnl DECIMAL(18, 6),
    return_pct DECIMAL(12, 6),
    commission DECIMAL(18, 6),
    slippage DECIMAL(18, 6),
    created_at TIMESTAMP DEFAULT current_timestamp
);

-- User Settings
CREATE TABLE IF NOT EXISTS user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    settings JSONB, -- Contains theme, notifications, preferences, etc
    created_at TIMESTAMP DEFAULT current_timestamp,
    updated_at TIMESTAMP DEFAULT current_timestamp
);

-- Watchlists
CREATE TABLE IF NOT EXISTS watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(50) NOT NULL,
    added_at TIMESTAMP DEFAULT current_timestamp
);

-- Create Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_timestamp ON activity_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_backtest_results_user_id ON backtest_results(user_id);
CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlists_user_id ON watchlists(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlists_symbol ON watchlists(symbol);
CREATE INDEX IF NOT EXISTS idx_trading_activity_user_id ON trading_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_trading_activity_timestamp ON trading_activity(timestamp);
CREATE INDEX IF NOT EXISTS idx_trading_activity_type ON trading_activity(activity_type);
CREATE INDEX IF NOT EXISTS idx_trading_activity_symbol ON trading_activity(symbol);
CREATE INDEX IF NOT EXISTS idx_backtest_trades_user_id ON backtest_trades(user_id);
CREATE INDEX IF NOT EXISTS idx_backtest_trades_backtest_id ON backtest_trades(backtest_id);
CREATE INDEX IF NOT EXISTS idx_backtest_trades_entry_time ON backtest_trades(entry_time);

-- Row Level Security (RLS) Policies
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE kite_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE trading_activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE backtest_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE backtest_trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlists ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only read their own data
DROP POLICY IF EXISTS "Users can read own data" ON users CASCADE;
CREATE POLICY "Users can read own data" ON users
    FOR SELECT USING (auth.uid() = id);

-- Policy: Users can update their own data
DROP POLICY IF EXISTS "Users can update own data" ON users CASCADE;
CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Policy: Users can delete their own account
DROP POLICY IF EXISTS "Users can delete own account" ON users CASCADE;
CREATE POLICY "Users can delete own account" ON users
    FOR DELETE USING (auth.uid() = id);

-- Policy: Users can read their own profile
DROP POLICY IF EXISTS "Users can read own profile" ON user_profiles CASCADE;
CREATE POLICY "Users can read own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can insert their own profile
DROP POLICY IF EXISTS "Users can insert own profile" ON user_profiles CASCADE;
CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Users can modify their own profile
DROP POLICY IF EXISTS "Users can modify own profile" ON user_profiles CASCADE;
CREATE POLICY "Users can modify own profile" ON user_profiles
    FOR UPDATE WITH CHECK (auth.uid() = user_id);

-- Policy: Users can delete their own profile
DROP POLICY IF EXISTS "Users can delete own profile" ON user_profiles CASCADE;
CREATE POLICY "Users can delete own profile" ON user_profiles
    FOR DELETE USING (auth.uid() = user_id);

-- Policy: Users can read their own Kite credentials
DROP POLICY IF EXISTS "Users can read own kite credentials" ON kite_credentials CASCADE;
CREATE POLICY "Users can read own kite credentials" ON kite_credentials
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can insert their own Kite credentials
DROP POLICY IF EXISTS "Users can insert own kite credentials" ON kite_credentials CASCADE;
CREATE POLICY "Users can insert own kite credentials" ON kite_credentials
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own Kite credentials
DROP POLICY IF EXISTS "Users can update own kite credentials" ON kite_credentials CASCADE;
CREATE POLICY "Users can update own kite credentials" ON kite_credentials
    FOR UPDATE WITH CHECK (auth.uid() = user_id);

-- Policy: Users can delete their own Kite credentials (revoke access)
DROP POLICY IF EXISTS "Users can delete own kite credentials" ON kite_credentials CASCADE;
CREATE POLICY "Users can delete own kite credentials" ON kite_credentials
    FOR DELETE USING (auth.uid() = user_id);

-- Policy: Users can read their own activity logs
DROP POLICY IF EXISTS "Users can read own activity logs" ON activity_logs CASCADE;
CREATE POLICY "Users can read own activity logs" ON activity_logs
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can insert their own activity logs
DROP POLICY IF EXISTS "Users can insert own activity logs" ON activity_logs CASCADE;
CREATE POLICY "Users can insert own activity logs" ON activity_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Users can read their own trading activity
DROP POLICY IF EXISTS "Users can read own trading activity" ON trading_activity CASCADE;
CREATE POLICY "Users can read own trading activity" ON trading_activity
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can insert their own trading activity
DROP POLICY IF EXISTS "Users can insert own trading activity" ON trading_activity CASCADE;
CREATE POLICY "Users can insert own trading activity" ON trading_activity
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Users can delete their own trading activity
DROP POLICY IF EXISTS "Users can delete own trading activity" ON trading_activity CASCADE;
CREATE POLICY "Users can delete own trading activity" ON trading_activity
    FOR DELETE USING (auth.uid() = user_id);

-- Policy: Users can read their own portfolios
DROP POLICY IF EXISTS "Users can read own portfolios" ON portfolios CASCADE;
CREATE POLICY "Users can read own portfolios" ON portfolios
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can insert their own portfolios
DROP POLICY IF EXISTS "Users can insert own portfolios" ON portfolios CASCADE;
CREATE POLICY "Users can insert own portfolios" ON portfolios
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own portfolios
DROP POLICY IF EXISTS "Users can update own portfolios" ON portfolios CASCADE;
CREATE POLICY "Users can update own portfolios" ON portfolios
    FOR UPDATE WITH CHECK (auth.uid() = user_id);

-- Policy: Users can delete their own portfolios
DROP POLICY IF EXISTS "Users can delete own portfolios" ON portfolios CASCADE;
CREATE POLICY "Users can delete own portfolios" ON portfolios
    FOR DELETE USING (auth.uid() = user_id);

-- Policy: Users can read their own backtest results
DROP POLICY IF EXISTS "Users can read own backtest results" ON backtest_results CASCADE;
CREATE POLICY "Users can read own backtest results" ON backtest_results
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can insert their own backtest results
DROP POLICY IF EXISTS "Users can insert own backtest results" ON backtest_results CASCADE;
CREATE POLICY "Users can insert own backtest results" ON backtest_results
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Users can delete their own backtest results
DROP POLICY IF EXISTS "Users can delete own backtest results" ON backtest_results CASCADE;
CREATE POLICY "Users can delete own backtest results" ON backtest_results
    FOR DELETE USING (auth.uid() = user_id);

-- Policy: Users can read their own backtest trades
DROP POLICY IF EXISTS "Users can read own backtest trades" ON backtest_trades CASCADE;
CREATE POLICY "Users can read own backtest trades" ON backtest_trades
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can insert their own backtest trades
DROP POLICY IF EXISTS "Users can insert own backtest trades" ON backtest_trades CASCADE;
CREATE POLICY "Users can insert own backtest trades" ON backtest_trades
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Users can delete their own backtest trades
DROP POLICY IF EXISTS "Users can delete own backtest trades" ON backtest_trades CASCADE;
CREATE POLICY "Users can delete own backtest trades" ON backtest_trades
    FOR DELETE USING (auth.uid() = user_id);

-- Policy: Users can read their own settings
DROP POLICY IF EXISTS "Users can read own settings" ON user_settings CASCADE;
CREATE POLICY "Users can read own settings" ON user_settings
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can manage their own settings
DROP POLICY IF EXISTS "Users can manage own settings" ON user_settings CASCADE;
CREATE POLICY "Users can manage own settings" ON user_settings
    FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own settings" ON user_settings CASCADE;
CREATE POLICY "Users can update own settings" ON user_settings
    FOR UPDATE WITH CHECK (auth.uid() = user_id);

-- Policy: Users can read their own watchlist
DROP POLICY IF EXISTS "Users can read own watchlist" ON watchlists CASCADE;
CREATE POLICY "Users can read own watchlist" ON watchlists
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can manage their own watchlist
DROP POLICY IF EXISTS "Users can manage own watchlist" ON watchlists CASCADE;
CREATE POLICY "Users can manage own watchlist" ON watchlists
    FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own watchlist items" ON watchlists CASCADE;
CREATE POLICY "Users can delete own watchlist items" ON watchlists
    FOR DELETE USING (auth.uid() = user_id);

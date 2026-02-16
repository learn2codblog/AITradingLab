# Supabase Setup Guide - AI Trading Lab

## 🎯 Overview

This guide walks you through setting up Supabase for persistent data storage in AI Trading Lab. Supabase provides:

- ✅ **User Persistence**: User data survives app deployments
- ✅ **Kite Credentials Storage**: Securely store trading API keys
- ✅ **Activity Logging**: Complete audit trail of user actions
- ✅ **Data Backup**: Automatic backups of all user data
- ✅ **Row Level Security**: User can only access their own data
- ✅ **Real-time Sync**: Updates across devices instantly

## 📋 Prerequisites

- Supabase account (free tier available at https://supabase.com)
- Basic understanding of SQL
- `requirements.txt` updated with Supabase packages

## 🚀 Step-by-Step Setup

### 1. Create Supabase Project

1. Go to [https://app.supabase.com](https://app.supabase.com)
2. Click **Create a new project**
3. Enter project name: `ai-trading-lab`
4. Set a strong database password
5. Choose your region (closest to your users)
6. Wait for project to be created (5-10 minutes)

### 2. Get Your Credentials

After project creation:

1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** → `SUPABASE_ANON_KEY`
   - **service_role secret** → `SUPABASE_SERVICE_ROLE_KEY`

### 3. Set Environment Variables

Create `.env` file in project root:

```bash
# Copy from .env.example
cp .env.example .env
```

Edit `.env` and add your Supabase credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

### 4. Create Database Tables

The database schema is automatically created using SQL. You have two options:

#### Option A: Using SQL Editor (Recommended)

1. In Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy entire contents of `docs/SUPABASE_SCHEMA.sql`
4. Paste into the editor
5. Click **Run**
6. ✅ All tables and policies created!

#### Option B: Using Python Setup Script

```bash
pip install -r requirements.txt
python scripts/setup_supabase.py
```

### 5. Verify Setup

Run the verification script:

```bash
python scripts/setup_supabase.py
```

You should see:
```
✅ Connected to Supabase
✅ users
✅ user_profiles
✅ kite_credentials
✅ activity_logs
✅ portfolios
✅ backtest_results
✅ user_settings
✅ watchlists
```

### 6. Install Dependencies

```bash
pip install -r requirements.txt
```

## 💾 Database Schema

### Users Table
Stores user account information:
- `id` - UUID (primary key)
- `email` - User email (unique)
- `name` - Full name
- `password_hash` - SHA-256 hashed password
- `login_method` - 'email', 'google', 'microsoft', 'yahoo'
- `picture_url` - Profile picture URL
- `created_at` - Registration timestamp
- `is_active` - Account status

### User Profiles Table
Extended profile information:
- `user_id` - FK to users
- `bio` - Short biography
- `risk_tolerance` - conservative/moderate/aggressive
- `investment_horizon` - short/medium/long
- `trading_style` - day_trading/swing/position
- `initial_capital` - Starting funds
- `notifications_enabled` - Alert preference
- `dark_mode` - Theme preference

### Kite Credentials Table
Encrypted Zerodha API keys:
- `user_id` - FK to users
- `api_key` - Zerodha API key
- `api_secret` - Zerodha API secret
- `access_token` - OAuth token
- `is_connected` - Connection status
- `connected_at` - Timestamp

### Activity Logs Table
Complete audit trail:
- `user_id` - FK to users
- `activity_type` - login/trade/backtest/settings change
- `description` - Human-readable description
- `action_details` - JSON with additional data
- `status` - success/pending/failed
- `timestamp` - When it happened
- `ip_address` - User's IP

### Additional Tables
- **portfolios** - Saved portfolio configurations
- **backtest_results** - Performance results from strategy tests
- **user_settings** - Preferences and configuration
- **watchlists** - Stocks user is monitoring

## 🔐 Security Features

### Row Level Security (RLS)
All tables have RLS policies enabled:
- Users can only read their own data
- Users cannot access other user's information
- Activity logs are write-only (audit trail)

### Data Encryption
- Kite credentials stored in database (consider additional encryption)
- All API keys should be treated as sensitive
- Use `.env` for local development (never commit to git)

### .gitignore Configuration
Ensure these are ignored:
```
.env
.env.local
secrets.toml
__pycache__/
*.pyc
```

## 🔧 Code Integration

### Using Supabase Client

```python
from src.supabase_client import get_supabase_client

# Get the global client
supabase = get_supabase_client()

# Check connection
if supabase.is_connected():
    # Use the client
    user = supabase.get_user_by_email("user@example.com")
```

### Authentication with Supabase

```python
from src.auth_supabase import SupabaseAuthManager

auth = SupabaseAuthManager()

# Register new user
success, msg = auth.register_email_user(
    email="user@example.com",
    password="secure_password",
    name="User Name"
)

# Login
success, msg = auth.login_email_user(
    email="user@example.com",
    password="secure_password"
)
```

### Storing Kite Credentials

```python
# Store credentials after OAuth
supabase.store_kite_credentials(
    user_id=user_id,
    api_key="your-api-key",
    api_secret="your-api-secret",
    access_token="your-token"
)

# Retrieve credentials
kite_creds = supabase.get_kite_credentials(user_id)
if kite_creds and kite_creds['is_connected']:
    api_key = kite_creds['api_key']
```

### Activity Logging

```python
# Log user action
supabase.log_activity(
    user_id=user_id,
    activity_type='backtest_created',
    description='User ran backtest on INFY',
    action_details={'symbol': 'INFY', 'strategy': 'RSI'},
    status='success'
)

# Get activity history
activities = supabase.get_user_activities(user_id, limit=50)
for activity in activities:
    print(f"{activity['timestamp']} - {activity['description']}")
```

## 📊 Data Persistence Features

### User Dashboard
- Profile settings automatically saved to Supabase
- Preferences synced across devices
- Activity log available anytime

### Kite Integration
- API credentials encrypted and stored
- Connection status tracked
- Automatic disconnection logging

### Backtesting
- All backtest results saved to database
- Performance metrics archived
- Historical strategy comparison possible

### Portfolio Management
- Save multiple portfolio configurations
- Load saved portfolios anytime
- Track performance over time

## 🔄 Data Migration from JSON Files

If you had previous local data in JSON files:

```python
from src.supabase_client import get_supabase_client
import json

supabase = get_supabase_client()

# Migrate users from users.json
with open('users.json', 'r') as f:
    old_users = json.load(f)

for email, user_data in old_users.items():
    supabase.create_user(
        email=email,
        name=user_data['name'],
        password_hash=user_data['password_hash'],
        login_method='email'
    )
```

## 🆘 Troubleshooting

### Connection Failed
```
Error: Failed to connect to Supabase
```
- ✅ Check `.env` file has correct credentials
- ✅ Verify SUPABASE_URL is without trailing slash
- ✅ Confirm SUPABASE_ANON_KEY is not empty
- ✅ Check internet connection

### "Users table not found"
```
Error: relation "users" does not exist
```
- ✅ Run SQL schema from `docs/SUPABASE_SCHEMA.sql`
- ✅ Verify tables were created in Supabase dashboard
- ✅ Check project is correct in credentials

### Row Level Security Denied
```
Error: new row violates row level security policy
```
- ✅ Ensure RLS policies are created (part of schema)
- ✅ Verify user_id in data matches authenticated user
- ✅ Check auth context is set correctly

### Credentials Not Loading
```
Supabase credentials not configured
```
- ✅ Create `.env` file if it doesn't exist
- ✅ Add SUPABASE_URL and SUPABASE_ANON_KEY
- ✅ Restart Streamlit app: `Ctrl+C` and rerun

## 📈 Best Practices

1. **Regular Backups**
   - Supabase automatically backs up data
   - Enable daily backups in project settings

2. **Monitor Usage**
   - Check Supabase dashboard for storage limits
   - Upgrade plan if approaching limits

3. **Test RLS Policies**
   - Ensure user isolation is working
   - Regularly audit access patterns

4. **Secure Credentials**
   - Never commit `.env` to git
   - Rotate API keys periodically
   - Use strong passwords

5. **Monitor Performance**
   - Add database indexes for frequently queried fields
   - Archive old activity logs periodically
   - Monitor response times in Supabase dashboard

## 📱 Streamlit Cloud Deployment

For Streamlit Cloud deployment, add secrets in dashboard:

1. Go to app settings
2. Add **Secrets** section
3. Add SUPABASE_URL and SUPABASE_ANON_KEY
4. Save and re-deploy

```toml
# .streamlit/secrets.toml (local only, don't commit)
SUPABASE_URL = "https://..."
SUPABASE_ANON_KEY = "..."
```

## 🎓 Next Steps

1. ✅ Complete setup above
2. ⬜ Run `python scripts/setup_supabase.py`
3. ⬜ Test login with demo account (created by script)
4. ⬜ Connect Zerodha account (optional)
5. ⬜ Deploy to production with safety checks

## 📞 Support

- Supabase Docs: https://supabase.com/docs
- Supabase Discord: https://discord.supabase.com
- GitHub Issues: Report problems in project repo

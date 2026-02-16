# 🔧 CRITICAL FIX: Service Role Key Required

## ⚠️ Error You're Seeing:
```
Error saving portfolio: {'message': 'new row violates row-level security policy for table "portfolios"', 'code': '42501'}
```

## 🎯 Root Cause:
**Missing `SUPABASE_SERVICE_ROLE_KEY` environment variable**

This key is required for:
- ✅ User registration
- ✅ Portfolio saves
- ✅ Backtest saves
- ✅ Watchlist management
- ✅ Settings persistence
- ✅ Password changes

Without it, all data persistence operations will **fail with RLS policy errors**.

---

## 🚀 Quick Fix (3 Steps)

### Step 1: Get Your Service Role Key

1. Go to **Supabase Dashboard**: https://app.supabase.com/
2. Select your project
3. Click **Settings** (gear icon) → **API**
4. Find **Project API keys** section
5. Copy the **`service_role`** key (not the `anon` key!)
   - ⚠️ **It starts with**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - ⚠️ **Much longer than anon key** (~500+ characters)

### Step 2: Add to Your .env File

Open your `.env` file (or create it from `.env.example`) and add:

```bash
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-actual-key-here...
```

**Complete .env Example:**
```bash
# ==================== SUPABASE CONFIGURATION ====================
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here  # ← ADD THIS LINE
```

### Step 3: Restart Your App

```bash
streamlit run app_modern.py
```

Or if on **Hugging Face Spaces**:
1. Go to **Settings** → **Variables and secrets**
2. Add new secret:
   - Name: `SUPABASE_SERVICE_ROLE_KEY`
   - Value: (paste your service role key)
3. Click **Save**
4. Space will automatically restart

---

## ✅ Verification

Run SETUP.py to verify:

```bash
python SETUP.py
```

You should see:
```
✅ SUPABASE_URL: https://...
✅ SUPABASE_ANON_KEY: eyJhbG...
✅ SUPABASE_SERVICE_ROLE_KEY: eyJhbG...  ← This should appear!
```

If you see:
```
⚠️ SUPABASE_SERVICE_ROLE_KEY not set (data persistence will fail)
```

Then the key is **not** configured correctly.

---

## 🔒 Security Note

**⚠️ IMPORTANT - Service Role Key Security:**

The `service_role` key **bypasses all Row-Level Security (RLS)** policies and has **full database access**. 

**Never expose this key:**
- ❌ Don't commit to Git (add `.env` to `.gitignore`)
- ❌ Don't share publicly
- ❌ Don't use in client-side JavaScript
- ✅ Only use in backend Python code
- ✅ Store in environment variables
- ✅ Use Hugging Face Secrets for deployment

**Why it's safe in your setup:**
- ✅ Used only in server-side Python (Streamlit backend)
- ✅ Not exposed to browser/client
- ✅ Protected by environment variables
- ✅ Only used for authenticated user operations with explicit user_id checks

---

## 🧪 Test After Setup

1. **Login** to your app
2. Go to **💼 Portfolio** page
3. Add some stocks
4. Enter a portfolio name
5. Click **💾 Save Portfolio**
6. Should see: **"✅ Portfolio saved"** (not RLS error)

7. Go to **💾 My Data** tab
8. Should see your saved portfolio listed

---

## 🔍 Still Getting Errors?

### Check Environment Variables Are Loaded:

Add this debug snippet temporarily to your code:

```python
import os
print("SUPABASE_URL:", os.getenv('SUPABASE_URL'))
print("SUPABASE_ANON_KEY:", os.getenv('SUPABASE_ANON_KEY')[:20] if os.getenv('SUPABASE_ANON_KEY') else 'NOT SET')
print("SUPABASE_SERVICE_ROLE_KEY:", os.getenv('SUPABASE_SERVICE_ROLE_KEY')[:20] if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else 'NOT SET')
```

**Expected Output:**
```
SUPABASE_URL: https://your-project.supabase.co
SUPABASE_ANON_KEY: eyJhbGciOiJIUzI1NiIs...
SUPABASE_SERVICE_ROLE_KEY: eyJhbGciOiJIUzI1NiIs...
```

If SERVICE_ROLE_KEY shows `NOT SET`, your .env file is not being loaded correctly.

### Common Issues:

1. **Wrong file name**: Must be exactly `.env` (not `env.txt` or `.env.txt`)
2. **Wrong location**: `.env` must be in project root (same folder as `app_modern.py`)
3. **Not restarted**: After changing `.env`, you MUST restart Streamlit
4. **Whitespace**: No spaces around `=` in `.env` file
   - ✅ Correct: `SUPABASE_SERVICE_ROLE_KEY=value`
   - ❌ Wrong: `SUPABASE_SERVICE_ROLE_KEY = value`

---

## 📚 Technical Background

### Why Service Role Key?

**Row-Level Security (RLS) Problem:**
- Supabase RLS policies check: `auth.uid() = user_id`
- When user not authenticated yet (registration), `auth.uid()` is NULL
- INSERT blocked by policy: `FOR INSERT WITH CHECK (auth.uid() = user_id)`

**Service Role Key Solution:**
- Bypasses ALL RLS policies
- Allows system operations (registration, admin tasks)
- Used with explicit `user_id` parameter for security

**Implementation Pattern:**
```python
# Registration - uses service key
client = self.service_client  # Bypasses RLS
client.table('users').insert({'user_id': uuid, ...})

# Normal operations - uses anon key  
client = self.client  # Enforces RLS
client.table('users').select('*').eq('id', user_id)  # Only returns user's own data
```

---

## ✅ Summary Checklist

- [ ] Got service_role key from Supabase Dashboard
- [ ] Added SUPABASE_SERVICE_ROLE_KEY to .env file
- [ ] Verified key is ~500+ characters (not the shorter anon key)
- [ ] Restarted Streamlit app
- [ ] Ran python SETUP.py to verify
- [ ] Tested portfolio save - no RLS error
- [ ] Data appears in "💾 My Data" tab

**Once complete, all data persistence will work perfectly! 🎉**

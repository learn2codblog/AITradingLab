# Authentication Quick Reference

## 🚀 Get Started in 30 Seconds

### Demo Login (Immediate)
```
1. Run: streamlit run app_modern.py
2. Click: "✅ Demo Login" button
3. Enter email: trader@example.com
4. Enter name: Demo Trader
5. Click: "✅ Demo Login"
✅ You're in! Explore the app.
```

### Logout
```
1. Click: "🚪 Logout" button (top navigation)
2. Confirm logout
✅ You've been logged out
```

---

## 💻 For Developers

### Check if User is Logged In
```python
from src.auth import AuthManager

auth_manager = AuthManager()
auth_manager.initialize_session_state()

if auth_manager.is_authenticated():
    print("User is logged in!")
else:
    print("User needs to login")
```

### Get User Information
```python
from src.auth import AuthManager

auth_manager = AuthManager()
user_info = auth_manager.get_user_info()

print(f"Name: {user_info['name']}")
print(f"Email: {user_info['email']}")
print(f"LoginMethod: {user_info['login_method']}")
```

### Protect a Feature (Require Login)
```python
from src.auth import require_login

@require_login
def my_protected_feature():
    st.write("Only logged-in users see this!")
```

### Programmatic Logout
```python
from src.auth import AuthManager

auth_manager = AuthManager()
auth_manager.logout()
st.rerun()
```

---

## 🔐 Gmail OAuth2 Setup (5 Steps)

### Step 1: Google Cloud Console
```
Go to: https://console.cloud.google.com/
Create → New Project → "AITradingLab"
```

### Step 2: Enable API
```
APIs & Services → Library
Search: "Google+ API"
Click: ENABLE
```

### Step 3: Create Credentials
```
APIs & Services → Credentials
CREATE CREDENTIALS → OAuth 2.0 Client ID
Select: Web application
Add Redirect URI: http://localhost:8501
CREATE → Copy Client ID & Client Secret
```

### Step 4: Create .env File
```bash
# .env
GMAIL_CLIENT_ID=your-client-id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your-client-secret
GMAIL_REDIRECT_URI=http://localhost:8501
```

### Step 5: Restart App
```bash
streamlit run app_modern.py
```

---

## 📁 Files Structure

```
AITradingLab/
├── app_modern.py              # Modified: Added auth check
├── .env.example               # Template for OAuth credentials
├── src/
│   └── auth.py               # Authentication module (NEW)
├── ui/
│   └── login_page.py         # Login UI component (NEW)
├── utils/
│   ├── __init__.py           # Utils package init (NEW)
│   └── oauth_config.py       # OAuth configuration (NEW)
└── docs/getting-started/
    ├── AUTHENTICATION_SETUP.md        # Full guide
    └── AUTHENTICATION_IMPLEMENTATION.md # What was added
```

---

## 🔑 Session State Variables

When logged in, these are available:

```python
st.session_state.authenticated  # bool - True if logged in
st.session_state.user_email     # str - User's email
st.session_state.user_name      # str - User's full name
st.session_state.user_picture   # str - Profile picture URL (Gmail only)
st.session_state.session_start  # datetime - When logged in
st.session_state.login_method   # str - "gmail" or "demo"
```

---

## ⚡ Environment Variables

| Variable | Example | Required | Notes |
|----------|---------|----------|-------|
| `GMAIL_CLIENT_ID` | `xyz.apps.googleusercontent.com` | Dev only | From Google Cloud Console |
| `GMAIL_CLIENT_SECRET` | `abc123xyz` | Dev only | Keep secret! |
| `GMAIL_REDIRECT_URI` | `http://localhost:8501` | Dev only | Must match Google settings |

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Please login" repeatedly | Check auth code is at top of app_modern.py |
| Demo login not working | Fill both email and name fields |
| Gmail button not working | Check .env file exists with correct values |
| Session keeps expiring | Sessions timeout after 24 hours (security feature) |
| Can't see user info | Refresh browser (F5) and login again |

---

## 🔒 Security Checklist

- [ ] `.env` file is created (not committed)
- [ ] `.env` is in `.gitignore`
- [ ] Using environment variables, not hardcoded credentials
- [ ] `GMAIL_CLIENT_SECRET` is kept secret
- [ ] Never share `.env` file
- [ ] Use HTTPS for production OAuth

---

## 📚 Full Documentation

For complete details, see:
- [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) - Full guide with setups
- [AUTHENTICATION_IMPLEMENTATION.md](AUTHENTICATION_IMPLEMENTATION.md) - What was added

---

## ❓ Common Questions

**Q: Is my password stored?**
A: No passwords are stored. Login uses OAuth2 (Google) or demo mode.

**Q: Can I use other login methods?**
A: Yes! Architecture supports GitHub, Facebook, etc. (See developer guide)

**Q: How long are sessions valid?**
A: 24 hours. Auto-logout on next page load if expired.

**Q: Can I store user data persistently?**
A: Current system uses memory. Add database to `src/auth.py` for persistence.

**Q: Is this secure?**
A: Yes! Uses OAuth2 and secure session management. See security guide.

---

## 🚀 Next Features (Optional)

- [ ] Database user storage
- [ ] Two-factor authentication (2FA)
- [ ] Social login (GitHub, Facebook)
- [ ] User profiles/settings
- [ ] Role-based access control
- [ ] Login activity logs

---

**Last Updated:** 2024
**Status:** ✅ Production Ready

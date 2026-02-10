# Authentication & Login Guide

## Overview

AITradingLab now includes a secure authentication system with support for:
- **Demo Login** - For testing and development
- **Gmail OAuth2** - For production deployment

This guide will help you set up and use the authentication features.

---

## 🚀 Quick Start with Demo Login

The fastest way to get started is using the built-in demo login:

### Using Demo Login

1. **Start the application**
   ```bash
   streamlit run app_modern.py
   ```

2. **Login with demo credentials**
   - Click the "✅ Demo Login" button
   - Enter any email (e.g., `trader@example.com`)
   - Enter a name (e.g., `Demo Trader`)
   - Click "✅ Demo Login"

3. **Access the full application**
   - You're now logged in!
   - Explore all features freely
   - Use "🚪 Logout" button to log out

### Logout

- Click the **"🚪 Logout"** button in the navigation bar
- You'll be returned to the login page
- Click "✅ Demo Login" to log back in

---

## 🔐 Setting up Gmail OAuth2

For production deployment, use Gmail OAuth2 for secure authentication.

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a Project" → "NEW PROJECT"
3. Enter project name: `AITradingLab`
4. Click "CREATE"
5. Wait for project to be created

### Step 2: Enable OAuth 2.0 API

1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Google+ API"
3. Click on the result
4. Click "ENABLE"
5. Wait for the API to be enabled

### Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "CREATE CREDENTIALS" → "OAuth 2.0 Client ID"
3. You may be prompted to configure the OAuth consent screen:
   - Click "CONFIGURE CONSENT SCREEN"
   - Select "External" for user type
   - Click "CREATE"
   - Fill in the required fields:
     - App name: `AITradingLab`
     - User support email: your email
     - Developer contact: your email
   - Click "SAVE AND CONTINUE"
   - On "Scopes" page, click "SAVE AND CONTINUE"
   - Review and click "BACK TO DASHBOARD"

4. Now create the OAuth credentials:
   - Go back to "APIs & Services" → "Credentials"
   - Click "CREATE CREDENTIALS" → "OAuth 2.0 Client ID"
   - Select "Web application"
   - Give it a name: `AITradingLab Web Client`
   - Under "Authorized redirect URIs", add:
     - `http://localhost:8501` (for local development)
     - `https://yourdomainname.com` (for production)
   - Click "CREATE"

5. **Copy your credentials**:
   - On the credentials page, find your OAuth client
   - Click the download icon or copy the Client ID and Client Secret
   - Keep these safe!

### Step 4: Set Environment Variables

Create a `.env` file in the project root directory:

```bash
# .env
GMAIL_CLIENT_ID=your-client-id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your-client-secret
GMAIL_REDIRECT_URI=http://localhost:8501
```

**⚠️ Important Security Notes:**
- Never commit `.env` to version control
- Add `.env` to `.gitignore`:
  ```
  # .gitignore
  .env
  .env.local
  .env.prod
  ```
- Use strong, randomly generated secrets
- Rotate secrets regularly

### Step 5: Install Required Packages

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-auth
```

Or use the existing requirements:
```bash
pip install -r requirements.txt
```

### Step 6: Restart the Application

```bash
streamlit run app_modern.py
```

Now the "🔗 Sign in with Gmail" button will be fully functional.

---

## 📋 User Session Management

### Session Features

- **Session Duration**: 24 hours
- **Session Persistence**: Across page reloads
- **Auto-logout**: After 24 hours of inactivity
- **Session Info**: Display current user and login method

### Session Display

In the header, you'll see:
- 👤 User's name
- 📧 User's email
- ⏱️ Session duration
- Login method (Gmail or Demo)

### Session Files

Session data is stored in `st.session_state`:
- `authenticated`: Login status
- `user_email`: User's email address
- `user_name`: User's full name
- `user_picture`: User's profile picture (Gmail only)
- `session_start`: Session start time
- `login_method`: Method used to login (gmail/demo)

---

## 🔧 Developer Guide

### Authentication Architecture

```
User Visit
    ↓
Check session_state.authenticated
    ↓
IF authenticated: Continue to app
IF not authenticated: Redirect to login page
    ↓
User clicks Gmail or Demo Login
    ↓
OAuth2 flow (Gmail) or direct session (Demo)
    ↓
Store user info in session_state
    ↓
User can now access full app
```

### Key Classes

#### AuthManager
Located in `src/auth.py`

```python
from src.auth import AuthManager

# Initialize
auth_manager = AuthManager()
auth_manager.initialize_session_state()

# Check authentication
if auth_manager.is_authenticated():
    # User is logged in
    pass

# Check session validity
if auth_manager.is_session_valid():
    # Session is still active
    pass

# Get user info
user_info = auth_manager.get_user_info()
print(user_info['email'])
print(user_info['name'])

# Logout
auth_manager.logout()

# Create demo session
auth_manager.create_demo_user("user@example.com", "John Doe")

# Set user session
auth_manager.set_user_session(
    email="user@gmail.com",
    name="John Doe",
    picture="https://...",
    method="gmail"
)
```

#### OAuthConfig
Located in `utils/oauth_config.py`

```python
from utils.oauth_config import OAuthConfig, OAuthHelper

# Create config
config = OAuthConfig()

# Check if configured
if config.is_configured:
    print("Gmail OAuth2 is properly configured")

# Get authorization URL
auth_url = config.get_auth_url()

# Validate setup
if OAuthHelper.validate_oauth_setup():
    print("OAuth setup is complete")

# Get setup instructions
instructions = OAuthHelper.get_setup_instructions()
```

### Using Authentication in Your Code

#### Require Login for a Function

```python
from src.auth import require_login

@require_login
def protected_feature():
    """This function requires login"""
    user_info = st.session_state
    st.write(f"Hello, {user_info.user_name}!")
```

#### Check Authentication Status

```python
from src.auth import AuthManager

auth_manager = AuthManager()
auth_manager.initialize_session_state()

if not auth_manager.is_authenticated():
    st.warning("Please login first")
    st.stop()

# Continue with authenticated code
st.success("You are logged in!")
```

#### Display User Information

```python
from src.auth import AuthManager

auth_manager = AuthManager()
if auth_manager.is_authenticated():
    user_info = auth_manager.get_user_info()
    st.write(f"**User:** {user_info['name']}")
    st.write(f"**Email:** {user_info['email']}")
    st.write(f"**Session Duration:** {auth_manager.get_session_duration()}")
```

---

## 🐛 Troubleshooting

### Issue: "Please login first" appears repeatedly

**Solution:**
- Check that `st.session_state` is properly initialized
- Verify the authentication code is at the top of `app_modern.py`
- Clear browser cache and cookies
- Restart Streamlit: `Ctrl+C` and run `streamlit run app_modern.py` again

### Issue: Gmail login not working

**Common causes:**
- Missing or invalid `GMAIL_CLIENT_ID` environment variable
- `GMAIL_REDIRECT_URI` doesn't match Google Cloud Console settings
- OAuth consent screen not configured
- Missing API permissions

**Fix:**
1. Verify `.env` file contains correct values
2. Check Google Cloud Console settings match your `.env`
3. Ensure "Google+ API" is enabled in Google Cloud Console
4. Reconfigure the OAuth consent screen
5. Test with Demo Login first to ensure app is working

### Issue: "Session expired" message

**Solution:**
- Sessions expire after 24 hours of inactivity
- The system will automatically prompt you to login again
- This is intentional for security

### Issue: Demo Login not working

**Solution:**
- Ensure both email and name fields are filled
- Email should be a valid email format (e.g., `user@example.com`)
- Check browser console for error messages: `F12` → "Console" tab
- Try a different email address

### Issue: Cannot see user info in header

**Solution:**
- Refresh the page: `F5`
- Check if `AuthManager` is properly initialized at the top of `app_modern.py`
- Verify user is actually logged in by checking navigation bar

---

## 🔐 Security Best Practices

### For Development

- Use Demo Login for testing
- Never commit `.env` files
- Use unique credentials for each environment

### For Production

1. **Use HTTPS**
   - OAuth2 requires secure connections in production
   - Update `GMAIL_REDIRECT_URI` to use `https://`

2. **Secure Credential Storage**
   - Use environment variables (not hardcoded)
   - Consider using AWS Secrets Manager or Azure Key Vault
   - Rotate secrets regularly

3. **Token Management**
   - Don't store tokens in browser cookies
   - Use secure server-side session storage
   - Implement token refresh mechanism

4. **User Data Protection**
   - Minimize data collection (only email and name)
   - Implement data deletion on logout
   - Comply with GDPR/privacy regulations

5. **Rate Limiting**
   - Implement login attempt rate limiting
   - Add CAPTCHA for repeated failed attempts
   - Log authentication events

---

## 📚 Additional Resources

- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Streamlit Session State](https://docs.streamlit.io/library/api-reference/session-state)
- [Security Best Practices](https://owasp.org/www-project-top-ten/)

---

## ❓ FAQ

**Q: Can I use other OAuth providers?**
A: Yes! The architecture supports adding other providers (Facebook, GitHub, etc.). Modify `utils/oauth_config.py` to add new providers.

**Q: Where is user data stored?**
A: Currently, user data is stored in `st.session_state` (in memory). For persistent storage, add a database connection to `src/auth.py`.

**Q: How do I implement user registration?**
A: The current system uses OAuth sign-in (no registration needed). To add registration, implement user creation in `src/auth.py`.

**Q: Can I customize the login page?**
A: Yes! Modify `ui/login_page.py` to change colors, text, and layout.

**Q: How do I add a "Remember me" feature?**
A: Store session tokens in browser cookies or implement persistent login using database storage.

---

**Need more help?** 
- Check the [main README](../README.md)
- Review the [Getting Started guide](../getting-started/)
- Submit an issue on GitHub

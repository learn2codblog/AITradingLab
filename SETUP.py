#!/usr/bin/env python3
"""
Complete Supabase Setup & Initialization
One-command setup for data persistence
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def print_banner():
    """Print welcome banner"""
    print("""
    ╔═════════════════════════════════════════════════════════╗
    ║                                                         ║
    ║  🚀 AI Trading Lab - Supabase Data Persistence Setup   ║
    ║                                                         ║
    ║     Professional Data Persistence Implementation        ║
    ║                                                         ║
    ╚═════════════════════════════════════════════════════════╝
    """)

def check_env():
    """Check environment configuration from .env or platform variables"""
    print("1️⃣  Checking environment configuration...")
    
    # Try loading from .env first (for local development)
    env_path = Path(".env")
    if env_path.exists():
        print("   ✅ .env file found")
        load_dotenv()
    else:
        print("   ℹ️  .env file not found (checking platform variables...)")
    
    # Check if vars exist (from .env OR from platform like Hugging Face)
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if url and key:
        print(f"   ✅ Environment variables loaded")
        print(f"   ✅ SUPABASE_URL: {url[:30]}...")
        print(f"   ✅ SUPABASE_ANON_KEY: {key[:20]}...")
        
        if service_key:
            print(f"   ✅ SUPABASE_SERVICE_ROLE_KEY: {service_key[:20]}...")
        else:
            print(f"   ⚠️  SUPABASE_SERVICE_ROLE_KEY not set (data persistence will fail)")
            print(f"      Get from: Supabase Dashboard → Settings → API → service_role key")
            print(f"      Required for: Registration, portfolio saves, backtest saves")
        
        return True
    else:
        print("   ❌ Supabase credentials not found")
        print("   ℹ️  Add these environment variables:")
        print("      - SUPABASE_URL")
        print("      - SUPABASE_ANON_KEY")
        print("      - SUPABASE_SERVICE_ROLE_KEY (critical for data persistence)")
        print("   To:")
        print("      - .env file (local development), or")
        print("      - Platform environment variables (Hugging Face, etc.)")
        
        # Try to create .env.example for reference
        if not env_path.exists():
            import shutil
            example_path = Path(".env.example")
            if example_path.exists():
                shutil.copy(example_path, env_path)
                print(f"   📝 .env template created from .env.example")
        
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\n2️⃣  Checking dependencies...")
    
    required = [
        'supabase',
        'streamlit',
        'pandas',
        'plotly'
    ]
    
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n   To install missing packages:")
        print(f"   pip install -r requirements.txt")
        return False
    
    return True

def check_supabase_connection():
    """Test Supabase connection"""
    print("\n3️⃣  Testing Supabase connection...")
    
    try:
        from src.supabase_client import get_supabase_client
        
        client = get_supabase_client()
        
        if client.is_connected():
            print("   ✅ Connected to Supabase")
            return True
        else:
            print("   ❌ Failed to connect to Supabase")
            print("   Check your credentials in .env")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def check_database_tables():
    """Verify database tables exist"""
    print("\n4️⃣  Checking database tables...")
    
    try:
        from src.supabase_client import get_supabase_client
        
        client = get_supabase_client()
        
        if not client.is_connected():
            print("   ⚠️  Not connected to Supabase")
            return False
        
        tables = [
            'users',
            'user_profiles',
            'kite_credentials',
            'activity_logs',
            'portfolios',
            'backtest_results',
            'user_settings',
            'watchlists'
        ]
        
        all_exist = True
        for table in tables:
            try:
                result = client.client.table(table).select('1').limit(1).execute()
                print(f"   ✅ {table}")
            except:
                print(f"   ❌ {table} - NOT FOUND")
                all_exist = False
        
        if not all_exist:
            print("\n   📝 To create tables:")
            print("   1. Go to: https://app.supabase.com")
            print("   2. Select your project")
            print("   3. Go to SQL Editor")
            print("   4. Create new query")
            print("   5. Copy from: docs/SUPABASE_SCHEMA.sql")
            print("   6. Run the SQL script")
        
        return all_exist
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def create_demo_user():
    """Create demo user for testing"""
    print("\n5️⃣  Setting up demo account...")
    
    try:
        from src.auth_supabase import SupabaseAuthManager
        
        auth = SupabaseAuthManager()
        
        success, message = auth.register_email_user(
            email="demo@aitradinglab.com",
            password="demo123456",
            name="Demo Trader"
        )
        
        if success:
            print(f"   ✅ Demo user created")
            print(f"   📧 Email: demo@aitradinglab.com")
            print(f"   🔑 Password: demo123456")
        else:
            if "already registered" in message:
                print(f"   ℹ️  Demo user already exists")
            else:
                print(f"   ℹ️  {message}")
        
        return True
        
    except Exception as e:
        print(f"   ⚠️  Could not create demo user: {str(e)}")
        return False

def print_next_steps():
    """Print next steps for user"""
    print("\n" + "="*60)
    print("✨ SETUP COMPLETE!")
    print("="*60)
    
    print("""
    📚 Documentation:
    ├─ docs/SETUP_SUPABASE.md          Complete setup guide
    ├─ docs/DATA_PERSISTENCE_GUIDE.md  Feature overview
    ├─ docs/IMPLEMENTATION_COMPLETE.md Technical details
    └─ QUICK_REFERENCE.md              Quick reference

    🚀 To start the app:
    └─ streamlit run app_modern.py

    🔐 Test login with:
    ├─ Email: demo@aitradinglab.com
    └─ Password: demo123456

    ⚡ Next steps:
    1. Update .env with Supabase credentials
    2. Create tables in Supabase (SQL Editor)
    3. Run: streamlit run app_modern.py
    4. Test login with demo account
    5. Connect Zerodha (optional)
    6. Deploy to production!

    📞 Support:
    ├─ Supabase Docs: https://supabase.com/docs
    ├─ Setup Guide: docs/SETUP_SUPABASE.md
    └─ Issues: Check QUICK_REFERENCE.md
    """)

def main():
    """Main setup flow"""
    print_banner()
    
    # Step 1: Check environment
    env_ok = check_env()
    if not env_ok:
        print("\n⚠️  Setup paused - need .env configuration")
        print("\nTo complete setup:")
        print("1. Edit .env file")
        print("2. Add SUPABASE_URL and SUPABASE_ANON_KEY")
        print("3. Run this script again")
        return False
    
    # Step 2: Check dependencies
    deps_ok = check_dependencies()
    if not deps_ok:
        print("\n⚠️  Setup paused - missing dependencies")
        print("\nTo complete setup:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Run this script again")
        return False
    
    # Step 3: Test connection
    conn_ok = check_supabase_connection()
    if not conn_ok:
        print("\n❌ Cannot connect to Supabase")
        return False
    
    # Step 4: Check tables
    tables_ok = check_database_tables()
    
    if not tables_ok:
        print("\n⚠️  Database tables not found")
        print("\nTo create tables:")
        print("1. Go to https://app.supabase.com")
        print("2. Copy from docs/SUPABASE_SCHEMA.sql")
        print("3. Run in SQL Editor")
        return False
    
    # Step 5: Create demo user
    create_demo_user()
    
    # Print next steps
    print_next_steps()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

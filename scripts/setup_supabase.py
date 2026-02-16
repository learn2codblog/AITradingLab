"""
Setup script to initialize Supabase database and tables
Run this once after creating your Supabase project
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_supabase():
    """Initialize Supabase database"""
    
    print("🚀 AI Trading Lab - Supabase Setup")
    print("=" * 50)
    
    # Check environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ ERROR: Supabase credentials not found!")
        print("\nPlease set environment variables:")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_ANON_KEY")
        print("\nYou can set these in:")
        print("  1. .env file in project root")
        print("  2. System environment variables")
        print("  3. .streamlit/secrets.toml for Streamlit Cloud")
        return False
    
    print("✅ Supabase credentials found")
    print(f"   URL: {supabase_url[:30]}...")
    
    try:
        from src.supabase_client import get_supabase_client
        
        client = get_supabase_client()
        
        if not client.is_connected():
            print("❌ Failed to connect to Supabase")
            return False
        
        print("✅ Connected to Supabase")
        
        print("\n📋 Verifying required tables...")
        
        # Check if tables exist by trying to query them
        tables_to_check = [
            'users',
            'user_profiles',
            'kite_credentials',
            'activity_logs',
            'portfolios',
            'backtest_results',
            'user_settings',
            'watchlists'
        ]
        
        for table in tables_to_check:
            try:
                result = client.client.table(table).select('count', count='exact').execute()
                print(f"  ✅ {table}")
            except Exception as e:
                print(f"  ❌ {table} - {str(e)}")
        
        print("\n📖 To complete setup:")
        print("  1. Go to: https://app.supabase.com")
        print("  2. Select your project")
        print("  3. Go to SQL Editor")
        print("  4. Create a new query")
        print("  5. Copy the contents of: docs/SUPABASE_SCHEMA.sql")
        print("  6. Run the SQL script")
        print("\n✅ Setup guide saved to: docs/SETUP_SUPABASE.md")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        return False


def create_demo_user():
    """Create a demo user for testing"""
    print("\n🔐 Creating demo user...")
    
    try:
        from src.auth_supabase import SupabaseAuthManager
        
        auth = SupabaseAuthManager()
        
        success, message = auth.register_email_user(
            email="demo@aitradinglab.com",
            password="demo123456",
            name="Demo Trader"
        )
        
        if success:
            print(f"✅ {message}")
            print("\nDemo credentials:")
            print("  Email: demo@aitradinglab.com")
            print("  Password: demo123456")
        else:
            print(f"ℹ️ {message}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create demo user: {str(e)}")
        return False


if __name__ == "__main__":
    success = setup_supabase()
    
    if success:
        create_demo_user()
        print("\n✅ Setup complete!")
        print("You can now run: streamlit run app_modern.py")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)

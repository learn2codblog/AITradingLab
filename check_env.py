"""
Quick diagnostic tool to check Supabase environment variables

Run this to verify your .env configuration:
    python check_env.py
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def check_env_vars():
    """Check all Supabase environment variables"""
    
    print("\n" + "="*60)
    print("🔍 SUPABASE ENVIRONMENT VARIABLE DIAGNOSTIC")
    print("="*60 + "\n")
    
    # Required variables
    required_vars = {
        'SUPABASE_URL': 'Supabase project URL',
        'SUPABASE_ANON_KEY': 'Public anon/public key',
        'SUPABASE_SERVICE_ROLE_KEY': 'Service role key (CRITICAL for data saves)'
    }
    
    all_set = True
    
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        
        if value:
            # Show first 30 characters for verification
            preview = value[:30] + "..." if len(value) > 30 else value
            print(f"✅ {var_name}")
            print(f"   {description}")
            print(f"   Value: {preview}")
            print(f"   Length: {len(value)} characters\n")
        else:
            print(f"❌ {var_name} - NOT SET")
            print(f"   {description}")
            print(f"   Status: MISSING\n")
            all_set = False
    
    print("="*60)
    
    if all_set:
        print("✅ ALL ENVIRONMENT VARIABLES CONFIGURED!")
        print("\nYour app should work correctly.")
        print("If you still get errors, restart Streamlit:")
        print("  streamlit run app_modern.py\n")
        return True
    else:
        print("⚠️ MISSING REQUIRED ENVIRONMENT VARIABLES")
        print("\nFollow these steps:")
        print("1. Copy .env.example to .env:")
        print("   cp .env.example .env")
        print("\n2. Get keys from Supabase Dashboard:")
        print("   https://app.supabase.com/project/YOUR_PROJECT/settings/api")
        print("\n3. Add keys to .env file")
        print("\n4. Re-run this script to verify")
        print("\nSee FIX_SERVICE_ROLE_KEY.md for detailed instructions.\n")
        return False

def check_env_file():
    """Check if .env file exists"""
    
    print("\n" + "="*60)
    print("📄 CHECKING .ENV FILE")
    print("="*60 + "\n")
    
    if os.path.exists('.env'):
        print("✅ .env file found")
        
        # Check file size
        file_size = os.path.getsize('.env')
        print(f"   Size: {file_size} bytes")
        
        if file_size < 100:
            print("   ⚠️ Warning: File seems small. Make sure you added the keys.")
        else:
            print("   ✅ File size looks good")
        
        # Check if it has the service key
        with open('.env', 'r') as f:
            content = f.read()
            if 'SUPABASE_SERVICE_ROLE_KEY=' in content:
                # Check if it's just the template placeholder
                if 'your-service-role-key-here' in content or 'your_service_role_key_here' in content:
                    print("   ⚠️ Service key looks like template placeholder")
                    print("   Replace with actual key from Supabase Dashboard")
                else:
                    print("   ✅ SUPABASE_SERVICE_ROLE_KEY found in file")
            else:
                print("   ❌ SUPABASE_SERVICE_ROLE_KEY not found in file")
                print("   Add this line to .env:")
                print("   SUPABASE_SERVICE_ROLE_KEY=your-actual-key")
    else:
        print("❌ .env file NOT FOUND")
        print("   Create it from template:")
        print("   cp .env.example .env")
        print("   Then edit .env and add your Supabase keys")
    
    print()

def validate_key_format():
    """Validate that keys have correct format"""
    
    print("\n" + "="*60)
    print("🔍 VALIDATING KEY FORMATS")
    print("="*60 + "\n")
    
    anon_key = os.getenv('SUPABASE_ANON_KEY')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if anon_key:
        if anon_key.startswith('eyJ'):
            print("✅ ANON_KEY format looks correct (JWT token)")
        else:
            print("⚠️ ANON_KEY doesn't look like a JWT token")
            print("   Should start with: eyJ")
    
    if service_key:
        if service_key.startswith('eyJ'):
            print("✅ SERVICE_ROLE_KEY format looks correct (JWT token)")
            
            # Service key should be longer than anon key
            if anon_key and len(service_key) > len(anon_key):
                print(f"✅ SERVICE_ROLE_KEY is longer than ANON_KEY (good)")
                print(f"   Service: {len(service_key)} chars")
                print(f"   Anon: {len(anon_key)} chars")
            elif anon_key:
                print(f"⚠️ SERVICE_ROLE_KEY seems too short")
                print(f"   Service: {len(service_key)} chars")
                print(f"   Anon: {len(anon_key)} chars")
                print("   Make sure you copied the service_role key, not anon key")
        else:
            print("⚠️ SERVICE_ROLE_KEY doesn't look like a JWT token")
            print("   Should start with: eyJ")
    
    print()

if __name__ == "__main__":
    check_env_file()
    env_ok = check_env_vars()
    
    if env_ok:
        validate_key_format()
    
    print("="*60)
    print("\n📖 For detailed setup instructions, see:")
    print("   FIX_SERVICE_ROLE_KEY.md")
    print("\n" + "="*60 + "\n")

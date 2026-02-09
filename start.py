"""
Quick Start Script for AI Trading Lab PRO+ v2.0
Launches the modern UI application
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'streamlit',
        'pandas',
        'numpy',
        'plotly',
        'yfinance',
        'scikit-learn',
        'xgboost'
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print("❌ Missing dependencies:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\n💡 Install all dependencies with:")
        print("   pip install -r requirements.txt")
        return False

    print("✅ All dependencies installed!")
    return True

def main():
    """Main function to launch the app"""
    print("=" * 60)
    print("🚀 AI Trading Lab PRO+ v2.0")
    print("=" * 60)
    print()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Check if app_modern.py exists
    if not os.path.exists('app_modern.py'):
        print("❌ app_modern.py not found!")
        print("   Make sure you're in the AITradingLab directory")
        sys.exit(1)

    print()
    print("🎯 Launching application...")
    print("   URL: http://localhost:8501")
    print()
    print("💡 Tips:")
    print("   - Use Ctrl+C to stop the server")
    print("   - Clear cache from Settings page")
    print("   - Check documentation/ folder for guides")
    print()
    print("=" * 60)
    print()

    # Launch streamlit
    try:
        subprocess.run([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app_modern.py",
            "--server.port=8501",
            "--server.address=localhost"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for using AI Trading Lab PRO+!")
        sys.exit(0)

if __name__ == "__main__":
    main()


"""
Launch script for Content Analysis Platform Streamlit UI

This script provides an easy way to start the Streamlit application
with proper configuration and environment setup.
"""

import subprocess
import sys
from pathlib import Path
import os


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['streamlit', 'plotly', 'pandas']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r streamlit_requirements.txt")
        return False
    
    return True


def launch_streamlit():
    """Launch Streamlit application"""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    app_path = script_dir / 'src' / 'ui' / 'streamlit_app.py'
    
    if not app_path.exists():
        print(f"❌ Error: Streamlit app not found at {app_path}")
        return
    
    print("🚀 Launching Content Analysis Platform...")
    print(f"📁 App location: {app_path}")
    print("\n" + "="*60)
    print("🌐 The app will open in your browser automatically")
    print("⏹️  Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Launch Streamlit
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.port=8501",
        "--server.headless=false",
        "--browser.gatherUsageStats=false"
    ]
    
    try:
        subprocess.run(cmd, cwd=script_dir)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down Content Analysis Platform...")
    except Exception as e:
        print(f"\n❌ Error launching Streamlit: {e}")


def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     📊 Content Analysis Platform Launcher 📊             ║
║                                                          ║
║     Professional Web Content Analysis with AI           ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    print("✅ All dependencies installed\n")
    
    # Launch app
    launch_streamlit()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Setup script for AI Invoice Tool
"""

import os
import sys
import subprocess
import platform

def run_command(command):
    """Run shell command and return success status"""
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def install_system_dependencies():
    """Install system-level dependencies"""
    system = platform.system().lower()
    
    print("📦 Installing system dependencies...")
    
    if system == "darwin":  # macOS
        print("Detected macOS - installing Tesseract via Homebrew...")
        if not run_command("brew --version"):
            print("❌ Homebrew not found. Please install Homebrew first:")
            print("https://brew.sh/")
            return False
        
        if not run_command("brew install tesseract"):
            print("⚠️  Failed to install Tesseract. You may need to install it manually.")
    
    elif system == "linux":
        print("Detected Linux - installing Tesseract via apt...")
        if not run_command("sudo apt-get update && sudo apt-get install -y tesseract-ocr"):
            print("⚠️  Failed to install Tesseract. You may need to install it manually.")
    
    else:
        print(f"⚠️  System {system} not directly supported.")
        print("Please install Tesseract manually:")
        print("- Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("- Other: Check your package manager")

def install_python_dependencies():
    """Install Python dependencies"""
    print("🐍 Installing Python dependencies...")
    
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt"):
        print("❌ Failed to install Python dependencies")
        return False
    
    print("✅ Python dependencies installed successfully")
    return True

def create_env_template():
    """Create .env template file"""
    env_template = """# AI Invoice Tool Environment Variables

# OpenAI API Key (optional - for enhanced data extraction)
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Default extraction model (optional)
DEFAULT_EXTRACTION_MODEL=gpt-3.5-turbo

# Google Sheets Integration (optional)
# Upload credentials.json file via the Settings page instead
"""
    
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(env_template)
        print("✅ Created .env template file")
    else:
        print("ℹ️  .env file already exists")

def setup_directories():
    """Create necessary directories"""
    directories = ["temp", "uploads", "exports"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created {directory}/ directory")

def test_installation():
    """Test if the installation works"""
    print("🧪 Testing installation...")
    
    try:
        # Test core imports
        import streamlit
        import reportlab
        import pandas
        print("✅ Core dependencies working")
        
        # Test OCR imports
        try:
            import pytesseract
            import easyocr
            import fitz
            import PIL
            print("✅ OCR dependencies working")
        except ImportError as e:
            print(f"⚠️  Some OCR dependencies missing: {e}")
        
        # Test optional imports
        try:
            import openai
            print("✅ OpenAI integration available")
        except ImportError:
            print("ℹ️  OpenAI not installed (optional)")
        
        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
            print("✅ Google Sheets integration available")
        except ImportError:
            print("ℹ️  Google Sheets integration not installed (optional)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Installation test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 AI Invoice Tool Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install system dependencies
    install_system_dependencies()
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Setup failed at Python dependencies")
        sys.exit(1)
    
    # Create environment template
    create_env_template()
    
    # Setup directories
    setup_directories()
    
    # Test installation
    if test_installation():
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Edit .env file with your API keys (optional)")
        print("2. Run: streamlit run app.py")
        print("3. Open http://localhost:8501 in your browser")
        print("\n📚 For detailed instructions, see README.md")
    else:
        print("\n❌ Setup completed with warnings")
        print("Check the messages above and install missing dependencies")

if __name__ == "__main__":
    main() 
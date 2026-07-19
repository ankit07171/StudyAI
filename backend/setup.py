"""
Setup script for AI Study Assistant backend
"""
import os
import sys
from pathlib import Path


def create_directories():
    """Create necessary directories"""
    directories = [
        'uploads',
        'logs',
        'exports',
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def check_env_file():
    """Check if .env file exists"""
    if not Path('.env').exists():
        print("⚠ .env file not found!")
        print("→ Copying .env.example to .env")
        
        if Path('.env.example').exists():
            import shutil
            shutil.copy('.env.example', '.env')
            print("✓ Created .env file")
            print("→ Please edit .env and add your API keys")
        else:
            print("✗ .env.example not found!")
            return False
    else:
        print("✓ .env file exists")
    
    return True


def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 10):
        print("✗ Python 3.10+ is required")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def main():
    """Main setup function"""
    print("=" * 50)
    print("AI Study Assistant - Backend Setup")
    print("=" * 50)
    print()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Check environment file
    print("\n🔐 Checking environment configuration...")
    check_env_file()
    
    print("\n" + "=" * 50)
    print("✓ Setup complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Edit .env file with your API keys")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Create database: createdb studyai")
    print("4. Run server: python main.py")
    print("\nAPI Docs will be available at: http://localhost:8000/api/docs")


if __name__ == "__main__":
    main()

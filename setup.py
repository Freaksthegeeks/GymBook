#!/usr/bin/env python3
"""
Setup script for GymBook - Gym Management App
This script helps set up the initial configuration for the app.
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_flutter():
    """Check if Flutter is installed."""
    print("🔍 Checking Flutter installation...")
    try:
        result = subprocess.run(['flutter', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Flutter is installed")
            return True
        else:
            print("❌ Flutter is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("❌ Flutter is not installed or not in PATH")
        return False

def setup_flutter():
    """Set up Flutter dependencies."""
    print("\n📱 Setting up Flutter project...")
    
    # Get Flutter dependencies
    if not run_command("flutter pub get", "Getting Flutter dependencies"):
        return False
    
    # Check for any issues
    if not run_command("flutter doctor", "Running Flutter doctor"):
        return False
    
    return True

def setup_python():
    """Set up Python dependencies."""
    print("\n🐍 Setting up Python dependencies...")
    
    # Install required packages
    packages = [
        "fastapi",
        "uvicorn[standard]",
        "psycopg2-binary",
        "pydantic"
    ]
    
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            return False
    
    return True

def create_env_file():
    """Create environment configuration file."""
    print("\n⚙️ Creating environment configuration...")
    
    env_content = """# GymBook Environment Configuration

# Database Configuration
DB_NAME=gym
DB_USER=skvar
DB_PASSWORD=Root1234
DB_HOST=localhost
DB_PORT=5432

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Flutter Configuration
FLUTTER_API_URL=http://10.0.2.2:8000
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Environment file created (.env)")
        return True
    except Exception as e:
        print(f"❌ Failed to create environment file: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Welcome to GymBook Setup!")
    print("=" * 50)
    
    # Check Flutter
    if not check_flutter():
        print("\n❌ Please install Flutter first:")
        print("   Visit: https://flutter.dev/docs/get-started/install")
        sys.exit(1)
    
    # Setup Flutter
    if not setup_flutter():
        print("\n❌ Flutter setup failed")
        sys.exit(1)
    
    # Setup Python
    if not setup_python():
        print("\n❌ Python setup failed")
        sys.exit(1)
    
    # Create environment file
    if not create_env_file():
        print("\n❌ Environment setup failed")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start your PostgreSQL database")
    print("2. Run the FastAPI server: uvicorn index:app --reload --host 0.0.0.0 --port 8000")
    print("3. Run the Flutter app: flutter run")
    print("\n📖 For more information, see README.md")
    print("=" * 50)

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Setup script for GymEdge - Gym Management System
This script helps set up the initial configuration for the system.
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

def setup_python():
    """Set up Python dependencies."""
    print("\n🐍 Setting up Python dependencies...")
    
    # Install required packages
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies from requirements.txt"):
        return False
    
    return True

def create_env_file():
    """Create environment configuration file."""
    print("\n⚙️ Creating environment configuration...")
    
    env_content = """# GymEdge Environment Configuration

# Database Configuration
DB_NAME=gym
DB_USER=skvar
DB_PASSWORD=Root1234
DB_HOST=localhost
DB_PORT=5432

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration
FRONTEND_PORT=3000
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
    print("🚀 Welcome to GymEdge Setup!")
    print("=" * 50)
    
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
    print("3. Serve the frontend from the web/ directory")
    print("\n📖 For more information, see README.md")
    print("=" * 50)

if __name__ == "__main__":
    main()
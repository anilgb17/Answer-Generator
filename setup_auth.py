#!/usr/bin/env python3
"""Setup script for authentication system with key generation."""
import sys
import os
import secrets
from pathlib import Path
from cryptography.fernet import Fernet

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))


def generate_keys():
    """Generate SECRET_KEY and ENCRYPTION_KEY."""
    print("🔑 Generating security keys...")
    print("\n" + "="*60)
    print("COPY THESE KEYS TO YOUR backend/.env FILE:")
    print("="*60)
    
    secret_key = secrets.token_hex(32)
    print(f"\nSECRET_KEY={secret_key}")
    
    encryption_key = Fernet.generate_key().decode()
    print(f"ENCRYPTION_KEY={encryption_key}")
    
    print("\n" + "="*60)
    print("⚠️  IMPORTANT: Keep these keys secure and never commit them!")
    print("="*60 + "\n")
    
    return secret_key, encryption_key


def update_env_file(secret_key, encryption_key):
    """Update .env file with generated keys."""
    env_path = backend_dir / ".env"
    
    if not env_path.exists():
        print(f"⚠️  Warning: {env_path} not found")
        return False
    
    # Read current content
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Replace placeholder keys
    content = content.replace(
        "SECRET_KEY=your_secret_key_here_generate_with_secrets_token_hex",
        f"SECRET_KEY={secret_key}"
    )
    content = content.replace(
        "ENCRYPTION_KEY=your_encryption_key_here_generate_with_fernet",
        f"ENCRYPTION_KEY={encryption_key}"
    )
    
    # Write back
    with open(env_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {env_path} with generated keys")
    return True


def setup_database():
    """Initialize database and create default admin user."""
    from src.database import init_db, SessionLocal
    from src.auth import create_user
    from src.models_db import User
    
    print("\n📊 Setting up database...")
    
    # Initialize database
    print("Creating database tables...")
    init_db()
    print("✅ Database tables created")
    
    # Create default admin user
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
        
        if existing_admin:
            print("✅ Admin user already exists")
        else:
            admin = create_user(
                db=db,
                email="admin@example.com",
                username="admin",
                password="admin123",
                is_admin=True
            )
            print(f"✅ Created admin user: {admin.email}")
            print("   Default password: admin123")
            print("   ⚠️  Please change this password after first login!")
    
    finally:
        db.close()


def main():
    """Main setup function."""
    print("="*60)
    print("AUTHENTICATION SYSTEM SETUP")
    print("="*60)
    
    # Step 1: Generate keys
    secret_key, encryption_key = generate_keys()
    
    # Step 2: Ask if user wants to auto-update .env
    response = input("Do you want to automatically update backend/.env? (y/n): ").lower()
    if response == 'y':
        update_env_file(secret_key, encryption_key)
    else:
        print("⚠️  Please manually copy the keys to backend/.env")
    
    # Step 3: Setup database
    try:
        setup_database()
    except Exception as e:
        print(f"\n❌ Error setting up database: {e}")
        print("Make sure you have updated the .env file with the keys first!")
        return
    
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start Redis: docker-compose up redis -d")
    print("2. Start backend: cd backend && uvicorn src.main:app --reload")
    print("3. Login with: admin@example.com / admin123")
    print("4. Change admin password immediately!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

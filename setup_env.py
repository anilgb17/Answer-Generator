#!/usr/bin/env python3
"""
Setup script to create .env file with generated security keys
"""
import secrets
import shutil
from pathlib import Path

def setup_env():
    print("=" * 60)
    print("🔧 Answer Generator - Environment Setup")
    print("=" * 60)
    
    env_example = Path("backend/.env.example")
    env_file = Path("backend/.env")
    
    # Check if .env already exists
    if env_file.exists():
        response = input("\n⚠️  .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("❌ Setup cancelled.")
            return
    
    # Copy .env.example to .env
    print("\n📋 Creating .env file from template...")
    shutil.copy(env_example, env_file)
    
    # Generate security keys
    print("🔐 Generating security keys...")
    secret_key = secrets.token_hex(32)
    encryption_key = secrets.token_urlsafe(32)
    
    # Read the file
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Replace empty keys with generated ones
    content = content.replace('SECRET_KEY=', f'SECRET_KEY={secret_key}')
    content = content.replace('ENCRYPTION_KEY=', f'ENCRYPTION_KEY={encryption_key}')
    
    # Write back
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("\n✅ Environment file created successfully!")
    print("\n" + "=" * 60)
    print("📝 NEXT STEPS:")
    print("=" * 60)
    print("\n1. Open backend/.env file")
    print("\n2. Add at least ONE API key (Gemini recommended - FREE):")
    print("   • Gemini (FREE): https://makersuite.google.com/app/apikey")
    print("   • Perplexity (FREE tier): https://www.perplexity.ai/settings/api")
    print("   • OpenAI (PAID): https://platform.openai.com/api-keys")
    print("   • Anthropic (PAID): https://console.anthropic.com/")
    print("\n3. Save the file")
    print("\n4. Start the application:")
    print("   • Windows: start-project.bat")
    print("   • Linux/Mac: docker-compose up -d")
    print("\n" + "=" * 60)
    print("\n🔒 Security keys generated:")
    print(f"   SECRET_KEY: {secret_key}")
    print(f"   ENCRYPTION_KEY: {encryption_key}")
    print("\n⚠️  Keep these keys secret! Never commit .env to git.")
    print("=" * 60)

if __name__ == "__main__":
    try:
        setup_env()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please ensure you're running this from the project root directory.")

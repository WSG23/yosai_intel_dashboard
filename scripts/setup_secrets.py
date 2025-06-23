#!/usr/bin/env python3
"""
Secure Secret Key Management for Yōsai Intel Dashboard
Generates environment-specific keys with proper security
"""
import secrets
import os
from pathlib import Path
import argparse

def generate_secure_key(length=32):
    """Generate cryptographically secure key"""
    return secrets.token_hex(length)

def setup_environment(env='development'):
    """Setup secrets for specific environment"""
    
    # Key lengths by environment
    key_lengths = {
        'development': 32,  # 64 hex chars
        'staging': 32,      # 64 hex chars  
        'production': 64    # 128 hex chars (extra secure)
    }
    
    length = key_lengths.get(env, 32)
    secret_key = generate_secure_key(length)
    
    # Environment-specific .env files
    env_file = f".env.{env}" if env != 'development' else ".env"
    
    # Template for environment file
    env_template = f"""# Yōsai Intel Dashboard - {env.title()} Environment
# Generated on: {os.popen('date').read().strip()}
# SECURITY: Never commit this file to version control

# Application Configuration
YOSAI_ENV={env}
SECRET_KEY={secret_key}
DEBUG={'true' if env == 'development' else 'false'}

# Database Configuration
DB_TYPE={'mock' if env == 'development' else 'postgresql'}
DB_HOST={'localhost' if env == 'development' else 'your-db-host'}
DB_PORT=5432
DB_NAME=yosai_{env}
DB_USER=yosai_user
DB_PASSWORD=change-me-to-secure-password

# Security Settings
WTF_CSRF_ENABLED=true
CORS_ORIGINS={'http://localhost:3000' if env == 'development' else 'https://yourdomain.com'}

# Monitoring (Production only)
SENTRY_DSN={'' if env == 'development' else 'your-sentry-dsn-here'}
"""

    # Write environment file
    Path(env_file).write_text(env_template)
    
    print(f"✅ Created {env_file}")
    print(f"🔑 Secret key length: {len(secret_key)} characters")
    print(f"🔒 Environment: {env}")
    
    # Update .gitignore
    gitignore_entries = [
        ".env",
        ".env.local", 
        ".env.development",
        ".env.staging",
        ".env.production",
        "*.key",
        "secrets/"
    ]
    
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        existing = gitignore_path.read_text()
        new_entries = [entry for entry in gitignore_entries if entry not in existing]
        if new_entries:
            with open(gitignore_path, 'a') as f:
                f.write("\n# Secret files (auto-added)\n")
                for entry in new_entries:
                    f.write(f"{entry}\n")
            print(f"✅ Updated .gitignore with {len(new_entries)} entries")
    
    return secret_key

def main():
    parser = argparse.ArgumentParser(description='Setup secure secrets for Yōsai Dashboard')
    parser.add_argument('--env', choices=['development', 'staging', 'production'], 
                       default='development', help='Environment to setup')
    parser.add_argument('--rotate', action='store_true', 
                       help='Rotate existing secret (generate new one)')
    
    args = parser.parse_args()
    
    if args.rotate:
        print(f"🔄 Rotating secret key for {args.env} environment...")
    
    secret_key = setup_environment(args.env)
    
    print(f"\n🚀 To use this environment:")
    print(f"   export YOSAI_ENV={args.env}")
    print(f"   python3 app.py")
    
    if args.env == 'production':
        print(f"\n⚠️  PRODUCTION SECURITY REMINDERS:")
        print(f"   1. Store SECRET_KEY in secure vault (AWS Secrets Manager, etc.)")
        print(f"   2. Use different database passwords")
        print(f"   3. Configure HTTPS/TLS certificates")
        print(f"   4. Set up proper monitoring")

if __name__ == "__main__":
    main()
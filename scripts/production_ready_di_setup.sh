#!/bin/bash
# production_ready_di_setup.sh - Get your DI system production ready NOW

echo "🚀 YŌSAI INTEL DI - PRODUCTION SETUP"
echo "===================================="

# 1. Create missing files
echo "📁 Creating missing files..."

# Create core/__init__.py
cat > core/__init__.py << 'EOF'
"""
Yōsai Intel Dashboard - Core Package
Dependency Injection and application management
"""

from .container import Container, get_container, reset_container
from .config_manager import ConfigManager
from .app_factory import create_application
from .service_registry import get_configured_container

__all__ = [
    'Container',
    'get_container', 
    'reset_container',
    'ConfigManager',
    'create_application',
    'get_configured_container'
]

__version__ = '1.0.0'
EOF

# 2. Create verification script
echo "🧪 Creating verification script..."

cat > verify_di_production.py << 'EOF'
#!/usr/bin/env python3
"""Quick production readiness check for DI system"""

def verify_production_readiness():
    """Verify DI system is production ready"""
    print("🔍 Verifying Production Readiness...")
    
    checks = [
        ("Core imports", check_core_imports),
        ("Container functionality", check_container),
        ("Service registry", check_service_registry),
        ("App creation", check_app_creation),
        ("Health monitoring", check_health)
    ]
    
    passed = 0
    for name, check_func in checks:
        try:
            if check_func():
                print(f"✅ {name}")
                passed += 1
            else:
                print(f"❌ {name}")
        except Exception as e:
            print(f"💥 {name}: {e}")
    
    score = (passed / len(checks)) * 100
    
    if score >= 80:
        print(f"\n🎉 PRODUCTION READY! Score: {score:.0f}%")
        return True
    else:
        print(f"\n⚠️  Needs work. Score: {score:.0f}%")
        return False

def check_core_imports():
    """Check core package imports"""
    from core import Container, ConfigManager, create_application
    return True

def check_container():
    """Check container functionality"""
    from core.container import Container
    container = Container()
    container.register('test', lambda: "works")
    return container.get('test') == "works"

def check_service_registry():
    """Check service registry"""
    from core.service_registry import get_configured_container
    container = get_configured_container()
    return container.has('config')

def check_app_creation():
    """Check app creation"""
    from core.app_factory import create_application
    app = create_application()
    return app is not None

def check_health():
    """Check health monitoring"""
    from core.service_registry import get_configured_container
    container = get_configured_container()
    health = container.health_check()
    return health['status'] in ['healthy', 'degraded']

if __name__ == "__main__":
    success = verify_production_readiness()
    exit(0 if success else 1)
EOF

chmod +x verify_di_production.py

# 3. Create production configuration
echo "⚙️ Creating production configuration..."

cat > config/production.yaml << 'EOF'
# Production configuration for DI system
app:
  debug: false
  host: "0.0.0.0"
  port: 8050
  secret_key: "${SECRET_KEY}"

database:
  type: "${DB_TYPE:-postgresql}"
  host: "${DB_HOST:-localhost}"
  port: "${DB_PORT:-5432}"
  name: "${DB_NAME:-yosai_intel}"
  user: "${DB_USER:-postgres}"
  password: "${DB_PASSWORD}"
  pool_size: "${DB_POOL_SIZE:-10}"

cache:
  type: "redis"
  url: "${REDIS_URL:-redis://localhost:6379/0}"
  timeout: 300

monitoring:
  health_check_interval: 30
  log_level: "INFO"
  metrics_enabled: true
EOF

# 4. Create environment template
echo "🌍 Creating environment template..."

cat > .env.production.template << 'EOF'
# Production Environment Variables
# Copy to .env and fill in actual values

# App Configuration
SECRET_KEY=your-super-secret-key-change-this
DEBUG=False
HOST=0.0.0.0
PORT=8050

# Database Configuration
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=yosai_intel
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_POOL_SIZE=10

# Cache Configuration
REDIS_URL=redis://localhost:6379/0

# Monitoring
LOG_LEVEL=INFO
HEALTH_CHECK_ENABLED=True
EOF

# 5. Create startup script
echo "🚀 Creating startup script..."

cat > start_production.sh << 'EOF'
#!/bin/bash
# Production startup script

echo "🏯 Starting Yōsai Intel Dashboard (Production)"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📋 Copy .env.production.template to .env and configure"
    exit 1
fi

# Verify DI system
echo "🔍 Verifying DI system..."
python verify_di_production.py

if [ $? -ne 0 ]; then
    echo "❌ DI verification failed!"
    exit 1
fi

# Start application
echo "🚀 Starting application..."
python app.py
EOF

chmod +x start_production.sh

# 6. Run verification
echo "🧪 Running verification..."
python verify_di_production.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! Your DI system is production ready!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Copy .env.production.template to .env"
    echo "2. Fill in your actual configuration values"
    echo "3. Run: ./start_production.sh"
    echo "4. Access: http://localhost:8050"
    echo ""
    echo "🏆 Ready for Priority 3: Configuration Management!"
else
    echo ""
    echo "⚠️  Some issues detected. Please fix and try again."
fi
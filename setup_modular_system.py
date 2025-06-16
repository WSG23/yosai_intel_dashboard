# setup_modular_system.py - Complete modular system setup and configuration
"""
Yōsai Intel Dashboard - Modular System Setup Script
Automatically configures the entire modular architecture
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

class ModularSystemSetup:
    """Handles complete setup of the modular system"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.setup_results: Dict[str, bool] = {}
        
    def create_project_structure(self) -> None:
        """Create the complete modular project structure"""
        
        directories = [
            "config",
            "models", 
            "services",
            "components",
            "components/analytics",
            "pages",
            "pages/analytics",
            "utils",
            "assets",
            "assets/css",
            "assets/css/01-foundation",
            "assets/css/02-layout", 
            "assets/css/03-components",
            "assets/css/04-panels",
            "assets/css/05-pages",
            "assets/css/06-themes",
            "assets/css/07-utilities",
            "data",
            "data/uploads",
            "tests",
            "docs"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py files for Python packages
            if not directory.startswith(('assets', 'data', 'docs')):
                init_file = dir_path / "__init__.py"
                if not init_file.exists():
                    init_file.write_text("")
        
        print("✅ Project structure created")
        self.setup_results['project_structure'] = True
    
    def create_configuration_files(self) -> None:
        """Create configuration files"""
        
        # Environment configuration
        env_content = """# Yōsai Intel Dashboard Configuration
# Database Configuration
DB_TYPE=mock
DB_HOST=localhost
DB_PORT=5432
DB_NAME=yosai_intel
DB_USER=postgres
DB_PASSWORD=
DB_POOL_SIZE=5

# Application Configuration
DEBUG=True
HOST=127.0.0.1
PORT=8050

# Security
SECRET_KEY=your-secret-key-change-this-in-production

# File Upload
MAX_FILE_SIZE=100MB
UPLOAD_FOLDER=data/uploads

# Analytics
CACHE_TIMEOUT=300
"""
        
        env_file = self.project_root / ".env.example"
        env_file.write_text(env_content)
        
        # Docker configuration
        dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8050

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD curl -f http://localhost:8050/ || exit 1

# Run application
CMD ["python", "app.py"]
"""
        
        dockerfile = self.project_root / "Dockerfile"
        dockerfile.write_text(dockerfile_content)
        
        # Docker Compose
        docker_compose_content = """version: '3.8'

services:
  dashboard:
    build: .
    ports:
      - "8050:8050"
    environment:
      - DB_TYPE=postgresql
      - DB_HOST=postgres
      - DB_NAME=yosai_intel
      - DB_USER=postgres
      - DB_PASSWORD=password
    depends_on:
      - postgres
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: yosai_intel
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database_setup.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped

volumes:
  postgres_data:
"""
        
        docker_compose_file = self.project_root / "docker-compose.yml"
        docker_compose_file.write_text(docker_compose_content)
        
        print("✅ Configuration files created")
        self.setup_results['configuration'] = True
    
    def create_requirements_file(self) -> None:
        """Create comprehensive requirements.txt"""
        
        requirements_content = """# Core Dash Dependencies
dash>=2.14.1
dash-bootstrap-components>=1.5.0
plotly>=5.15.0

# Data Processing
pandas>=2.1.1
numpy>=1.25.2
openpyxl>=3.1.2

# Database
psycopg2-binary>=2.9.7
sqlalchemy>=2.0.0

# File Processing
python-multipart>=0.0.6

# Development
python-dotenv>=1.0.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0

# Type Checking
mypy>=1.5.0
types-python-dateutil

# Code Quality
black>=23.0.0
flake8>=6.0.0
isort>=5.12.0

# Documentation
sphinx>=7.1.0
sphinx-rtd-theme>=1.3.0

# Production
gunicorn>=21.2.0
redis>=4.6.0

# Monitoring
sentry-sdk[flask]>=1.32.0

# Geographic/Map (optional)
geopandas>=0.13.0
shapely>=2.0.0
"""
        
        requirements_file = self.project_root / "requirements.txt"
        requirements_file.write_text(requirements_content)
        
        print("✅ Requirements file created")
        self.setup_results['requirements'] = True
    
    def create_git_configuration(self) -> None:
        """Create Git configuration files"""
        
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Environment Variables
.env
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo

# Dash
assets/.webassets-cache

# Data
data/uploads/*
!data/uploads/.gitkeep
*.csv
*.xlsx
*.json
logs/

# Database
*.db
*.sqlite3

# Cache
.cache/
.pytest_cache/

# Coverage
htmlcov/
.coverage
.coverage.*
coverage.xml

# Documentation
docs/_build/

# Mac
.DS_Store

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini

# Backup files
*.backup
*.bak
"""
        
        gitignore_file = self.project_root / ".gitignore"
        gitignore_file.write_text(gitignore_content)
        
        # Git attributes
        gitattributes_content = """# Auto detect text files and perform LF normalization
* text=auto

# Python files
*.py text eol=lf

# Web files
*.html text eol=lf
*.css text eol=lf
*.js text eol=lf
*.json text eol=lf

# Config files
*.yml text eol=lf
*.yaml text eol=lf
*.ini text eol=lf
*.cfg text eol=lf

# Documentation
*.md text eol=lf
*.rst text eol=lf

# Data files (treat as binary)
*.csv binary
*.xlsx binary
*.xls binary
*.db binary
*.sqlite binary
"""
        
        gitattributes_file = self.project_root / ".gitattributes"
        gitattributes_file.write_text(gitattributes_content)
        
        print("✅ Git configuration created")
        self.setup_results['git'] = True
    
    def create_testing_configuration(self) -> None:
        """Create testing configuration"""
        
        # Pytest configuration
        pytest_ini_content = """[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    database: Tests requiring database
"""
        
        pytest_ini = self.project_root / "pytest.ini"
        pytest_ini.write_text(pytest_ini_content)
        
        # MyPy configuration
        mypy_ini_content = """[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True

[mypy-dash.*]
ignore_missing_imports = True

[mypy-plotly.*]
ignore_missing_imports = True

[mypy-pandas.*]
ignore_missing_imports = True
"""
        
        mypy_ini = self.project_root / "mypy.ini"
        mypy_ini.write_text(mypy_ini_content)
        
        print("✅ Testing configuration created")
        self.setup_results['testing'] = True
    
    def create_documentation_structure(self) -> None:
        """Create documentation structure"""
        
        docs_dir = self.project_root / "docs"
        
        # README
        readme_content = """# Yōsai Intel Dashboard

An AI-powered modular security intelligence dashboard for physical access control monitoring.

## 🏗️ Modular Architecture

This project follows a fully modular architecture for maximum maintainability and testability:

```
yosai_intel_dashboard/
├── app.py                     # Main application entry point
├── config/                    # Configuration management
│   ├── database_manager.py    # Database connections and pooling
│   └── settings.py           # Application settings
├── models/                    # Data models and business entities
│   ├── base.py               # Base model classes
│   ├── entities.py           # Core entities (Person, Door, Facility)
│   ├── events.py             # Event models (AccessEvent, Anomaly)
│   ├── enums.py              # Enumerated types
│   └── access_events.py      # Access event operations
├── services/                  # Business logic layer
│   └── analytics_service.py  # Analytics and data processing
├── components/               # UI components
│   ├── analytics/            # Analytics-specific components
│   ├── navbar.py             # Navigation component
│   └── map_panel.py          # Map visualization
├── pages/                    # Multi-page application pages
│   └── deep_analytics.py     # Analytics page
├── utils/                    # Utility functions
└── assets/                   # Static assets and CSS
    └── css/                  # Modular CSS architecture
```

## 🚀 Quick Start

### Development Setup

1. **Clone and enter the project:**
   ```bash
   git clone <repository>
   cd yosai_intel_dashboard
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Access the dashboard:**
   Open http://127.0.0.1:8050 in your browser

### Production Deployment

Using Docker Compose:
```bash
docker-compose up -d
```

## 🧪 Testing

Run the complete test suite:
```bash
# Validate modular architecture
python test_modular_system.py

# Run unit tests
pytest

# Run type checking
mypy .

# Check code quality
black . --check
flake8 .
```

## 📋 Features

- **Real-time Security Monitoring**: Live access control event monitoring
- **AI-Powered Anomaly Detection**: Advanced pattern recognition
- **Interactive Analytics**: Deep dive data analysis with file uploads
- **Modular Architecture**: Easy to maintain, test, and extend
- **Multi-page Interface**: Organized functionality across multiple pages
- **Type-Safe**: Full type annotations and validation

## 🔧 Configuration

### Database

Configure your database in `.env`:
```
DB_TYPE=postgresql  # or 'sqlite' or 'mock'
DB_HOST=localhost
DB_PORT=5432
DB_NAME=yosai_intel
DB_USER=your_user
DB_PASSWORD=your_password
```

### Application

Key configuration options:
```
DEBUG=False           # Set to False for production
HOST=0.0.0.0         # Bind to all interfaces for production
PORT=8050            # Application port
SECRET_KEY=your-key  # Change for production
```

## 📊 Modular Components

### Database Layer (`config/`)
- **database_manager.py**: Connection pooling, multiple database support
- Supports PostgreSQL, SQLite, and Mock databases
- Type-safe connection management

### Models Layer (`models/`)
- **entities.py**: Core business entities
- **events.py**: Event and transaction models
- **enums.py**: Type-safe enumerations
- Full type annotations and validation

### Services Layer (`services/`)
- **analytics_service.py**: Business logic for analytics
- Caching and performance optimization
- Modular and testable

### Components Layer (`components/`)
- Reusable UI components
- Independent and testable
- Type-safe prop interfaces

## 🤝 Contributing

1. Ensure all tests pass: `python test_modular_system.py`
2. Follow type safety guidelines
3. Maintain modular architecture principles
4. Update documentation for new features

## 📄 License

MIT License - see LICENSE file for details.
"""
        
        readme_file = self.project_root / "README.md"
        readme_file.write_text(readme_content)
        
        # API Documentation
        api_docs_content = """# API Documentation

## Database Manager

### `DatabaseManager`

Factory class for creating database connections.

#### Methods

- `from_environment() -> DatabaseConfig`: Create config from environment variables
- `create_connection(config) -> DatabaseConnection`: Create database connection
- `test_connection(config) -> bool`: Test database connectivity

## Analytics Service

### `AnalyticsService`

Centralized analytics service for dashboard operations.

#### Methods

- `get_dashboard_summary() -> Dict[str, Any]`: Get dashboard overview
- `get_access_patterns_analysis(days) -> Dict[str, Any]`: Analyze access patterns
- `process_uploaded_file(df, filename) -> Dict[str, Any]`: Process uploaded data

## Models

### `AccessEvent`

Represents a single access control event.

#### Attributes

- `event_id: str`: Unique event identifier
- `timestamp: datetime`: When the event occurred
- `person_id: str`: Person attempting access
- `door_id: str`: Door being accessed
- `access_result: AccessResult`: Success/failure of access
"""
        
        api_docs_file = docs_dir / "api.md"
        api_docs_file.write_text(api_docs_content)
        
        print("✅ Documentation created")
        self.setup_results['documentation'] = True
    
    def setup_development_tools(self) -> None:
        """Setup development tools and scripts"""
        
        # Development script
        dev_script_content = """#!/bin/bash
# Development helper script

set -e

echo "🚀 Yōsai Intel Dashboard - Development Setup"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run: python -m venv venv"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run tests
echo "🧪 Running tests..."
python test_modular_system.py

# Start application
echo "🎯 Starting application..."
python app.py
"""
        
        dev_script = self.project_root / "dev.sh"
        dev_script.write_text(dev_script_content)
        dev_script.chmod(0o755)
        
        # Production script
        prod_script_content = """#!/bin/bash
# Production deployment script

set -e

echo "🚀 Yōsai Intel Dashboard - Production Deployment"

# Build and start with Docker Compose
echo "🐳 Building and starting services..."
docker-compose down
docker-compose build
docker-compose up -d

echo "✅ Services started!"
echo "Dashboard: http://localhost:8050"
echo "Database: localhost:5432"

# Show logs
echo "📋 Following logs (Ctrl+C to exit)..."
docker-compose logs -f dashboard
"""
        
        prod_script = self.project_root / "deploy.sh"
        prod_script.write_text(prod_script_content)
        prod_script.chmod(0o755)
        
        print("✅ Development tools created")
        self.setup_results['dev_tools'] = True
    
    def run_setup(self) -> None:
        """Run complete setup process"""
        
        print("🚀 Setting up Yōsai Intel Modular System...")
        print("=" * 50)
        
        try:
            self.create_project_structure()
            self.create_requirements_file()
            self.create_configuration_files()
            self.create_git_configuration()
            self.create_testing_configuration()
            self.create_documentation_structure()
            self.setup_development_tools()
            
            print("\n" + "=" * 50)
            print("✅ Setup completed successfully!")
            
            # Print summary
            self.print_setup_summary()
            
        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            print("Please check the error and try again.")
    
    def print_setup_summary(self) -> None:
        """Print setup summary and next steps"""
        
        print(f"\n📋 SETUP SUMMARY")
        print("-" * 30)
        
        for component, success in self.setup_results.items():
            status = "✅" if success else "❌"
            print(f"{status} {component.replace('_', ' ').title()}")
        
        total_success = sum(self.setup_results.values())
        total_components = len(self.setup_results)
        
        print(f"\nCompleted: {total_success}/{total_components} components")
        
        if total_success == total_components:
            print(f"\n🎉 Perfect! All components set up successfully!")
            print(f"\n📋 NEXT STEPS:")
            print(f"1. Create virtual environment: python -m venv venv")
            print(f"2. Activate environment: source venv/bin/activate")
            print(f"3. Install dependencies: pip install -r requirements.txt")
            print(f"4. Copy environment config: cp .env.example .env")
            print(f"5. Run validation: python test_modular_system.py")
            print(f"6. Start development: ./dev.sh")
            print(f"\n🚀 Ready for development!")
        else:
            print(f"\n⚠️  Some components had issues. Please check above.")

def main():
    """Main execution function"""
    
    # Get project root
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])
    else:
        project_root = Path(".")
    
    project_root = project_root.resolve()
    
    print("🏗️  YŌSAI INTEL MODULAR SYSTEM SETUP")
    print("=" * 50)
    print(f"Project Root: {project_root}")
    
    if not project_root.exists():
        print(f"❌ Directory not found: {project_root}")
        sys.exit(1)
    
    # Create setup instance
    setup = ModularSystemSetup(project_root)
    
    # Run setup
    setup.run_setup()

if __name__ == "__main__":
    main()
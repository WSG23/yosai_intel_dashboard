# Yōsai Intel Dashboard

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
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Make sure all dependencies are installed **before** running Pyright or using
   the Pylance extension. Missing packages will otherwise appear as unresolved
   imports.

4. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration (e.g. set HOST and database info)
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Access the dashboard:**
   Open http://127.0.0.1:8050 in your browser

### Troubleshooting

If Pylance shows unresolved imports or type errors, your editor may not be
using the virtual environment where dependencies were installed. Try the
following steps:

1. Activate the virtual environment:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Restart your editor so Pylance picks up the correct interpreter.

### Production Deployment

Using Docker Compose:
```bash
docker-compose up -d
```
Docker Compose reads variables from a `.env` file in this directory. Set
`DB_PASSWORD` there (or export it in your shell) before starting the services.

## 🧪 Testing

Run the complete test suite:
```bash
# Validate modular architecture
python test_modular_system.py

# Run dashboard integration tests
python tests/test_dashboard.py

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

This project uses **`config/yaml_config.py`** as the single source of
configuration. Earlier versions included a `unified_config.py` module, but it
has been removed in favor of the YAML-based system. All settings are loaded from
YAML files in `config/` and can be overridden via environment variables.

### Database

Configure your database in `.env`:
```
DB_TYPE=postgresql  # or 'sqlite' or 'mock'
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

### Application

Key configuration options:
```
DEBUG=False           # Set to False for production
HOST=0.0.0.0         # Bind to all interfaces for production
PORT=8050            # Application port
SECRET_KEY=your-key  # Change for production
```

### Environment Overrides

`ConfigurationManager` loads YAML files from `config/` and then checks for
environment variables. When a variable name matches a key used in the YAML
configuration (for example `DB_HOST`, `DB_USER`, `REDIS_HOST` or
`SECRET_KEY`), its value replaces the one from the file. This lets you adjust
settings without editing the YAML files.

Example:

```bash
DB_HOST=localhost
DB_USER=postgres
REDIS_HOST=localhost
SECRET_KEY=supersecret
python app.py
```

These values override `database.host`, `database.username`, `cache.host` and
`security.secret_key` from the loaded YAML.

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

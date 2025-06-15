# config/settings.py
import os
from typing import Dict, Any

class Config:
    """Base configuration class"""
    # Database settings
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/yosai_intel')
    
    # Redis settings for caching
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {'csv', 'json', 'xlsx', 'xls'}
    
    # Security settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    
    # Analytics settings
    CACHE_TIMEOUT = 300  # 5 minutes
    MAX_RECORDS_DISPLAY = 10000
    
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig()
    else:
        return DevelopmentConfig()

# config/database.py
import psycopg2
import pandas as pd
from typing import Dict, Any, Optional
import logging

class DatabaseConnection:
    """Database connection and query handler"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(self.database_url)
            logging.info("Database connection established")
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            raise
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """Execute query and return DataFrame"""
        if not self.connection:
            self.connect()
            
        try:
            df = pd.read_sql_query(query, self.connection, params=params)
            return df
        except Exception as e:
            logging.error(f"Query execution failed: {e}")
            return pd.DataFrame()
    
    def execute_command(self, command: str, params: Optional[tuple] = None):
        """Execute command (INSERT, UPDATE, DELETE)"""
        if not self.connection:
            self.connect()
            
        try:
            cursor = self.connection.cursor()
            cursor.execute(command, params)
            self.connection.commit()
            cursor.close()
        except Exception as e:
            logging.error(f"Command execution failed: {e}")
            self.connection.rollback()
            raise
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed")
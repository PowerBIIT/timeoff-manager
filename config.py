import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration with environment variable validation"""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SMTP (optional - może być None)
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USE_SSL = os.getenv('SMTP_USE_SSL', 'true').lower() == 'true'
    SMTP_LOGIN = os.getenv('SMTP_LOGIN')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    EMAIL_FROM = os.getenv('EMAIL_FROM')

    # Azure
    APP_NAME = os.getenv('APP_NAME', 'timeoff-manager-app')

    @staticmethod
    def validate():
        """Validate required environment variables"""
        required = ['DATABASE_URL', 'SECRET_KEY']
        missing = [var for var in required if not os.getenv(var)]

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        return True

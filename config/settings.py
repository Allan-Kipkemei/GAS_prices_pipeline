import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    # Database
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_SSL_MODE = os.getenv('DB_SSL_MODE')
    
    # Construct DB URL
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # API Keys
    EIA_API_KEY = os.getenv('EIA_API_KEY')
    OPEN_ENERGY_API_KEY = os.getenv('OPEN_ENERGY_API_KEY')
    KENYA_FUEL_API_KEY = os.getenv('KENYA_FUEL_API_KEY')
    
    # Email Settings
    ALERT_EMAIL = os.getenv('ALERT_EMAIL')
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = os.getenv('SMTP_PORT')
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    
    # Application
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    TIMEZONE = 'Africa/Nairobi'
    
    # API Endpoints
    EIA_BASE_URL = "https://api.eia.gov/v2"
    OPEN_ENERGY_BASE_URL = "https://api.openenergyplatform.org"
    
    # Thresholds
    PRICE_CHANGE_ALERT_PERCENT = 5.0
    ANOMALY_THRESHOLD = 3.0  # Standard deviations

settings = Settings()
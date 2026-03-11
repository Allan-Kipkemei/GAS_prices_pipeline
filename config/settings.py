import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / '.env'

# Load variables from the project root regardless of the current working directory.
load_dotenv(dotenv_path=ENV_PATH)


class Settings:
    def __init__(self) -> None:
        # Database
        self.DB_HOST = os.getenv('DB_HOST', 'localhost')
        self.DB_PORT = os.getenv('DB_PORT', '5432')
        self.DB_NAME = os.getenv('DB_NAME')
        self.DB_USER = os.getenv('DB_USER')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD')
        self.DB_SSL_MODE = os.getenv('DB_SSL_MODE')

        # Prefer a complete DATABASE_URL when present, otherwise build one from components.
        self.DATABASE_URL = os.getenv('DATABASE_URL') or self._build_database_url()

        # API Keys
        self.EIA_API_KEY = os.getenv('EIA_API_KEY')
        self.OPEN_ENERGY_API_KEY = os.getenv('OPEN_ENERGY_API_KEY')
        self.KENYA_FUEL_API_KEY = os.getenv('KENYA_FUEL_API_KEY')

        # Email Settings
        self.ALERT_EMAIL = os.getenv('ALERT_EMAIL')
        self.SMTP_SERVER = os.getenv('SMTP_SERVER', os.getenv('SMTP_HOST'))
        self.SMTP_PORT = os.getenv('SMTP_PORT', '587')
        self.SMTP_USERNAME = os.getenv('SMTP_USERNAME', os.getenv('SMTP_USER'))
        self.SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

        # Application
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.TIMEZONE = os.getenv('TIMEZONE', 'Africa/Nairobi')

        # API Endpoints
        self.EIA_BASE_URL = os.getenv('EIA_BASE_URL', 'https://api.eia.gov/v2')
        self.OPEN_ENERGY_BASE_URL = os.getenv(
            'OPEN_ENERGY_BASE_URL',
            'https://api.openenergyplatform.org',
        )

        # Thresholds
        self.PRICE_CHANGE_ALERT_PERCENT = float(os.getenv('PRICE_CHANGE_ALERT_PERCENT', '5.0'))
        self.ANOMALY_THRESHOLD = float(os.getenv('ANOMALY_THRESHOLD', '3.0'))

    def _build_database_url(self) -> str | None:
        required_values = [self.DB_NAME, self.DB_USER, self.DB_PASSWORD]
        if not all(required_values):
            return None

        user = quote_plus(self.DB_USER)
        password = quote_plus(self.DB_PASSWORD)
        return f'postgresql://{user}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'


settings = Settings()

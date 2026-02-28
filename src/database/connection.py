from contextlib import contextmanager
import logging
import ssl

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from config.settings import settings
from .models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None

    def connect(self):
        """Establish database connection with SSL when configured."""
        if self.engine is not None and self.SessionLocal is not None:
            return

        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            connect_args = {'ssl': ssl_context} if settings.DB_SSL_MODE == 'require' else {}

            self.engine = create_engine(
                settings.DATABASE_URL,
                echo=False,
                connect_args=connect_args,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            logger.info('Database connection established successfully')

        except Exception as e:
            logger.error(f'Failed to connect to database: {e}')
            raise

    @contextmanager
    def get_session(self):
        """Provide a transactional scope around a series of operations."""
        if self.SessionLocal is None:
            self.connect()

        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f'Database session error: {e}')
            raise
        finally:
            session.close()

    def create_tables(self):
        """Create all tables in the database."""
        if self.engine is None:
            self.connect()

        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info('Database tables created successfully')
        except SQLAlchemyError as e:
            logger.error(f'Failed to create tables: {e}')
            raise


# Singleton instance
db_manager = DatabaseManager()

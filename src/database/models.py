from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class FuelPrice(Base):
    __tablename__ = 'fuel_prices'

    id = Column(String, primary_key=True, default=generate_uuid)
    fuel_type = Column(String, nullable=False)  # petrol, diesel, kerosene, etc.
    price = Column(Float, nullable=False)
    currency = Column(String, default='KES')
    region = Column(String)  # County, state, country
    station_name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)

    # Metadata
    source = Column(String)  # API source (EIA, OpenEnergy, KenyaGov)
    source_id = Column(String)  # Original ID from API
    recorded_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Data quality flags
    is_valid = Column(Boolean, default=True)
    validation_errors = Column(JSON)

    # Indexes
    __table_args__ = (
        Index('idx_fuel_type_region', 'fuel_type', 'region'),
        Index('idx_recorded_at', 'recorded_at'),
        Index('idx_source_id', 'source_id'),
    )

class PriceTrend(Base):
    __tablename__ = 'price_trends'

    id = Column(String, primary_key=True, default=generate_uuid)
    fuel_type = Column(String, nullable=False)
    region = Column(String)

    # Metrics
    current_price = Column(Float)
    yesterday_price = Column(Float)
    week_ago_price = Column(Float)
    month_ago_price = Column(Float)

    # Changes
    day_change = Column(Float)
    day_change_percent = Column(Float)
    week_change_percent = Column(Float)
    month_change_percent = Column(Float)

    # Statistics
    rolling_7d_avg = Column(Float)
    rolling_30d_avg = Column(Float)
    volatility_7d = Column(Float)  # Standard deviation

    # Timestamps
    calculated_at = Column(DateTime, server_default=func.now())
    period_start = Column(DateTime)
    period_end = Column(DateTime)

class AnomalyLog(Base):
    __tablename__ = 'anomaly_logs'

    id = Column(String, primary_key=True, default=generate_uuid)
    fuel_price_id = Column(String, ForeignKey('fuel_prices.id'))
    anomaly_type = Column(String)  # 'spike', 'drop', 'missing'
    severity = Column(String)  # 'low', 'medium', 'high'
    deviation = Column(Float)  # How many std deviations from mean
    detected_at = Column(DateTime, server_default=func.now())
    resolved = Column(Boolean, default=False)
    notes = Column(String)

class APILog(Base):
    __tablename__ = 'api_logs'

    id = Column(String, primary_key=True, default=generate_uuid)
    source = Column(String, nullable=False)
    endpoint = Column(String)
    status_code = Column(Integer)
    response_time_ms = Column(Integer)
    records_fetched = Column(Integer)
    error_message = Column(String)
    executed_at = Column(DateTime, server_default=func.now())

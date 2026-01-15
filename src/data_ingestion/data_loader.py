from sqlalchemy.exc import IntegrityError
from datetime import datetime
import logging
from typing import List, Dict
from database.connection import db_manager
from database.models import FuelPrice, APILog
from .api_client import EnergyAPIClient

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self):
        self.api_client = EnergyAPIClient()
    
    def ingest_all_sources(self) -> Dict:
        """Ingest data from all available sources"""
        results = {
            'total_ingested': 0,
            'sources': {},
            'errors': []
        }
        
        # Ingest from EIA
        eia_results = self._ingest_eia_data()
        results['sources']['eia'] = eia_results
        results['total_ingested'] += eia_results.get('ingested', 0)
        
        # Ingest Kenya data (mock/actual)
        kenya_results = self._ingest_kenya_data()
        results['sources']['kenya'] = kenya_results
        results['total_ingested'] += kenya_results.get('ingested', 0)
        
        # Log API call
        self._log_api_call('ingest_all', results)
        
        return results
    
    def _ingest_eia_data(self) -> Dict:
        """Ingest data from EIA API"""
        start_time = datetime.now()
        
        try:
            # Fetch data
            raw_data = self.api_client.fetch_eia_prices()
            
            # Load to database
            ingested_count = 0
            with db_manager.get_session() as session:
                for item in raw_data:
                    try:
                        fuel_price = FuelPrice(
                            fuel_type=item['fuel_type'],
                            price=item['price'],
                            currency=item['currency'],
                            region=item['region'],
                            station_name=item['station_name'],
                            source=item['source'],
                            source_id=item['source_id'],
                            recorded_at=datetime.fromisoformat(item['recorded_at'].replace('Z', '+00:00')),
                            latitude=item['latitude'],
                            longitude=item['longitude']
                        )
                        session.add(fuel_price)
                        ingested_count += 1
                    except IntegrityError:
                        session.rollback()
                        # Update existing record
                        existing = session.query(FuelPrice).filter_by(
                            source_id=item['source_id']
                        ).first()
                        if existing:
                            existing.price = item['price']
                            existing.updated_at = datetime.now()
                            ingested_count += 1
                        continue
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                'status': 'success',
                'ingested': ingested_count,
                'response_time_ms': round(response_time, 2),
                'total_fetched': len(raw_data)
            }
            
        except Exception as e:
            logger.error(f"EIA ingestion failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'ingested': 0
            }
    
    def _ingest_kenya_data(self) -> Dict:
        """Ingest Kenya-specific fuel data"""
        # Similar implementation to _ingest_eia_data
        # ...
        return {'status': 'success', 'ingested': 2}  # Placeholder
    
    def _log_api_call(self, endpoint: str, results: Dict):
        """Log API call details"""
        try:
            with db_manager.get_session() as session:
                api_log = APILog(
                    source='ingestion_pipeline',
                    endpoint=endpoint,
                    status_code=200 if not results.get('errors') else 500,
                    records_fetched=results['total_ingested'],
                    executed_at=datetime.now()
                )
                session.add(api_log)
        except Exception as e:
            logger.error(f"Failed to log API call: {e}")
import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
from config.settings import settings

logger = logging.getLogger(__name__)

class EnergyAPIClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FuelPriceMonitor/1.0',
            'Accept': 'application/json'
        })
    
    def fetch_eia_prices(self, fuel_type: str = "petroleum", days: int = 1) -> List[Dict]:
        """Fetch fuel prices from EIA API"""
        try:
            endpoint = f"{settings.EIA_BASE_URL}/petroleum/pri/gnd/data/"
            params = {
                'api_key': settings.EIA_API_KEY,
                'frequency': 'daily',
                'data': ['value'],
                'facets': {'product': [fuel_type]},
                'start': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
                'end': datetime.now().strftime('%Y-%m-%d'),
                'sort': [{'column': 'period', 'direction': 'desc'}],
                'offset': 0,
                'length': 5000
            }
            
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched {len(data.get('response', {}).get('data', []))} records from EIA")
            
            return self._transform_eia_data(data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"EIA API request failed: {e}")
            return []
    
    def fetch_kenya_fuel_prices(self) -> List[Dict]:
        """Fetch Kenya-specific fuel prices (mock/placeholder)"""
        # Note: Replace with actual Kenya ERC API when available
        mock_data = [
            {
                'fuel_type': 'super_petrol',
                'price': 212.36,
                'region': 'Nairobi',
                'station': 'Shell Upper Hill',
                'latitude': -1.2921,
                'longitude': 36.8219,
                'recorded_at': datetime.now().isoformat()
            },
            {
                'fuel_type': 'diesel',
                'price': 201.47,
                'region': 'Nairobi',
                'station': 'Total Westlands',
                'latitude': -1.2659,
                'longitude': 36.8046,
                'recorded_at': datetime.now().isoformat()
            }
        ]
        
        logger.info(f"Generated {len(mock_data)} mock Kenya fuel prices")
        return mock_data
    
    def _transform_eia_data(self, raw_data: Dict) -> List[Dict]:
        """Transform EIA API response to our schema"""
        transformed = []
        
        for item in raw_data.get('response', {}).get('data', []):
            transformed.append({
                'fuel_type': item.get('product', '').lower().replace(' ', '_'),
                'price': float(item.get('value', 0)),
                'currency': 'USD',
                'region': item.get('area-name', 'Unknown'),
                'station_name': 'EIA Reported',
                'source': 'eia',
                'source_id': f"eia_{item.get('period')}_{item.get('product')}",
                'recorded_at': item.get('period'),
                'latitude': None,
                'longitude': None
            })
        
        return transformed
    
    def check_api_health(self) -> Dict:
        """Check health of all API endpoints"""
        health_status = {}
        
        # Check EIA API
        try:
            start_time = datetime.now()
            response = self.session.get(
                f"{settings.EIA_BASE_URL}/openapi",
                params={'api_key': settings.EIA_API_KEY},
                timeout=10
            )
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            health_status['eia'] = {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_time_ms': round(response_time, 2),
                'status_code': response.status_code
            }
        except Exception as e:
            health_status['eia'] = {
                'status': 'error',
                'error': str(e)
            }
        
        return health_status
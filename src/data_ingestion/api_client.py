import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

import requests

from config.settings import settings

logger = logging.getLogger(__name__)

DEFAULT_REQUEST_TIMEOUT_SECONDS = 30
HEALTH_REQUEST_TIMEOUT_SECONDS = 10
MAX_EIA_RECORDS = 5000


class EnergyAPIClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                'User-Agent': 'FuelPriceMonitor/1.0',
                'Accept': 'application/json',
            }
        )

    def fetch_eia_prices(self, fuel_type: str = "petroleum", days: int = 1) -> List[Dict[str, Any]]:
        """Fetch fuel prices from the EIA API."""
        try:
            now = datetime.now()
            response = self.session.get(
                f"{settings.EIA_BASE_URL}/petroleum/pri/gnd/data/",
                params=self._build_eia_query_params(fuel_type=fuel_type, days=days, now=now),
                timeout=DEFAULT_REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()

            payload = response.json()
            records = payload.get('response', {}).get('data', [])
            logger.info("Fetched %s records from EIA", len(records))

            return self._transform_eia_data(payload)
        except requests.exceptions.RequestException as exc:
            logger.error("EIA API request failed: %s", exc)
            return []

    def fetch_kenya_fuel_prices(self) -> List[Dict[str, Any]]:
        """Fetch Kenya-specific fuel prices (mock/placeholder)."""
        # Note: Replace with actual Kenya ERC API when available.
        timestamp = datetime.now().isoformat()
        mock_data = [
            {
                'fuel_type': 'super_petrol',
                'price': 212.36,
                'region': 'Nairobi',
                'station': 'Shell Upper Hill',
                'latitude': -1.2921,
                'longitude': 36.8219,
                'recorded_at': timestamp,
            },
            {
                'fuel_type': 'diesel',
                'price': 201.47,
                'region': 'Nairobi',
                'station': 'Total Westlands',
                'latitude': -1.2659,
                'longitude': 36.8046,
                'recorded_at': timestamp,
            },
        ]

        logger.info("Generated %s mock Kenya fuel prices", len(mock_data))
        return mock_data

    def _build_eia_query_params(self, fuel_type: str, days: int, now: datetime) -> Dict[str, Any]:
        return {
            'api_key': settings.EIA_API_KEY,
            'frequency': 'daily',
            'data': ['value'],
            'facets': {'product': [fuel_type]},
            'start': (now - timedelta(days=days)).strftime('%Y-%m-%d'),
            'end': now.strftime('%Y-%m-%d'),
            'sort': [{'column': 'period', 'direction': 'desc'}],
            'offset': 0,
            'length': MAX_EIA_RECORDS,
        }

    def _transform_eia_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform EIA API response to our internal schema."""
        transformed: List[Dict[str, Any]] = []

        for item in raw_data.get('response', {}).get('data', []):
            transformed.append(
                {
                    'fuel_type': item.get('product', '').lower().replace(' ', '_'),
                    'price': float(item.get('value', 0)),
                    'currency': 'USD',
                    'region': item.get('area-name', 'Unknown'),
                    'station_name': 'EIA Reported',
                    'source': 'eia',
                    'source_id': f"eia_{item.get('period')}_{item.get('product')}",
                    'recorded_at': item.get('period'),
                    'latitude': None,
                    'longitude': None,
                }
            )

        return transformed

    def check_api_health(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all API endpoints."""
        health_status: Dict[str, Dict[str, Any]] = {}

        try:
            start_time = datetime.now()
            response = self.session.get(
                f"{settings.EIA_BASE_URL}/openapi",
                params={'api_key': settings.EIA_API_KEY},
                timeout=HEALTH_REQUEST_TIMEOUT_SECONDS,
            )
            response_time = (datetime.now() - start_time).total_seconds() * 1000

            health_status['eia'] = {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_time_ms': round(response_time, 2),
                'status_code': response.status_code,
            }
        except requests.exceptions.RequestException as exc:
            health_status['eia'] = {
                'status': 'error',
                'error': str(exc),
            }

        return health_status

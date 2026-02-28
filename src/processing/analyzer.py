from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from sqlalchemy import func

from src.database.connection import db_manager
from src.database.models import FuelPrice


class DataAnalyzer:
    def calculate_daily_trends(self) -> List[Dict]:
        """Compute simple daily trend metrics per fuel type and region."""
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day)
        yesterday_start = today_start - timedelta(days=1)

        with db_manager.get_session() as session:
            today_rows = (
                session.query(
                    FuelPrice.fuel_type,
                    FuelPrice.region,
                    func.avg(FuelPrice.price).label('avg_price'),
                )
                .filter(FuelPrice.recorded_at >= today_start)
                .group_by(FuelPrice.fuel_type, FuelPrice.region)
                .all()
            )

            yesterday_rows = (
                session.query(
                    FuelPrice.fuel_type,
                    FuelPrice.region,
                    func.avg(FuelPrice.price).label('avg_price'),
                )
                .filter(FuelPrice.recorded_at >= yesterday_start, FuelPrice.recorded_at < today_start)
                .group_by(FuelPrice.fuel_type, FuelPrice.region)
                .all()
            )

        yesterday_map: Dict[Tuple[str, str], float] = {
            (row.fuel_type, row.region): float(row.avg_price or 0.0)
            for row in yesterday_rows
        }

        trends: List[Dict] = []
        for row in today_rows:
            current_price = float(row.avg_price or 0.0)
            key = (row.fuel_type, row.region)
            yesterday_price = yesterday_map.get(key, current_price)
            day_change = current_price - yesterday_price
            day_change_percent = (day_change / yesterday_price * 100.0) if yesterday_price else 0.0

            trends.append(
                {
                    'fuel_type': row.fuel_type,
                    'region': row.region,
                    'current_price': round(current_price, 4),
                    'yesterday_price': round(yesterday_price, 4),
                    'day_change': round(day_change, 4),
                    'day_change_percent': round(day_change_percent, 4),
                }
            )

        return trends

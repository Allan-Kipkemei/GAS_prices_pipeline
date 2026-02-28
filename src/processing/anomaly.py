from statistics import mean, pstdev
from typing import Dict, List, Tuple

from sqlalchemy import desc

from src.database.connection import db_manager
from src.database.models import FuelPrice


class AnomalyDetector:
    def detect_price_anomalies(self, z_threshold: float = 3.0, history_size: int = 30) -> List[Dict]:
        """Detect simple z-score based anomalies per fuel/region series."""
        with db_manager.get_session() as session:
            rows = (
                session.query(FuelPrice)
                .order_by(FuelPrice.recorded_at.desc())
                .limit(5000)
                .all()
            )

        grouped: Dict[Tuple[str, str], List[FuelPrice]] = {}
        for row in rows:
            key = (row.fuel_type or 'unknown', row.region or 'unknown')
            grouped.setdefault(key, []).append(row)

        anomalies: List[Dict] = []
        for (fuel_type, region), series in grouped.items():
            series = sorted(series, key=lambda r: r.recorded_at)
            prices = [float(r.price) for r in series if r.price is not None]
            if len(prices) < 5:
                continue

            baseline = prices[-history_size:]
            if len(baseline) < 2:
                continue

            avg = mean(baseline)
            sigma = pstdev(baseline)
            if sigma == 0:
                continue

            latest = prices[-1]
            z_score = (latest - avg) / sigma
            if abs(z_score) >= z_threshold:
                anomalies.append(
                    {
                        'fuel_type': fuel_type,
                        'region': region,
                        'latest_price': round(latest, 4),
                        'baseline_mean': round(avg, 4),
                        'z_score': round(z_score, 4),
                        'anomaly_type': 'spike' if z_score > 0 else 'drop',
                    }
                )

        return anomalies

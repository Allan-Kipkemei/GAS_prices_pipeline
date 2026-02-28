"""Compatibility module for accessing DAG definitions from src.processing."""

from typing import Any

try:
    from src.dags.fuel_price_dag import dag as fuel_price_monitoring_dag
except Exception:
    # Keep import-time failures isolated when Airflow/providers are unavailable.
    fuel_price_monitoring_dag = None


def get_dag() -> Any:
    """Return the Airflow DAG object when available, otherwise None."""
    return fuel_price_monitoring_dag


__all__ = ["fuel_price_monitoring_dag", "get_dag"]

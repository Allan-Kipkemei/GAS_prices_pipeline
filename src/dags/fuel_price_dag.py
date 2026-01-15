from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.data_ingestion.data_loader import DataLoader
from src.processing.analyzer import DataAnalyzer
from src.processing.anomaly import AnomalyDetector
from src.utils.notifications import send_alert_email

default_args = {
    'owner': 'fuel_price_team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def ingest_data_task(**context):
    """Task to ingest data from all sources"""
    loader = DataLoader()
    results = loader.ingest_all_sources()
    
    # Push results to XCom for other tasks
    context['ti'].xcom_push(key='ingestion_results', value=results)
    
    if results['total_ingested'] == 0:
        raise Exception("No data ingested from any source")
    
    return results

def validate_data_task(**context):
    """Task to validate ingested data"""
    ingestion_results = context['ti'].xcom_pull(key='ingestion_results', task_ids='ingest_data')
    
    # Check data quality
    hook = PostgresHook(postgres_conn_id='fuel_price_db')
    
    # Query for null prices
    null_prices = hook.get_records("""
        SELECT COUNT(*) FROM fuel_prices 
        WHERE price IS NULL 
        AND created_at >= NOW() - INTERVAL '1 hour'
    """)
    
    if null_prices[0][0] > 0:
        raise Exception(f"Found {null_prices[0][0]} records with null prices")
    
    return {"validated_records": ingestion_results['total_ingested']}

def analyze_trends_task(**context):
    """Task to calculate trends and statistics"""
    analyzer = DataAnalyzer()
    trends = analyzer.calculate_daily_trends()
    
    context['ti'].xcom_push(key='trends', value=trends)
    return trends

def detect_anomalies_task(**context):
    """Task to detect price anomalies"""
    detector = AnomalyDetector()
    anomalies = detector.detect_price_anomalies()
    
    if anomalies:
        context['ti'].xcom_push(key='anomalies_detected', value=True)
        context['ti'].xcom_push(key='anomalies', value=anomalies)
    
    return anomalies

def check_thresholds_task(**context):
    """Task to check for significant price changes"""
    trends = context['ti'].xcom_pull(key='trends', task_ids='analyze_trends')
    
    alerts = []
    for trend in trends:
        if abs(trend.get('day_change_percent', 0)) > 5.0:  # 5% threshold
            alerts.append({
                'fuel_type': trend['fuel_type'],
                'region': trend['region'],
                'change_percent': trend['day_change_percent'],
                'current_price': trend['current_price']
            })
    
    if alerts:
        context['ti'].xcom_push(key='price_alerts', value=alerts)
    
    return alerts

def generate_report_task(**context):
    """Task to generate daily report"""
    ingestion_results = context['ti'].xcom_pull(key='ingestion_results', task_ids='ingest_data')
    trends = context['ti'].xcom_pull(key='trends', task_ids='analyze_trends')
    
    report = f"""
    Daily Fuel Price Report - {datetime.now().strftime('%Y-%m-%d')}
    
    Summary:
    - Records ingested: {ingestion_results['total_ingested']}
    - Sources: {', '.join(ingestion_results['sources'].keys())}
    
    Top Trends:
    """
    
    for trend in trends[:5]:  # Top 5 trends
        report += f"\n- {trend['fuel_type']} in {trend['region']}: {trend['day_change_percent']:.2f}% change"
    
    context['ti'].xcom_push(key='daily_report', value=report)
    return report

with DAG(
    'fuel_price_monitoring',
    default_args=default_args,
    description='Daily fuel price monitoring pipeline',
    schedule_interval='0 6 * * *',  # Run daily at 6 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['fuel', 'energy', 'monitoring'],
) as dag:
    
    ingest_task = PythonOperator(
        task_id='ingest_data',
        python_callable=ingest_data_task,
    )
    
    validate_task = PythonOperator(
        task_id='validate_data',
        python_callable=validate_data_task,
    )
    
    analyze_task = PythonOperator(
        task_id='analyze_trends',
        python_callable=analyze_trends_task,
    )
    
    anomaly_task = PythonOperator(
        task_id='detect_anomalies',
        python_callable=detect_anomalies_task,
    )
    
    threshold_task = PythonOperator(
        task_id='check_thresholds',
        python_callable=check_thresholds_task,
    )
    
    report_task = PythonOperator(
        task_id='generate_report',
        python_callable=generate_report_task,
    )
    
    email_task = EmailOperator(
        task_id='send_daily_report',
        to='{{ var.value.alert_email }}',
        subject='Daily Fuel Price Report - {{ ds }}',
        html_content='{{ ti.xcom_pull(task_ids="generate_report") }}',
    )
    
    # Define task dependencies
    ingest_task >> validate_task >> analyze_task
    analyze_task >> [anomaly_task, threshold_task]
    [anomaly_task, threshold_task] >> report_task >> email_task
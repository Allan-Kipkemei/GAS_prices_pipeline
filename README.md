# EPRA Petrol Price Scraper - Automated Data Pipeline

## 📋 Overview
The **EPRA Petrol Price Scraper** is an automated data pipeline designed to scrape daily petrol prices from the Energy and Petroleum Regulatory Authority (EPRA), process the data, store it in a PostgreSQL database, and send email notifications. The pipeline is orchestrated using Apache Airflow for seamless automation and monitoring.

---

## 🎯 Features
- **Automated Daily Scraping**: Collects petrol price data daily at 9:00 AM UTC (12:00 PM EAT).
- **Data Processing**: Cleans and transforms the scraped data for consistency.
- **PostgreSQL Integration**: Stores structured data in a relational database.
- **Email Notifications**: Sends detailed reports after each pipeline run.
- **Error Handling**: Includes automatic retries and failure notifications.
- **Monitoring**: Comprehensive logging and task tracking via Airflow.

---

## 🏗️ Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   EPRA      │ ──▶ │   Airflow   │ ──▶ │ PostgreSQL  │ ──▶ │   Email     │
│   Website   │     │    DAG      │     │  Database   │     │ Notification│
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
     │                   │                   │                   │
     │ Web Scraping      │ Data Processing   │ Data Storage      │ Report Generation
     └───────────────────────────────────────────────────────────────────────────────
```

---

## 📁 Project Structure
```
fuel-price-monitor/
├── .env                                # Environment variables (ignored in Git)
├── .gitignore                          # Git ignore file
├── README.md                           # Project documentation
├── requirements.txt                    # Python dependencies
├── collect_data.py                     # Script for collecting data
├── connect-psql.py                     # Script for testing PostgreSQL connection
├── run_pipeline.py                     # Script to run the complete pipeline
├── test_current_connection.py          # Script to test database connection
├── test_eia_actual.py                  # Script to test EIA API integration
├── config/
│   ├── settings.py                     # Configuration settings for the project
├── docker/
│   ├── docker-compose.yml              # Docker Compose configuration
│   └── Dockerfile                      # Dockerfile for building the application image
├── docs/
│   └── API_KEYS.md                     # Documentation for API keys and usage
├── scripts/
│   ├── init_db.py                      # Script to initialize the database
│   └── sample_ingest.py                # Sample script for data ingestion
├── src/
│   ├── __init__.py                     # Package initialization
│   ├── main.py                         # Entry point for the FastAPI application
│   ├── dags/
│   │   ├── __init__.py                 # DAGs package initialization
│   │   └── fuel_price_dag.py           # Airflow DAG for the pipeline
│   ├── data_ingestion/
│   │   ├── __init__.py                 # Data ingestion package initialization
│   │   ├── api_client.py               # API client for fetching data
│   │   ├── kenya_scraper.py            # Kenya-specific scraper
│   │   ├── scheduler.py                # Scheduler for running scrapers
│   │   ├── epra_scraper.py             # EPRA scraper for Kenya data
│   │   └── complete_pipeline_real.py   # Complete pipeline implementation
│   ├── database/
│   │   ├── __init__.py                 # Database package initialization
│   │   ├── connection.py               # Database connection manager
│   │   └── models.py                   # Database models
│   ├── processing/
│   │   ├── __init__.py                 # Data processing package initialization
│   │   ├── analyzer.py                 # Analyzer for calculating trends
│   │   └── anomaly.py                  # Anomaly detection logic
│   └── utils/
│       ├── __init__.py                 # Utilities package initialization
│       └── notifications.py            # Utility for sending notifications
├── tests/
│   ├── __init__.py                     # Tests package initialization
│   ├── test_api_client.py              # Unit tests for the API client
│   └── test_validator.py               # Unit tests for data validation
└── venv/                               # Virtual environment
```

---

## 🔧 Installation & Setup

### 1. Prerequisites
- Python 3.1.8+
- PostgreSQL
- Apache Airflow 2.0+
- Docker (optional, for containerized deployment)

### 2. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/gregory-bot/Fuel-Energy-Price-Monitoring-pipeline.git
cd fuel-price-monitor

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Airflow Setup
```bash
# Initialize Airflow
export AIRFLOW_HOME=$(pwd)/airflow
airflow db init

# Create an admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# Configure SMTP for email notifications
# Update airflow.cfg with your SMTP settings
```

### 4. Database Setup
```sql
-- Create PostgreSQL database
CREATE DATABASE epra_prices;
CREATE USER epra_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE epra_prices TO epra_user;
```

### 5. Environment Variables Configuration
Create a `.env` file in the project root with the following variables. The app now resolves `.env` relative to the repository root, so it works even when launched from a different working directory:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=epra_prices
DB_USER=epra_user
DB_PASSWORD=your_password
DB_SSL_MODE=require
# Optional alternative: provide a full connection string instead of the values above
# DATABASE_URL=postgresql://epra_user:your_password@localhost:5432/epra_prices

# EIA API Configuration
EIA_API_KEY=your_eia_api_key

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
TIMEZONE=Africa/Nairobi
```

### 6. Initialize Database
```bash
python scripts/init_db.py
```

---

## 🚀 Usage

### Start Airflow Services
```bash
# Start the scheduler
airflow scheduler --daemon

# Start the webserver in another terminal
airflow webserver --daemon --port 8080

# Access the Airflow UI at http://localhost:8080
```

### Trigger the DAG Manually
```bash
# List available DAGs
airflow dags list

# Trigger the DAG
airflow dags trigger epra_daily_scraper

# Test the DAG
airflow dags test epra_daily_scraper 2026-01-10

# View logs
airflow tasks logs epra_daily_scraper scrape_task 2026-01-10
```

### Run Data Collection
```bash
# Collect data from all sources
python collect_data.py

# Run the complete pipeline
python run_pipeline.py
```

### Start FastAPI Server
```bash
# Run the FastAPI application
python src/main.py

# Access the API at http://localhost:8000
# View API documentation at http://localhost:8000/docs
```

---

## 📊 DAG Structure
The Airflow pipeline consists of the following tasks:

```
start_scraping
    │
    ├─▶ scrape_task (PythonOperator)
    │
    ├─▶ create_email_content (PythonOperator)
    │
    ├─▶ send_email_report (EmailOperator)
    │
    └─▶ end_scraping (DummyOperator)
```

### Task Details:
1. **start_scraping**: Marks the start of the pipeline.
2. **scrape_task**: Scrapes EPRA data from the website.
3. **create_email_content**: Generates email report content with statistics.
4. **send_email_report**: Sends the email notification to configured recipients.
5. **end_scraping**: Marks the end of the pipeline.

---

## 🔐 Environment Variables
Set the following environment variables for secure configuration:
```bash
export AIRFLOW_HOME=/path/to/airflow
export AIRFLOW__SMTP__SMTP_PASSWORD='your_app_password'
export DATABASE_URL='postgresql://user:pass@localhost/dbname'
export EIA_API_KEY='your_eia_api_key'
```

---

## 📊 API Endpoints

### Get All Fuel Prices
```
GET /api/prices
Query Parameters:
  - limit: number of records (default: 100)
  - offset: pagination offset (default: 0)
  - region: filter by region
  - fuel_type: filter by fuel type (Petrol, Diesel, etc.)
```

### Get Price Alerts
```
GET /api/alerts
Query Parameters:
  - limit: number of records (default: 100)
  - offset: pagination offset (default: 0)
```

### Create Price Alert
```
POST /api/alerts
Body:
{
  "fuel_price_id": 1,
  "alert_type": "price_spike",
  "threshold": 200.0,
  "actual_change": 15.5
}
```

---

## 📧 Email Report Sample
**EPRA Daily Scraping Report - 2026-01-10 09:05:00**

✅ **Scraping Successful!**

**Summary Statistics:**
- Total Records: 3,122
- Towns Covered: 223
- Average Price: KES 182.42
- Highest Price: KES 268.49
- Lowest Price: KES 171.39
- Date Range: 2026-01-01 to 2026-01-10

**Top 5 Most Expensive Towns:**
1. Nairobi - KES 268.49
2. Mombasa - KES 265.30
3. Kisumu - KES 262.15
4. Nakuru - KES 260.99
5. Eldoret - KES 258.50

---

## 🧪 Testing

### Run Unit Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_api_client.py

# Run with coverage
python -m pytest --cov=src tests/
```

### Test Database Connection
```bash
python test_current_connection.py
```

### Test EIA API Integration
```bash
python test_eia_actual.py
```

---

## 🐳 Docker Deployment

### Build Docker Image
```bash
docker build -t fuel-price-monitor:latest .
```

### Run with Docker Compose
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f
```

---

## 📈 Monitoring and Logging

The system uses Python's `logging` module for comprehensive logging. Logs are stored in:
- **Airflow Logs**: `$AIRFLOW_HOME/logs/`
- **Application Logs**: `logs/fuel-price-monitor.log`

View logs in real-time:
```bash
tail -f logs/fuel-price-monitor.log
```

---

## 🛠️ Next Steps
1. Improve the Kenya scraper to handle real EPRA website data.
2. Set up daily automatic collection using Airflow scheduler.
3. Add data analysis and visualization tools (Grafana, Tableau).
4. Deploy the pipeline to a production environment (AWS, Azure).
5. Implement caching strategies for improved performance.
6. Add real-time data streaming capabilities.

---

## 📚 Documentation

- [API Keys Setup Guide](docs/API_KEYS.md)
- [Database Schema Documentation](docs/DATABASE.md)
- [Airflow Configuration Guide](docs/AIRFLOW.md)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📞 Support
For issues, questions, or suggestions, please open an issue on the GitHub repository.

---

**Last Updated**: January 10, 2026

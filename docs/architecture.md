# CloudCostLens Architecture

CloudCostLens is designed as a cloud cost analytics platform.

## Planned Flow

Synthetic Billing Generator  

→ Raw CSV/JSON Files  

→ Snowflake Raw Tables  

→ dbt Staging Models  

→ dbt Cost Marts  

→ Cost Anomaly Detection  

→ Streamlit Dashboard  

→ Airflow Orchestration  

## Main Components

### 1. Billing Data Generator

Creates realistic cloud billing records including service, project, environment, usage quantity, unit cost, tags, and daily cost.

### 2. Snowflake Raw Layer

Stores raw billing-style records before transformation.

### 3. dbt Transformation Layer

Builds staging models and analytics marts for service spend, project spend, budget tracking, and cost anomalies.

### 4. Airflow Orchestration

Schedules ingestion, loading, transformation, testing, and reporting tasks.

### 5. Dashboard

Visualizes total spend, top cost drivers, daily spend, budget usage, and anomaly alerts.
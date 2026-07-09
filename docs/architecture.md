# CloudCostLens Architecture

CloudCostLens is a cloud cost analytics platform built as a local-first data engineering portfolio project.

## Current Flow

```text
Synthetic Billing Generator
→ CSV Validation
→ DuckDB Raw Warehouse
→ dbt Staging Models
→ dbt Cost Marts
→ Cost Anomaly Detection
→ Markdown Cost Report
→ Streamlit Dashboard
→ GitHub Actions CI
→ Optional Airflow DAG
```

The default workflow runs locally with DuckDB. Snowflake setup SQL is included in `snowflake/` as an optional future warehouse path, but the current project does not require Snowflake credentials.

## Main Components

### 1. Billing Data Generator

Creates realistic cloud billing records with service, project, environment, usage quantity, unit cost, tags, and daily cost.

### 2. CSV Validation

Validates required columns, value ranges, and data quality rules before loading analytics tables.

### 3. DuckDB Raw Warehouse

Stores raw billing records in `data/cloudcostlens.duckdb` for local development and analytics.

### 4. dbt Transformation Layer

Builds staging models and cost marts for daily spend, service spend, budget tracking, and anomaly detection.

### 5. Cost Anomaly Detection

Uses rolling 14-day statistics in `mart_cost_anomalies` to flag unusual daily service/project spend.

### 6. Markdown Cost Report

Generates a portfolio-friendly summary report in `reports/cloud_cost_summary.md`.

### 7. Streamlit Dashboard

Visualizes total spend, top cost drivers, daily spend, budget usage, and anomaly alerts.

### 8. GitHub Actions CI

Runs the core local pipeline on push and pull request to `main`.

### 9. Optional Airflow DAG

`cloudcostlens_daily_pipeline` can orchestrate ingestion, dbt, and report generation on a daily schedule. Airflow is optional and separate from the default `python main.py` workflow.

## Default Local Workflow

```bash
python main.py
streamlit run dashboard/app.py
```

## Optional Paths

- **Snowflake:** warehouse setup SQL for a future cloud deployment
- **Airflow:** optional orchestration via `requirements-airflow.txt`

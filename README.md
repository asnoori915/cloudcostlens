# CloudCostLens

CloudCostLens is a data engineering and analytics engineering portfolio project for cloud cost observability.

It generates realistic multi-cloud billing data, validates and loads it into a local analytics warehouse, transforms usage records with dbt, and visualizes spend trends, budget status, and cost anomalies in a Streamlit dashboard.

## Why I Built This

Cloud costs are a major operational concern for modern data and software teams. I built CloudCostLens to practice end-to-end analytics engineering: synthetic data generation, warehouse loading, dbt modeling, data quality testing, and business-facing cost monitoring.

## Current Capabilities

The project currently supports:

- Realistic cloud billing data generation
- Local CSV validation
- DuckDB local analytics warehouse
- dbt staging and mart models
- dbt tests
- Streamlit cost dashboard

## Example Dataset

The default generator produces a portfolio-ready sample dataset with:

- **22,500 billing records**
- A **90-day billing window**
- About **$785K** in simulated cloud spend
- Top cost drivers that include **ML services** (SageMaker, Vertex AI, Azure ML) and **storage services** (S3, Cloud Storage)

The data includes realistic variation such as higher weekday compute spend, slowly increasing storage costs, occasional ML training spikes, lower dev environment spend, and partially untagged resources.

## Tech Stack

**Current local stack**

- Python
- DuckDB
- dbt (dbt-duckdb)
- Streamlit
- Plotly
- SQL

**Optional future warehouse path**

Snowflake SQL setup is included in `snowflake/01_create_database_objects.sql` as an optional path for moving from local development to a cloud warehouse. The default project runs locally with DuckDB and does not require a Snowflake connection.

## Quick Start

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the end-to-end workflow:

```bash
python -m ingestion.main
python -m analytics.run_dbt --all
streamlit run dashboard/app.py
```

### What each command does

- `python -m ingestion.main` — generates billing data, validates the CSV, and loads it into DuckDB
- `python -m analytics.run_dbt --all` — runs dbt models and tests
- `streamlit run dashboard/app.py` — launches the cost observability dashboard

## Project Structure

```text
ingestion/          Billing data generation, validation, and DuckDB loading
dbt_cloudcostlens/  dbt staging and mart models
dashboard/          Streamlit dashboard
data/               Local CSV and DuckDB warehouse
snowflake/          Optional Snowflake warehouse setup SQL
docs/               Architecture notes
```

## dbt Models

**Staging**

- `stg_cloud_usage`
- `stg_projects`
- `stg_services`

**Marts**

- `fact_daily_cloud_cost`
- `mart_service_spend`
- `mart_budget_tracking`
- `mart_cost_anomalies`

## Future Enhancements

- Snowflake loading and dbt target switch
- Airflow orchestration
- GitHub Actions CI

## Project Status

Core local pipeline is working: data generation, validation, DuckDB loading, dbt transformations, tests, and dashboard visualization.

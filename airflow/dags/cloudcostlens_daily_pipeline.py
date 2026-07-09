"""Optional daily Airflow DAG for the CloudCostLens local analytics workflow.

This DAG orchestrates the existing local pipeline without Snowflake:
1. Generate, validate, and load billing data into DuckDB
2. Run dbt models and tests
3. Generate the Markdown cost summary report

Set CLOUDCOSTLENS_HOME to override the inferred project root path.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

DEFAULT_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def build_project_command(python_command: str) -> str:
    """Build a bash command that runs Python from the project root."""
    return (
        'PROJECT_ROOT="${CLOUDCOSTLENS_HOME:-'
        f"{DEFAULT_PROJECT_ROOT}"
        '}" && '
        'cd "$PROJECT_ROOT" && '
        f"{python_command}"
    )


with DAG(
    dag_id="cloudcostlens_daily_pipeline",
    description="Run the local CloudCostLens ingestion, dbt, and reporting workflow.",
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["cloudcostlens", "local", "duckdb"],
) as dag:
    generate_and_load_billing_data = BashOperator(
        task_id="generate_and_load_billing_data",
        bash_command=build_project_command("python -m ingestion.main"),
    )

    run_dbt_models_and_tests = BashOperator(
        task_id="run_dbt_models_and_tests",
        bash_command=build_project_command("python -m analytics.run_dbt --all"),
    )

    generate_cost_report = BashOperator(
        task_id="generate_cost_report",
        bash_command=build_project_command("python -m reporting.generate_cost_report"),
    )

    generate_and_load_billing_data >> run_dbt_models_and_tests >> generate_cost_report

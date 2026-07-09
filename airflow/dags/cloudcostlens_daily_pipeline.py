"""Optional daily Airflow DAG for the CloudCostLens local analytics workflow.

This DAG orchestrates the existing local pipeline without Snowflake:
1. Generate, validate, and load billing data into DuckDB
2. Run dbt models and tests
3. Generate the Markdown cost summary report

Tasks run with the project's normal virtual environment at PROJECT_ROOT/.venv,
not the Airflow virtual environment.

Set CLOUDCOSTLENS_HOME to override the inferred project root path.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

DEFAULT_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def build_project_command(module_args: str) -> str:
    """Build a bash command that runs the project virtualenv Python."""
    return f"""
PROJECT_ROOT="${{CLOUDCOSTLENS_HOME:-{DEFAULT_PROJECT_ROOT}}}"
PROJECT_PYTHON="$PROJECT_ROOT/.venv/bin/python"
test -x "$PROJECT_PYTHON" || {{
  echo "Project virtualenv not found: $PROJECT_PYTHON"
  exit 1
}}
cd "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT"
"$PROJECT_PYTHON" {module_args}
""".strip()


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
        bash_command=build_project_command("-m ingestion.main"),
    )

    run_dbt_models_and_tests = BashOperator(
        task_id="run_dbt_models_and_tests",
        bash_command=build_project_command("-m analytics.run_dbt --all"),
    )

    generate_cost_report = BashOperator(
        task_id="generate_cost_report",
        bash_command=build_project_command("-m reporting.generate_cost_report"),
    )

    generate_and_load_billing_data >> run_dbt_models_and_tests >> generate_cost_report

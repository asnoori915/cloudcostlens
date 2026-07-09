"""Run dbt models and tests for CloudCostLens."""

import argparse
import subprocess
import sys
from pathlib import Path

DBT_PROJECT_DIR = Path(__file__).resolve().parent.parent / "dbt_cloudcostlens"
DBT_EXECUTABLE = Path(sys.executable).parent / "dbt"


def run_dbt_command(command: str) -> None:
    """Run a dbt command from the project directory."""
    result = subprocess.run(
        [str(DBT_EXECUTABLE), command, "--profiles-dir", "."],
        cwd=DBT_PROJECT_DIR,
        check=False,
    )
    if result.returncode != 0:
        print(f"dbt {command} failed with exit code {result.returncode}.")
        sys.exit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run dbt models and tests for CloudCostLens.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run", action="store_true", help="Run dbt models.")
    group.add_argument("--test", action="store_true", help="Run dbt tests.")
    group.add_argument("--all", action="store_true", help="Run dbt models, then dbt tests.")
    args = parser.parse_args()

    if args.run:
        print("Running dbt models...", flush=True)
        run_dbt_command("run")
        print("dbt run complete.")
    elif args.test:
        print("Running dbt tests...", flush=True)
        run_dbt_command("test")
        print("dbt test complete.")
    else:
        print("Step 1/2: Running dbt models...", flush=True)
        run_dbt_command("run")
        print()
        print("Step 2/2: Running dbt tests...", flush=True)
        run_dbt_command("test")
        print()
        print("dbt workflow complete.")


if __name__ == "__main__":
    main()

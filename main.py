"""Run the CloudCostLens local workflow end to end."""

import subprocess
import sys


def run_step(command: list[str], failure_message: str) -> None:
    """Run a workflow command and stop if it fails."""
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        print(failure_message)
        sys.exit(result.returncode)


def main() -> None:
    print("Step 1/3: Running ingestion workflow...", flush=True)
    run_step(
        [sys.executable, "-m", "ingestion.main"],
        "Workflow stopped: ingestion failed.",
    )
    print()

    print("Step 2/3: Running dbt analytics workflow...", flush=True)
    run_step(
        [sys.executable, "-m", "analytics.run_dbt", "--all"],
        "Workflow stopped: dbt workflow failed.",
    )
    print()

    print("Step 3/3: Generating cost report...", flush=True)
    run_step(
        [sys.executable, "-m", "reporting.generate_cost_report"],
        "Workflow stopped: report generation failed.",
    )
    print()
    print("CloudCostLens workflow complete.")


if __name__ == "__main__":
    main()

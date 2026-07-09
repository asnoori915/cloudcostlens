"""Run the CloudCostLens ingestion workflow end to end."""

import sys

from .generate_billing_data import OUTPUT_PATH, generate_records, print_summary as print_generation_summary
from .load_to_duckdb import DB_PATH, TABLE_NAME, load_billing_data, print_summary as print_load_summary
from .validate_billing_data import print_summary as print_validation_summary, run_checks


def main() -> None:
    print("Step 1/3: Generating billing data...")
    df = generate_records()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved billing data to {OUTPUT_PATH}")
    print_generation_summary(df)
    print()

    print("Step 2/3: Validating billing data...")
    results = run_checks()
    if not print_validation_summary(results):
        print("Workflow stopped: validation failed.")
        sys.exit(1)
    print()

    print("Step 3/3: Loading billing data into DuckDB...")
    df = load_billing_data()
    print(f"Loaded data into {DB_PATH} ({TABLE_NAME})")
    print_load_summary(df)
    print()
    print("Ingestion workflow complete.")


if __name__ == "__main__":
    main()

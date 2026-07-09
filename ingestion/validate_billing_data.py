"""Validate raw cloud billing CSV data before loading into DuckDB."""

import sys
from pathlib import Path

import pandas as pd

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "cloud_billing.csv"

REQUIRED_COLUMNS = [
    "billing_date",
    "provider",
    "service",
    "project",
    "team",
    "environment",
    "region",
    "resource_id",
    "usage_quantity",
    "usage_unit",
    "unit_cost",
    "total_cost",
    "currency",
    "tag_owner",
    "tag_cost_center",
    "is_tagged",
]

ALLOWED_ENVIRONMENTS = {"dev", "staging", "prod"}
ALLOWED_CURRENCIES = {"USD"}


def run_checks() -> list[tuple[str, bool, str]]:
    """Run all validation checks and return (name, passed, detail) tuples."""
    results: list[tuple[str, bool, str]] = []

    if not CSV_PATH.exists():
        results.append(("File exists", False, f"Missing file: {CSV_PATH}"))
        return results

    results.append(("File exists", True, f"Found {CSV_PATH}"))

    df = pd.read_csv(CSV_PATH)

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        results.append(
            (
                "Required columns exist",
                False,
                f"Missing columns: {', '.join(missing_columns)}",
            )
        )
    else:
        results.append(
            ("Required columns exist", True, f"All {len(REQUIRED_COLUMNS)} columns present")
        )

    row_count = len(df)
    if row_count > 0:
        results.append(("Row count > 0", True, f"{row_count:,} rows found"))
    else:
        results.append(("Row count > 0", False, "CSV has no data rows"))

    negative_cost_count = (df["total_cost"] < 0).sum()
    if negative_cost_count == 0:
        results.append(("total_cost is non-negative", True, "No negative values"))
    else:
        results.append(
            (
                "total_cost is non-negative",
                False,
                f"{negative_cost_count:,} negative values found",
            )
        )

    negative_usage_count = (df["usage_quantity"] < 0).sum()
    if negative_usage_count == 0:
        results.append(("usage_quantity is non-negative", True, "No negative values"))
    else:
        results.append(
            (
                "usage_quantity is non-negative",
                False,
                f"{negative_usage_count:,} negative values found",
            )
        )

    billing_date_nulls = df["billing_date"].isna().sum()
    if billing_date_nulls == 0:
        results.append(("billing_date has no nulls", True, "No null values"))
    else:
        results.append(
            (
                "billing_date has no nulls",
                False,
                f"{billing_date_nulls:,} null values found",
            )
        )

    service_nulls = df["service"].isna().sum()
    if service_nulls == 0:
        results.append(("service has no nulls", True, "No null values"))
    else:
        results.append(
            ("service has no nulls", False, f"{service_nulls:,} null values found")
        )

    project_nulls = df["project"].isna().sum()
    if project_nulls == 0:
        results.append(("project has no nulls", True, "No null values"))
    else:
        results.append(
            ("project has no nulls", False, f"{project_nulls:,} null values found")
        )

    invalid_environments = set(df["environment"].dropna().unique()) - ALLOWED_ENVIRONMENTS
    if not invalid_environments:
        results.append(
            (
                "environment values are valid",
                True,
                "Only dev, staging, and prod found",
            )
        )
    else:
        results.append(
            (
                "environment values are valid",
                False,
                f"Invalid values: {', '.join(sorted(invalid_environments))}",
            )
        )

    invalid_currencies = set(df["currency"].dropna().unique()) - ALLOWED_CURRENCIES
    if not invalid_currencies:
        results.append(("currency values are valid", True, "Only USD found"))
    else:
        results.append(
            (
                "currency values are valid",
                False,
                f"Invalid values: {', '.join(sorted(invalid_currencies))}",
            )
        )

    return results


def print_summary(results: list[tuple[str, bool, str]]) -> bool:
    """Print PASS/FAIL lines and return True only if all checks passed."""
    print(f"Validating {CSV_PATH}\n")

    all_passed = True
    for name, passed, detail in results:
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}: {detail}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("Overall result: PASS")
    else:
        print("Overall result: FAIL")

    return all_passed


def main() -> None:
    results = run_checks()
    all_passed = print_summary(results)
    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()

"""Load raw cloud billing CSV data into a local DuckDB database."""

from pathlib import Path

import duckdb
import pandas as pd

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "cloud_billing.csv"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "cloudcostlens.duckdb"
TABLE_NAME = "raw_cloud_billing"


def load_billing_data() -> pd.DataFrame:
    """Read the billing CSV and load it into DuckDB."""
    df = pd.read_csv(CSV_PATH)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(DB_PATH))
    try:
        con.register("billing_df", df)
        con.execute(
            f"CREATE OR REPLACE TABLE {TABLE_NAME} AS SELECT * FROM billing_df"
        )
    finally:
        con.close()

    return df


def print_summary(df: pd.DataFrame) -> None:
    """Print a short summary of the loaded billing data."""
    top_services = (
        df.groupby("service")["total_cost"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )

    print(f"Rows loaded: {len(df):,}")
    print(f"Total cost loaded: ${df['total_cost'].sum():,.2f}")
    print(f"Min billing_date: {df['billing_date'].min()}")
    print(f"Max billing_date: {df['billing_date'].max()}")
    print("Top 5 services by total cost:")
    for service, cost in top_services.items():
        print(f"  - {service}: ${cost:,.2f}")


def main() -> None:
    df = load_billing_data()
    print(f"Loaded data into {DB_PATH} ({TABLE_NAME})")
    print_summary(df)


if __name__ == "__main__":
    main()

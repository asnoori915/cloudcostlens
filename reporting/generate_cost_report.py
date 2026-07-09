"""Generate a Markdown cloud cost summary report from DuckDB analytics tables."""

from datetime import datetime
from pathlib import Path

import duckdb
import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "cloudcostlens.duckdb"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "reports" / "cloud_cost_summary.md"


def format_currency(value: float) -> str:
    """Format a number as USD currency."""
    return f"${value:,.2f}"


def format_date(value) -> str:
    """Format a date value as YYYY-MM-DD."""
    if pd.isna(value):
        return "N/A"
    return pd.to_datetime(value).strftime("%Y-%m-%d")


def dataframe_to_markdown_table(df: pd.DataFrame) -> str:
    """Convert a dataframe to a simple Markdown table."""
    if df.empty:
        return "_No data available._"

    headers = "| " + " | ".join(df.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(df.columns)) + " |"
    rows = [
        "| " + " | ".join(str(value) for value in row) + " |"
        for row in df.itertuples(index=False, name=None)
    ]
    return "\n".join([headers, separator, *rows])


def load_report_data() -> dict:
    """Load summary metrics and tables from DuckDB."""
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        summary = con.execute(
            """
            select
                round(sum(total_cost), 2) as total_spend,
                sum(usage_records) as total_records,
                min(billing_date) as min_date,
                max(billing_date) as max_date
            from fact_daily_cloud_cost
            """
        ).fetchone()

        anomaly_count = con.execute(
            """
            select count(*) as anomaly_count
            from mart_cost_anomalies
            where is_anomaly = true
            """
        ).fetchone()[0]

        top_services = con.execute(
            """
            select service, provider, total_cost
            from mart_service_spend
            order by total_cost desc
            limit 5
            """
        ).fetchdf()

        top_projects = con.execute(
            """
            select
                project,
                round(sum(total_cost), 2) as total_cost
            from fact_daily_cloud_cost
            group by project
            order by total_cost desc
            limit 5
            """
        ).fetchdf()

        budget_summary = con.execute(
            """
            select
                budget_status,
                count(*) as project_count
            from mart_budget_tracking
            group by budget_status
            order by project_count desc
            """
        ).fetchdf()

        top_anomalies = con.execute(
            """
            select
                billing_date,
                service,
                project,
                daily_cost,
                anomaly_amount,
                anomaly_pct,
                anomaly_severity
            from mart_cost_anomalies
            where is_anomaly = true
            order by anomaly_amount desc
            limit 10
            """
        ).fetchdf()
    finally:
        con.close()

    return {
        "summary": summary,
        "anomaly_count": anomaly_count,
        "top_services": top_services,
        "top_projects": top_projects,
        "budget_summary": budget_summary,
        "top_anomalies": top_anomalies,
    }


def build_interpretation(data: dict) -> str:
    """Write a short interpretation of the report results."""
    total_spend, _, min_date, max_date = data["summary"]
    anomaly_count = data["anomaly_count"]
    top_service = data["top_services"].iloc[0]["service"] if not data["top_services"].empty else "N/A"
    top_project = data["top_projects"].iloc[0]["project"] if not data["top_projects"].empty else "N/A"
    over_budget_count = 0
    if not data["budget_summary"].empty:
        over_budget = data["budget_summary"][
            data["budget_summary"]["budget_status"] == "OVER_BUDGET"
        ]
        if not over_budget.empty:
            over_budget_count = int(over_budget.iloc[0]["project_count"])

    return (
        f"Over the reporting window from {format_date(min_date)} to {format_date(max_date)}, "
        f"CloudCostLens recorded {format_currency(total_spend)} in simulated cloud spend. "
        f"The largest cost drivers are concentrated in **{top_service}** services and the "
        f"**{top_project}** project. "
        f"{anomaly_count:,} cost anomalies were detected using rolling 14-day statistics, "
        f"suggesting occasional spikes in daily service spend. "
        f"Budget tracking shows {over_budget_count} project(s) currently marked as OVER_BUDGET, "
        f"which indicates spend has exceeded the configured project budget thresholds."
    )


def build_report(data: dict) -> str:
    """Build the Markdown report content."""
    total_spend, total_records, min_date, max_date = data["summary"]
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    top_services = data["top_services"].copy()
    if not top_services.empty:
        top_services["total_cost"] = top_services["total_cost"].map(format_currency)

    top_projects = data["top_projects"].copy()
    if not top_projects.empty:
        top_projects["total_cost"] = top_projects["total_cost"].map(format_currency)

    top_anomalies = data["top_anomalies"].copy()
    if not top_anomalies.empty:
        top_anomalies["billing_date"] = top_anomalies["billing_date"].map(format_date)
        top_anomalies["daily_cost"] = top_anomalies["daily_cost"].map(format_currency)
        top_anomalies["anomaly_amount"] = top_anomalies["anomaly_amount"].map(format_currency)
        top_anomalies["anomaly_pct"] = top_anomalies["anomaly_pct"].map(lambda v: f"{v:.2f}%")

    sections = [
        "# CloudCostLens Cost Summary Report",
        "",
        f"_Generated: {generated_at}_",
        "",
        "## Executive Summary",
        "",
        f"- **Total Spend:** {format_currency(total_spend)}",
        f"- **Total Records:** {int(total_records):,}",
        f"- **Date Range:** {format_date(min_date)} → {format_date(max_date)}",
        f"- **Number of Anomalies:** {int(data['anomaly_count']):,}",
        "",
        "## Top 5 Services by Spend",
        "",
        dataframe_to_markdown_table(top_services),
        "",
        "## Top 5 Projects by Spend",
        "",
        dataframe_to_markdown_table(top_projects),
        "",
        "## Budget Status Summary",
        "",
        dataframe_to_markdown_table(data["budget_summary"]),
        "",
        "## Top 10 Cost Anomalies",
        "",
        dataframe_to_markdown_table(top_anomalies),
        "",
        "## Interpretation",
        "",
        build_interpretation(data),
        "",
    ]
    return "\n".join(sections)


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"DuckDB file not found: {DB_PATH}")

    data = load_report_data()
    report = build_report(data)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(report, encoding="utf-8")

    print(f"Report saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

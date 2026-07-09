"""CloudCostLens Streamlit dashboard."""

from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "cloudcostlens.duckdb"

TABLES = [
    "raw_cloud_billing",
    "fact_daily_cloud_cost",
    "mart_service_spend",
    "mart_budget_tracking",
    "mart_cost_anomalies",
]


@st.cache_data
def load_tables() -> dict[str, pd.DataFrame]:
    """Load dashboard tables from DuckDB."""
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        return {
            table_name: con.execute(f"select * from {table_name}").fetchdf()
            for table_name in TABLES
        }
    finally:
        con.close()


def apply_filters(
    df: pd.DataFrame,
    providers: list[str],
    environments: list[str],
    projects: list[str],
) -> pd.DataFrame:
    """Filter a dataframe by provider, environment, and project."""
    filtered = df.copy()

    if providers:
        filtered = filtered[filtered["provider"].isin(providers)]
    if environments:
        filtered = filtered[filtered["environment"].isin(environments)]
    if projects:
        filtered = filtered[filtered["project"].isin(projects)]

    return filtered


def format_currency(value: float) -> str:
    """Format a number as USD currency."""
    return f"${value:,.2f}"


def format_date(value) -> str:
    """Format a date value as YYYY-MM-DD."""
    if pd.isna(value):
        return ""
    return pd.to_datetime(value).strftime("%Y-%m-%d")


def format_date_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Return a copy of a dataframe with selected date columns formatted."""
    display_df = df.copy()
    for column in columns:
        if column in display_df.columns:
            display_df[column] = pd.to_datetime(display_df[column]).dt.strftime("%Y-%m-%d")
    return display_df


def main() -> None:
    st.set_page_config(
        page_title="CloudCostLens",
        page_icon="☁️",
        layout="wide",
    )

    st.title("CloudCostLens")
    st.caption("Cloud Cost Observability Dashboard")

    if not DB_PATH.exists():
        st.error(f"DuckDB file not found: {DB_PATH}")
        st.info("Run `python -m ingestion.main` and `python -m analytics.run_dbt --all` first.")
        return

    tables = load_tables()
    raw_df = tables["raw_cloud_billing"]
    fact_df = tables["fact_daily_cloud_cost"]
    service_df = tables["mart_service_spend"]
    budget_df = tables["mart_budget_tracking"]
    anomalies_df = tables["mart_cost_anomalies"]

    st.sidebar.header("Filters")
    provider_options = sorted(fact_df["provider"].dropna().unique())
    environment_options = sorted(fact_df["environment"].dropna().unique())
    project_options = sorted(fact_df["project"].dropna().unique())

    selected_providers = st.sidebar.multiselect(
        "Provider",
        provider_options,
        default=provider_options,
    )
    selected_environments = st.sidebar.multiselect(
        "Environment",
        environment_options,
        default=environment_options,
    )
    selected_projects = st.sidebar.multiselect(
        "Project",
        project_options,
        default=project_options,
    )

    filtered_fact = apply_filters(
        fact_df,
        selected_providers,
        selected_environments,
        selected_projects,
    )
    filtered_raw = apply_filters(
        raw_df,
        selected_providers,
        selected_environments,
        selected_projects,
    )
    filtered_budget = budget_df.copy()
    if selected_environments:
        filtered_budget = filtered_budget[
            filtered_budget["environment"].isin(selected_environments)
        ]
    if selected_projects:
        filtered_budget = filtered_budget[filtered_budget["project"].isin(selected_projects)]

    visible_projects = filtered_fact["project"].dropna().unique()
    filtered_anomalies = anomalies_df[
        (anomalies_df["is_anomaly"] == True)  # noqa: E712
        & (anomalies_df["project"].isin(visible_projects))
    ]

    min_date = filtered_fact["billing_date"].min()
    max_date = filtered_fact["billing_date"].max()
    date_range = (
        f"{format_date(min_date)} → {format_date(max_date)}"
        if pd.notna(min_date) and pd.notna(max_date)
        else "No data"
    )

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    metric_col1.metric("Total Spend", format_currency(filtered_fact["total_cost"].sum()))
    metric_col2.metric("Total Records", f"{int(filtered_fact['usage_records'].sum()):,}")
    metric_col3.metric("Date Range", date_range)
    metric_col4.metric("Cost Anomalies", f"{len(filtered_anomalies):,}")

    st.markdown("---")

    chart_col1, chart_col2 = st.columns(2)

    daily_spend = (
        filtered_fact.groupby("billing_date", as_index=False)["total_cost"]
        .sum()
        .sort_values("billing_date")
    )
    service_spend = service_df.copy()
    if selected_providers:
        service_spend = service_spend[service_spend["provider"].isin(selected_providers)]
    service_spend = service_spend.sort_values("total_cost", ascending=False).head(10)
    project_spend = (
        filtered_fact.groupby("project", as_index=False)["total_cost"]
        .sum()
        .sort_values("total_cost", ascending=False)
    )

    with chart_col1:
        st.subheader("Daily Spend Trend")
        if daily_spend.empty:
            st.info("No data available for the selected filters.")
        else:
            fig = px.line(
                daily_spend,
                x="billing_date",
                y="total_cost",
                markers=True,
                labels={"billing_date": "Billing Date", "total_cost": "Total Cost (USD)"},
                template="plotly_white",
            )
            fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, width="stretch")

    with chart_col2:
        st.subheader("Top Services by Total Cost")
        if service_spend.empty:
            st.info("No data available for the selected filters.")
        else:
            fig = px.bar(
                service_spend,
                x="total_cost",
                y="service",
                orientation="h",
                labels={"total_cost": "Total Cost (USD)", "service": "Service"},
                template="plotly_white",
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, width="stretch")

    st.subheader("Spend by Project")
    if project_spend.empty:
        st.info("No data available for the selected filters.")
    else:
        fig = px.bar(
            project_spend,
            x="project",
            y="total_cost",
            labels={"project": "Project", "total_cost": "Total Cost (USD)"},
            template="plotly_white",
        )
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, width="stretch")

    table_col1, table_col2 = st.columns(2)

    with table_col1:
        st.subheader("Budget Tracking")
        budget_display = filtered_budget[
            [
                "project",
                "team",
                "environment",
                "total_cost",
                "budget_amount",
                "budget_used_pct",
                "budget_status",
            ]
        ].sort_values("budget_used_pct", ascending=False)
        st.dataframe(budget_display, width="stretch", hide_index=True)

    with table_col2:
        st.subheader("Cost Anomalies")
        anomaly_display = filtered_anomalies[
            [
                "billing_date",
                "service",
                "project",
                "daily_cost",
                "avg_previous_14_days",
                "stddev_previous_14_days",
            ]
        ].sort_values(["billing_date", "daily_cost"], ascending=[False, False])
        anomaly_display = format_date_columns(anomaly_display, ["billing_date"])
        st.dataframe(anomaly_display, width="stretch", hide_index=True)

    st.subheader("Raw Billing Sample")
    raw_sample = filtered_raw.sort_values("billing_date", ascending=False).head(100)
    raw_sample = format_date_columns(raw_sample, ["billing_date"])
    st.dataframe(raw_sample, width="stretch", hide_index=True)


if __name__ == "__main__":
    main()

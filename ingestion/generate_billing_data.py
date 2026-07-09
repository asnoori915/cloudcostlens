"""Generate realistic synthetic cloud billing data for CloudCostLens."""

import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

PROVIDERS = ["AWS", "GCP", "Azure"]

COMPUTE_SERVICES = ["EC2", "GCE", "Virtual Machines", "Lambda", "Cloud Functions"]
STORAGE_SERVICES = ["S3", "GCS", "Blob Storage", "EBS", "Cloud Storage"]
ML_SERVICES = ["SageMaker", "Vertex AI", "Azure ML"]
OTHER_SERVICES = ["RDS", "BigQuery", "Cloud SQL", "VPC", "Load Balancer", "CloudWatch"]

ALL_SERVICES = COMPUTE_SERVICES + STORAGE_SERVICES + ML_SERVICES + OTHER_SERVICES
SERVICE_WEIGHTS = (
    [8] * len(COMPUTE_SERVICES)
    + [6] * len(STORAGE_SERVICES)
    + [3] * len(ML_SERVICES)
    + [5] * len(OTHER_SERVICES)
)

PROJECTS = [
    "data-platform",
    "customer-api",
    "analytics-hub",
    "ml-pipeline",
    "web-app",
    "mobile-backend",
]
TEAMS = ["platform", "data-engineering", "machine-learning", "frontend", "backend", "devops"]
ENVIRONMENTS = ["prod", "staging", "dev"]
ENV_COST_MULTIPLIER = {"prod": 1.0, "staging": 0.7, "dev": 0.4}

REGIONS = {
    "AWS": ["us-east-1", "us-west-2", "eu-west-1"],
    "GCP": ["us-central1", "us-east1", "europe-west1"],
    "Azure": ["eastus", "westus2", "westeurope"],
}

COST_CENTERS = ["CC-1001", "CC-2000", "CC-3100", "CC-4200", "CC-5500"]

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "cloud_billing.csv"


def _service_category(service: str) -> str:
    if service in COMPUTE_SERVICES:
        return "compute"
    if service in STORAGE_SERVICES:
        return "storage"
    if service in ML_SERVICES:
        return "ml"
    return "other"


def _base_usage_and_cost(service: str) -> tuple[float, float, str]:
    category = _service_category(service)
    if category == "compute":
        return random.uniform(1, 24), random.uniform(0.05, 0.50), "hours"
    if category == "storage":
        return random.uniform(50, 2000), random.uniform(0.02, 0.08), "GB-months"
    if category == "ml":
        return random.uniform(2, 48), random.uniform(1.0, 8.0), "hours"
    return random.uniform(1, 100), random.uniform(0.10, 2.0), "units"


def generate_records(
    num_days: int = 90,
    records_per_day: int = 250,
    end_date: datetime | None = None,
) -> pd.DataFrame:
    """Build daily billing records with realistic cost variation."""
    if end_date is None:
        end_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    start_date = end_date - timedelta(days=num_days - 1)
    records = []

    for day_index in range(num_days):
        billing_date = start_date + timedelta(days=day_index)
        is_weekday = billing_date.weekday() < 5
        is_ml_spike_day = random.random() < 0.05
        storage_trend = 1.0 + (day_index / max(num_days - 1, 1)) * 0.35

        for _ in range(records_per_day):
            provider = random.choice(PROVIDERS)
            service = random.choices(ALL_SERVICES, weights=SERVICE_WEIGHTS, k=1)[0]
            environment = random.choices(ENVIRONMENTS, weights=[5, 2, 3], k=1)[0]
            category = _service_category(service)

            usage_quantity, unit_cost, usage_unit = _base_usage_and_cost(service)
            total_cost = usage_quantity * unit_cost

            # Environment: dev costs less than prod.
            total_cost *= ENV_COST_MULTIPLIER[environment]

            # Compute: higher spend on weekdays.
            if category == "compute":
                total_cost *= random.uniform(1.2, 1.5) if is_weekday else random.uniform(0.5, 0.75)

            # Storage: slowly increases over the date range.
            if category == "storage":
                total_cost *= storage_trend * random.uniform(0.9, 1.1)

            # ML training: occasional cost spikes.
            if category == "ml" and is_ml_spike_day:
                total_cost *= random.uniform(3.0, 10.0)

            is_tagged = random.random() > 0.18
            tag_owner = fake.name() if is_tagged else ""
            tag_cost_center = random.choice(COST_CENTERS) if is_tagged else ""

            records.append(
                {
                    "billing_date": billing_date.strftime("%Y-%m-%d"),
                    "provider": provider,
                    "service": service,
                    "project": random.choice(PROJECTS),
                    "team": random.choice(TEAMS),
                    "environment": environment,
                    "region": random.choice(REGIONS[provider]),
                    "resource_id": f"{provider.lower()}-{fake.uuid4()[:12]}",
                    "usage_quantity": round(usage_quantity, 4),
                    "usage_unit": usage_unit,
                    "unit_cost": round(unit_cost, 4),
                    "total_cost": round(total_cost, 2),
                    "currency": "USD",
                    "tag_owner": tag_owner,
                    "tag_cost_center": tag_cost_center,
                    "is_tagged": is_tagged,
                }
            )

    return pd.DataFrame(records)


def print_summary(df: pd.DataFrame) -> None:
    """Print a short summary of the generated billing dataset."""
    top_services = (
        df.groupby("service")["total_cost"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )

    print(f"Total rows: {len(df):,}")
    print(f"Total cost: ${df['total_cost'].sum():,.2f}")
    print(f"Date range: {df['billing_date'].min()} to {df['billing_date'].max()}")
    print("Top 5 services by cost:")
    for service, cost in top_services.items():
        print(f"  - {service}: ${cost:,.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic cloud billing data.")
    parser.add_argument("--days", type=int, default=90, help="Number of days to generate.")
    parser.add_argument(
        "--records-per-day",
        type=int,
        default=250,
        help="Billing records to create for each day.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="Output CSV path.",
    )
    args = parser.parse_args()

    df = generate_records(num_days=args.days, records_per_day=args.records_per_day)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)

    print(f"Saved billing data to {args.output}")
    print_summary(df)


if __name__ == "__main__":
    main()

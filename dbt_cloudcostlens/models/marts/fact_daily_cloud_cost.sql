select
    billing_date,
    provider,
    service,
    project,
    team,
    environment,
    region,
    count(*) as usage_records,
    round(sum(total_cost), 2) as total_cost
from {{ ref('stg_cloud_usage') }}
group by
    billing_date,
    provider,
    service,
    project,
    team,
    environment,
    region
select
    provider,
    service,
    usage_unit,
    min(billing_date) as first_billing_date,
    max(billing_date) as last_billing_date,
    round(sum(total_cost), 2) as total_cost,
    count(*) as usage_records
from {{ ref('stg_cloud_usage') }}
group by
    provider,
    service,
    usage_unit

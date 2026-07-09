select
    service,
    provider,
    count(*) as usage_records,
    round(sum(total_cost), 2) as total_cost,
    round(avg(total_cost), 2) as avg_record_cost,
    min(billing_date) as first_billing_date,
    max(billing_date) as last_billing_date
from {{ ref('stg_cloud_usage') }}
group by
    service,
    provider
order by total_cost desc
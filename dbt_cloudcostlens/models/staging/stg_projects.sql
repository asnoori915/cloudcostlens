select
    project,
    team,
    tag_cost_center,
    min(billing_date) as first_billing_date,
    max(billing_date) as last_billing_date,
    round(sum(total_cost), 2) as total_cost,
    count(distinct resource_id) as resource_count
from {{ ref('stg_cloud_usage') }}
group by
    project,
    team,
    tag_cost_center

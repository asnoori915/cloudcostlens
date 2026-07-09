with project_spend as (

    select
        project,
        min(team) as team,
        round(sum(total_cost), 2) as total_cost
    from {{ ref('stg_cloud_usage') }}
    group by project

),

budgets as (

    select
        project,
        case
            when project = 'analytics-platform' then 120000
            when project = 'ml-training' then 180000
            when project = 'customer-app' then 150000
            when project = 'internal-tools' then 75000
            when project = 'data-ingestion' then 110000
            else 100000
        end as budget_amount
    from project_spend

)

select
    p.project,
    p.team,
    p.total_cost,
    b.budget_amount,
    round((p.total_cost / b.budget_amount) * 100, 2) as budget_used_pct,
    case
        when p.total_cost > b.budget_amount then 'OVER_BUDGET'
        when p.total_cost >= b.budget_amount * 0.8 then 'AT_RISK'
        else 'OK'
    end as budget_status
from project_spend p
left join budgets b
    on p.project = b.project

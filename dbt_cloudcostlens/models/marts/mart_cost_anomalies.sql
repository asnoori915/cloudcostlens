with daily_service_spend as (

    select
        billing_date,
        service,
        project,
        round(sum(total_cost), 2) as daily_cost
    from {{ ref('stg_cloud_usage') }}
    group by billing_date, service, project

),

rolling_stats as (

    select
        billing_date,
        service,
        project,
        daily_cost,
        avg(daily_cost) over (
            partition by service, project
            order by billing_date
            rows between 13 preceding and 1 preceding
        ) as avg_previous_14_days,
        stddev_samp(daily_cost) over (
            partition by service, project
            order by billing_date
            rows between 13 preceding and 1 preceding
        ) as stddev_previous_14_days
    from daily_service_spend

)

select
    billing_date,
    service,
    project,
    daily_cost,
    round(avg_previous_14_days, 2) as avg_previous_14_days,
    round(stddev_previous_14_days, 2) as stddev_previous_14_days,
    case
        when avg_previous_14_days is null then false
        when stddev_previous_14_days is null then false
        when daily_cost > avg_previous_14_days + (2 * stddev_previous_14_days) then true
        else false
    end as is_anomaly
from rolling_stats
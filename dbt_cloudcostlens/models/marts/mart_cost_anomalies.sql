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

),

enriched as (

    select
        billing_date,
        service,
        project,
        daily_cost,
        avg_previous_14_days,
        stddev_previous_14_days,
        round(daily_cost - avg_previous_14_days, 2) as anomaly_amount,
        case
            when avg_previous_14_days is null or avg_previous_14_days = 0 then null
            else round(
                ((daily_cost - avg_previous_14_days) / avg_previous_14_days) * 100,
                2
            )
        end as anomaly_pct,
        case
            when avg_previous_14_days is null or stddev_previous_14_days is null then 'NORMAL'
            when daily_cost > avg_previous_14_days + (3 * stddev_previous_14_days) then 'HIGH'
            when daily_cost > avg_previous_14_days + (2.5 * stddev_previous_14_days) then 'MEDIUM'
            when daily_cost > avg_previous_14_days + (2 * stddev_previous_14_days) then 'LOW'
            else 'NORMAL'
        end as anomaly_severity
    from rolling_stats

)

select
    billing_date,
    service,
    project,
    daily_cost,
    round(avg_previous_14_days, 2) as avg_previous_14_days,
    round(stddev_previous_14_days, 2) as stddev_previous_14_days,
    anomaly_amount,
    anomaly_pct,
    anomaly_severity,
    case
        when anomaly_severity in ('LOW', 'MEDIUM', 'HIGH') then true
        else false
    end as is_anomaly
from enriched

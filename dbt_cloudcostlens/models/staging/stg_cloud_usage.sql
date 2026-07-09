with source as (

    select *
    from raw_cloud_billing

),

renamed as (

    select
        cast(billing_date as date) as billing_date,
        provider,
        service,
        project,
        team,
        environment,
        region,
        resource_id,
        cast(usage_quantity as double) as usage_quantity,
        usage_unit,
        cast(unit_cost as double) as unit_cost,
        cast(total_cost as double) as total_cost,
        currency,
        tag_owner,
        tag_cost_center,
        cast(is_tagged as boolean) as is_tagged
    from source

)

select *
from renamed
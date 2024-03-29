{{
    config(
        materialized='view'
    )
}}

with tripdata as
(
  select *,
  row_number() over(partition by vendor_id, lpep_pickup_datetime) as rn
  from {{ source('staging', 'nyc_green_trips_all')}}
  where vendor_id is not null
)
select

    -- identifiers
    {{ dbt_utils.generate_surrogate_key(['vendor_id', 'lpep_pickup_datetime']) }} as trip_id,
    cast(vendor_id as integer) as vendor_id,
    cast(ratecode_id as integer) as ratecode_id,
    cast(pu_location_id as integer) as pickup_location_id,
    cast(do_location_id as integer) as dropoff_location_id,

    -- timestamps
    cast(lpep_pickup_datetime as timestamp) as pickup_datetime,
    cast(lpep_dropoff_datetime as timestamp) as dropoff_datetime,

    -- trip info
    store_and_fwd_flag,
    cast(passenger_count as integer) as passenger_count,
    cast(trip_distance as numeric) as trip_distance,
    cast(trip_type as integer) as trip_type,

    -- payment info
    cast(fare_amount as numeric) as fare_amount,
    cast(extra as numeric) as extra,
    cast(mta_tax as numeric) as mta_tax,
    cast(tip_amount as numeric) as tip_amount,
    cast(tolls_amount as numeric) as tolls_amount,
    cast(ehail_fee as numeric) as ehail_fee,
    cast(improvement_surcharge as numeric) as improvement_surcharge,
    cast(payment_type as integer) as payment_type,
    cast(total_amount as numeric) as total_amount,
    {{ get_payment_type_description('payment_type') }} as payment_type_description

from tripdata
where rn = 1

-- dbt build --select <model_name> --vars '{ is_test_run: false }'
{% if var('is_test_run', default=true) %}

  limit 100

{% endif %}
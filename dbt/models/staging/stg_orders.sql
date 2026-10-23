select
    order_id::integer as order_id,
    customer_id::integer as customer_id,
    product_id::integer as product_id,
    order_date::date as order_date,
    quantity::integer as quantity,
    unit_price::numeric(12,2) as unit_price,
    lower(trim(status)) as status,
    (quantity::numeric * unit_price::numeric)::numeric(14,2) as sales_amount
from {{ source('raw', 'orders') }}

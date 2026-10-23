select
    product_id::integer as product_id,
    trim(product_name) as product_name,
    trim(category) as category,
    unit_price::numeric(12,2) as unit_price
from {{ source('raw', 'products') }}

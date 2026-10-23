select
    product_id,
    product_name,
    category,
    unit_price
from {{ ref('stg_products') }}

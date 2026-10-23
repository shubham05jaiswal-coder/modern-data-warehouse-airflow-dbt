select
    o.order_id,
    o.order_date,
    o.customer_id,
    c.customer_name,
    o.product_id,
    p.product_name,
    p.category,
    o.quantity,
    o.unit_price,
    o.sales_amount,
    o.status
from {{ ref('stg_orders') }} o
left join {{ ref('dim_customers') }} c on o.customer_id = c.customer_id
left join {{ ref('dim_products') }} p on o.product_id = p.product_id

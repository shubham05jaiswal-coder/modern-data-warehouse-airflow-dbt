select order_id, sales_amount
from {{ ref('fct_orders') }}
where sales_amount < 0

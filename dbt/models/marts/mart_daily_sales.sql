select
    order_date,
    count(*) filter (where status = 'completed') as completed_order_count,
    sum(quantity) filter (where status = 'completed') as units_sold,
    coalesce(sum(sales_amount) filter (where status = 'completed'), 0)::numeric(14,2) as gross_revenue,
    coalesce(avg(sales_amount) filter (where status = 'completed'), 0)::numeric(14,2) as average_order_value
from {{ ref('fct_orders') }}
group by order_date

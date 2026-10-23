select
    customer_id,
    customer_name,
    email,
    city,
    signup_date
from {{ ref('stg_customers') }}

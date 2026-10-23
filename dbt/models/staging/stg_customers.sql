select
    customer_id::integer as customer_id,
    trim(customer_name) as customer_name,
    lower(trim(email)) as email,
    trim(city) as city,
    signup_date::date as signup_date
from {{ source('raw', 'customers') }}

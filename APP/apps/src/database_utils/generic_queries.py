from apps.utils.constant import (
    DIM_CATEGORIES, DIM_DATES, PINCODE_TABLE, LANDING_PAGE_ECHART_TABLE,
    LOGISTICS_DISTRICT_TABLE, MONTHLY_DISTRICT_TABLE
)

fetch_district_list_query = f'''
        SELECT state_name as delivery_state, district_name as delivery_district 
        FROM {PINCODE_TABLE} group by 1, 2
    '''


fetch_max_date_query = f'''select min(order_date) as min_date, max(order_date) as max_date from {DIM_DATES}'''

max_date_retail_overall = f'''
                                WITH DateBounds AS (
    SELECT 
        MIN(order_year::int * 100 + order_month::int) AS min_year_month,
        MAX(order_year::int * 100 + order_month::int) AS max_year_month
    FROM {MONTHLY_DISTRICT_TABLE}
    where domain = 'Retail'
),
MaxPreviousMonth AS (
    SELECT 
        CASE 
            WHEN max_year_month %% 100 = 1 THEN (max_year_month / 100 - 1) * 100 + 12
            ELSE max_year_month - 1
        END AS prev_year_month
    FROM DateBounds
)
SELECT 
    (SELECT min_year_month FROM DateBounds) AS min_year_month,
    (SELECT prev_year_month FROM MaxPreviousMonth) AS max_year_month
'''

max_date_logistics_overall = f'''
                                WITH DateBounds AS (
    SELECT 
        MIN(order_year::int * 100 + order_month::int) AS min_year_month,
        MAX(order_year::int * 100 + order_month::int) AS max_year_month
    FROM {MONTHLY_DISTRICT_TABLE}
    where domain = 'Retail'
),
MaxPreviousMonth AS (
    SELECT 
        CASE 
            WHEN max_year_month %% 100 = 1 THEN (max_year_month / 100 - 1) * 100 + 12
            ELSE max_year_month - 1
        END AS prev_year_month
    FROM DateBounds
)
SELECT 
    (SELECT min_year_month FROM DateBounds) AS min_year_month,
    (SELECT prev_year_month FROM MaxPreviousMonth) AS max_year_month
'''


max_date_logistics = f'''select min(order_date) as min_date, max(order_date) as max_date from {LOGISTICS_DISTRICT_TABLE}'''

pincode_query = f''' select 
                    state_code as "State Code", 
                    state_name as "State", 
                    district_name as "District", 
                    pincode as "Pincode"
                from {PINCODE_TABLE} order by "Statecode"'''

fetch_category_list_query = f'''
                select 
                category  as category,
                sub_category 
                from {DIM_CATEGORIES}
                group by 1,2
        '''

landing_page_echart_data_query = f'''
    select 
	domain, 
	month::date as date, 
	order_count as weekly_average 
    from {LANDING_PAGE_ECHART_TABLE}
    where (extract(year from month)*100)+extract(month from month)
     < (select max((extract(year from month)*100)+extract(month from month)) from {LANDING_PAGE_ECHART_TABLE})
'''
landing_page_cumulative_orders_query = f'''
    select max(month), sum(order_count) as total_orders from 
        {LANDING_PAGE_ECHART_TABLE} 
    where domain='ONDC Network - All Domains' and
    (extract(year from month)*100)+extract(month from month)
     < (select max((extract(year from month)*100)+extract(month from month)) from {LANDING_PAGE_ECHART_TABLE})
'''
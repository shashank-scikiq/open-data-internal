INSERT INTO POSTGRES_SCHEMA.CATEGORY_TBL(order_date, category, delivery_district, 
delivery_state, delivery_state_code, seller_state, seller_district, seller_state_code, 
total_orders_delivered, pincode_count, total_items, intrastate_orders, intradistrict_orders, 
interstate_orders, intrastate_orders_percentage, intradistrict_orders_percentage)
WITH ItemLevelAggregation AS (
    SELECT
        order_date,
        consolidated_categories AS category,
        delivery_district,
        delivery_state,
        delivery_state_code,
        seller_state,
        seller_district,
        seller_state_code,
        network_order_id,
        MAX(delivery_pincode) AS delivery_pincode,
        SUM(total_items) AS total_items
    FROM POSTGRES_SCHEMA.AGG_TBL_B2C
    GROUP BY
         order_date, category, delivery_district, delivery_state,
        delivery_state_code, seller_state, seller_district, seller_state_code,
        network_order_id
),OrderLevelAggregation AS (
    SELECT
        order_date,
        category,
        delivery_district,
        delivery_state,
        delivery_state_code,
        seller_state,
        seller_district,
        seller_state_code,
        COUNT(DISTINCT network_order_id) AS total_orders_delivered,
        COUNT(distinct delivery_pincode) AS pincode_count,
        SUM(total_items) AS total_items,
        SUM(CASE WHEN delivery_state = seller_state THEN 1 ELSE 0 END) AS intrastate_orders,
        SUM(CASE WHEN delivery_district = seller_district THEN 1 ELSE 0 END) AS intradistrict_orders,
        SUM(CASE WHEN delivery_state != seller_state THEN 1 ELSE 0 END) AS interstate_orders
    FROM
        ItemLevelAggregation
    GROUP BY
         order_date, category, delivery_district, delivery_state, delivery_state_code, seller_state, seller_district, seller_state_code
)
SELECT
    order_date,
    category,
    delivery_district,
    MAX(delivery_state) AS delivery_state,
    delivery_state_code,
    MAX(seller_state) AS seller_state,
    seller_district,
    seller_state_code,
    SUM(total_orders_delivered) AS total_orders_delivered,
    SUM(pincode_count) AS pincode_count,
    SUM(total_items) AS total_items,
    SUM(intrastate_orders) AS intrastate_orders,
    SUM(intradistrict_orders) AS intradistrict_orders,
    SUM(interstate_orders) AS interstate_orders,
    ROUND(100.0 * SUM(intrastate_orders) / SUM(total_orders_delivered), 2) AS intrastate_orders_percentage,
    ROUND(100.0 * SUM(intradistrict_orders) / SUM(total_orders_delivered), 2) AS intradistrict_orders_percentage
FROM
    OrderLevelAggregation
GROUP BY
     order_date, category, delivery_district, delivery_state_code, seller_district, seller_state_code
ORDER BY
    order_date, category;
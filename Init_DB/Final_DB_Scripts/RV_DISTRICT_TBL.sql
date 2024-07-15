INSERT INTO POSTGRES_SCHEMA.RV_DISTRICT_TBL
(SELECT
    order_date,
    delivery_district,
    delivery_state,
    delivery_state_code,
    COUNT(network_order_id) AS total_orders_delivered,
    sum(rvfod.total_items) as total_items
FROM POSTGRES_SCHEMA.AGG_TBL_VOUCHER rvfod 
group by order_date, delivery_district, delivery_state, delivery_state_code
ORDER BY order_date, delivery_district)
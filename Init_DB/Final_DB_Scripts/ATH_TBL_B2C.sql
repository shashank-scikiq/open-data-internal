WITH order_subcategories AS (
    select
        "network order id", "Item Category" AS sub_category,
        array_join(cast(array_agg(coalesce("Item Consolidated Category", 'Missing')) as array(varchar)),',') AS consolidated_categories,
        COUNT(DISTINCT "Item Consolidated Category") AS category_count
    from
        (select "network order id", "Item Consolidated Category", "Item Category"
      from ATH_DB.ATH_TBL_B2C
      where date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')) = DATE('{date_val}')
      and "seller np name" NOT IN ('gl-6912-httpapi.glstaging.in/gl/ondc')
      group by "network order id","Item Consolidated Category","Item Category"  )
    group by "network order id", "Item Category"
),
distinct_subcategories AS (
  select "network order id", "Item Category" AS sub_category
  from ATH_DB.ATH_TBL_B2C
  where date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')) = DATE('{date_val}')
  and "seller np name" NOT IN ('gl-6912-httpapi.glstaging.in/gl/ondc')
  group by "network order id", "Item Category"
)
SELECT odv."network order id" AS network_order_id,
    odv."Item Category" AS sub_category,
    MAX(odv."seller np name") AS seller_np,
    SUM(CAST(odv."Qty" AS Decimal)) AS total_items,MAX(case WHEN TRIM(odv."Domain") = 'nic2004:52110' THEN 'Retail' ELSE 'Others' END) AS domain,
    MAX(CONCAT(lower(trim(odv."seller np name")), '-', lower(trim(odv."Provider id")))) AS provider_key,
    MAX(case WHEN odv."Order Status" IS NULL OR TRIM(odv."Order Status") = '' THEN 'In-progress' ELSE TRIM(odv."Order Status") END) AS order_status,
    MAX(CASE WHEN UPPER(odv."Seller Pincode") LIKE '%XXX%' OR UPPER(odv."Seller Pincode") LIKE '%*%' THEN NULL ELSE odv."Seller Pincode" END) AS seller_pincode,
    MAX(case WHEN UPPER(odv."Delivery Pincode") LIKE '%XXX%' OR UPPER(odv."Delivery Pincode") LIKE '%*%' THEN null ELSE odv."Delivery Pincode" END) AS delivery_pincode,
    MAX(DATE(SUBSTRING(odv."O_Created Date & Time", 1, 10))) AS order_date,
    MAX(oc.consolidated_categories) AS consolidated_categories,
   MAX(CASE WHEN oc.category_count > 1 THEN 1 ELSE 0 END) AS multi_category_flag,
   NULL as delivery_state,
   NULL as delivery_state_code, 
   NULL as delivery_district,
   NULL as seller_state,
   NULL as seller_state_code,
   NULL as seller_district
FROM ATH_DB.ATH_TBL_B2C odv
LEFT JOIN order_subcategories oc ON odv."network order id" = oc."network order id" AND odv."Item Category" = oc.sub_category
LEFT JOIN distinct_subcategories dc ON odv."network order id" = dc."network order id" AND odv."Item Category" = dc.sub_category
WHERE odv."seller np name" NOT IN ('gl-6912-httpapi.glstaging.in/gl/ondc')
and date(date_parse("O_Created Date & Time",'%Y-%m-%dT%H:%i:%s')) = DATE('{date_val}')
GROUP BY odv."network order id", odv."Item Category";
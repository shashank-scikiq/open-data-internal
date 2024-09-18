import pandas as pd
from apps.logging_conf import log_function_call, ondcLogger
from apps.utils import constant
from datetime import datetime
@log_function_call(ondcLogger)
def fetch_top3_district_sellers(connector, start_date, end_date, category=None, sub_category=None, domain=None,
                                state=None):
    table_name = constant.SELLER_TABLE
    query = f"""
        WITH TopDistricts AS (
            SELECT 
                seller_district,
                COUNT(DISTINCT trim(lower(provider_key))) AS active_sellers_count
            FROM 
                {table_name}
            WHERE 
                order_date BETWEEN %s AND %s
                AND seller_district <> 'Undefined'
                AND seller_district IS NOT NULL

    """

    parameters = [start_date, end_date]

    if category and category != 'None':
        query += constant.category_sub_query
        parameters.append(category)

    if sub_category:
        query += constant.sub_category_sub_query
        parameters.append(sub_category)

    if domain:
        query += constant.domain_sub_query
        parameters.append(domain)

    if state:
        query += constant.seller_state_sub_query
        parameters.append(state)

    query += f"""
            GROUP BY 
                seller_district
            HAVING COUNT(DISTINCT provider_key) > {constant.ACTIVE_SELLERS_MASKING}
            ORDER BY 
                active_sellers_count DESC
            LIMIT 3
        ),
        FinalResult AS (
            SELECT 
                om.order_date AS date,
                om.seller_district AS district,
                COUNT(DISTINCT provider_key) AS active_sellers_count
            FROM 
                {table_name} om
            INNER JOIN 
                TopDistricts td ON om.seller_district = td.seller_district
            WHERE 
                om.order_date BETWEEN %s AND %s
    """

    parameters.extend([start_date, end_date])

    if category and category != 'None':
        query += constant.tdr_category_sub_query
        parameters.append(category)

    if sub_category:
        query += constant.tdr_sub_category_sub_query
        parameters.append(sub_category)

    if domain:
        query += constant.tdr_domain_sub_query
        parameters.append(domain)

    if state:
        query += constant.tdr_seller_state_sub_query
        parameters.append(state)

    query += """
            GROUP BY 
                om.order_date, om.seller_district
            ORDER BY 
                om.order_date, COUNT(DISTINCT provider_key) DESC
        )
        SELECT * FROM FinalResult;
    """

    connector.execute(query, tuple(parameters))
    df = pd.DataFrame(connector.fetchall(), columns=[desc[0] for desc in connector.description])
    return df


@log_function_call(ondcLogger)
def fetch_overall_top3_district_sellers(connector, start_date, end_date, category=None, sub_category=None, domain=None, state=None):
    table_name = constant.MONTHLY_PROVIDERS
    if domain == 'Logistics':
        table_name = constant.LOGISTICS_MONTHLY_PROVIDERS
    stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
    edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

    # Extract month and year
    start_month = stdate_obj.month
    end_month = edate_obj.month
    start_year = stdate_obj.year
    end_year = edate_obj.year

    parameters = {
        'start_month': start_month,
        'start_year': start_year,
        'end_month': end_month,
        'end_year': end_year
    }

    query = f"""
        WITH TopDistricts AS (
            SELECT 
                seller_district,
                COUNT(DISTINCT TRIM(LOWER(provider_key))) AS active_sellers_count
            FROM 
                {table_name}
            WHERE
                (order_year > %(start_year)s OR (order_year = %(start_year)s AND order_month >= %(start_month)s))
                AND (order_year < %(end_year)s OR (order_year = %(end_year)s AND order_month <= %(end_month)s))
                AND seller_district <> 'Undefined'
                AND seller_district IS NOT NULL
    """

    # if domain:
    #     query += " AND domain = %(domain)s"
    #     parameters['domain'] = domain

    if state:
        query += " AND COALESCE(UPPER(seller_state), 'MISSING') = UPPER(%(state)s)"
        parameters['state'] = state.upper()

    query += f"""
            GROUP BY 
                seller_district
            HAVING COUNT(DISTINCT TRIM(LOWER(provider_key))) > 0  -- Add any necessary masking logic here
            ORDER BY 
                active_sellers_count DESC
            LIMIT 3
        ),
        FinalResult AS (
            SELECT 
                om.order_month AS order_month,
                om.order_year AS order_year,
                om.seller_district AS district,
                COUNT(DISTINCT TRIM(LOWER(om.provider_key))) AS active_sellers_count
            FROM 
                {table_name} om
            INNER JOIN 
                TopDistricts td ON om.seller_district = td.seller_district
            WHERE
                (om.order_year > %(start_year)s OR (om.order_year = %(start_year)s AND om.order_month >= %(start_month)s))
                AND (om.order_year < %(end_year)s OR (om.order_year = %(end_year)s AND om.order_month <= %(end_month)s))
    """

    # if domain:
    #     query += " AND om.domain = %(domain)s"
    #     parameters['domain'] = domain

    if state:
        query += " AND COALESCE(UPPER(om.seller_state), 'MISSING') = UPPER(%(state)s)"
        parameters['state'] = state.upper()

    query += """
            GROUP BY 
                om.order_month, om.order_year, om.seller_district
            ORDER BY 
                om.order_year, om.order_month, COUNT(DISTINCT TRIM(LOWER(provider_key))) DESC
        )
        SELECT * FROM FinalResult;
    """

    connector.execute(query, parameters)
    df = pd.DataFrame(connector.fetchall(), columns=[desc[0] for desc in connector.description])
    return df




@log_function_call(ondcLogger)
def fetch_top3_states_sellers(connector, start_date, end_date, category=None, sub_category=None, domain=None,
                              state=None):

    base_table = constant.SELLER_TABLE
    query = f'''
            WITH StateSellerCounts AS (
                SELECT 
                    COALESCE(seller_state, 'MISSING') AS seller_state,
                    COUNT(DISTINCT trim(lower(provider_key))) AS active_sellers_count
                FROM 
                    {base_table}
                WHERE 
                    order_date BETWEEN %s AND %s
                    and seller_state <> ''
        '''

    parameters = [start_date, end_date]

    if domain:
        query += constant.domain_sub_query
        parameters.append(domain)
    if state:
        query += " AND COALESCE(upper(seller_state), 'MISSING') = upper(%s)"
        parameters.append(state.upper())
    if category and category != 'None':
        query += constant.category_sub_query
        parameters.append(category)
    if sub_category:
        query += constant.sub_category_sub_query
        parameters.append(sub_category)

    query += f'''
                GROUP BY 
                    seller_state
            ),
            RankedStates AS (
                SELECT
                    seller_state,
                    active_sellers_count,
                    RANK() OVER (ORDER BY active_sellers_count DESC) AS state_rank
                FROM
                    StateSellerCounts
                where active_sellers_count > {constant.ACTIVE_SELLERS_MASKING}
                LIMIT 3
            )
            SELECT 
                om.order_date AS date,
                COALESCE(om.seller_state, 'MISSING') AS state,
                COUNT(DISTINCT om.provider_key) AS active_sellers_count,
                rs.state_rank
            FROM 
                {base_table} om
            INNER JOIN 
                RankedStates rs ON COALESCE(om.seller_state, 'MISSING') = rs.seller_state
            WHERE 
                om.order_date BETWEEN %s AND %s
        '''

    parameters.extend([start_date, end_date])

    if domain:
        query += constant.tdr_domain_sub_query
        parameters.append(domain)
    if state:
        query += " AND COALESCE(om.seller_state, 'MISSING') = upper(%s)"
        parameters.append(state.upper())
    if category and category != 'None':
        query += constant.tdr_category_sub_query
        parameters.append(category)
    if sub_category:
        query += constant.tdr_sub_category_sub_query
        parameters.append(sub_category)

    query += '''
            GROUP BY 
                om.order_date, om.seller_state, rs.state_rank
            ORDER BY 
                rs.state_rank, om.order_date
        '''

    connector.execute(query, tuple(parameters))
    df = pd.DataFrame(connector.fetchall(), columns=[desc[0] for desc in connector.description])
    return df


@log_function_call(ondcLogger)
def fetch_overall_top3_states_sellers(connector, start_date, end_date, category=None, sub_category=None, domain=None, state=None):
    base_table = constant.MONTHLY_PROVIDERS
    if domain == 'Logistics':
        base_table = constant.LOGISTICS_MONTHLY_PROVIDERS

    stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
    edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

    # Extract month and year
    start_month = stdate_obj.month
    end_month = edate_obj.month
    start_year = stdate_obj.year
    end_year = edate_obj.year

    parameters = {
        'start_month': start_month,
        'start_year': start_year,
        'end_month': end_month,
        'end_year': end_year
    }

    query = f'''
        WITH StateSellerCounts AS (
            SELECT 
                COALESCE(seller_state, 'MISSING') AS seller_state,
                COUNT(DISTINCT TRIM(LOWER(provider_key))) AS active_sellers_count
            FROM 
                {base_table}
            WHERE
                (order_year > %(start_year)s OR (order_year = %(start_year)s AND order_month >= %(start_month)s))
                AND (order_year < %(end_year)s OR (order_year = %(end_year)s AND order_month <= %(end_month)s))
                AND seller_state <> ''
    '''

    # if domain:
    #     query += " AND domain = %(domain)s"
    #     parameters['domain'] = domain

    if state:
        query += " AND COALESCE(UPPER(seller_state), 'MISSING') = UPPER(%(state)s)"
        parameters['state'] = state.upper()

    query += f'''
            GROUP BY 
                seller_state
        ),
        RankedStates AS (
            SELECT
                seller_state,
                active_sellers_count,
                RANK() OVER (ORDER BY active_sellers_count DESC) AS state_rank
            FROM
                StateSellerCounts
            WHERE active_sellers_count > 0  -- Add any necessary masking logic here
            LIMIT 3
        )
        SELECT 
            om.order_month AS order_month,
            om.order_year AS order_year,
            COALESCE(om.seller_state, 'MISSING') AS state,
            COUNT(DISTINCT TRIM(LOWER(om.provider_key))) AS active_sellers_count,
            rs.state_rank
        FROM 
            {base_table} om
        INNER JOIN 
            RankedStates rs ON COALESCE(om.seller_state, 'MISSING') = rs.seller_state
        WHERE
            (om.order_year > %(start_year)s OR (om.order_year = %(start_year)s AND om.order_month >= %(start_month)s))
            AND (om.order_year < %(end_year)s OR (om.order_year = %(end_year)s AND om.order_month <= %(end_month)s))
    '''

    # if domain:
    #     query += " AND om.domain = %(domain)s"
    #     parameters['domain'] = domain

    if state:
        query += " AND COALESCE(UPPER(om.seller_state), 'MISSING') = UPPER(%(state)s)"
        parameters['state'] = state.upper()

    query += '''
        GROUP BY 
            om.order_month, om.order_year, om.seller_state, rs.state_rank
        ORDER BY 
            rs.state_rank, om.order_year, om.order_month
    '''

    connector.execute(query, parameters)
    df = pd.DataFrame(connector.fetchall(), columns=[desc[0] for desc in connector.description])
    return df



@log_function_call(ondcLogger)
def fetch_state_sellers(connector, start_date, end_date, category=None, sub_category=None, domain=None, state=None):

    table_name = constant.SELLER_TABLE

    # Base SQL query
    query = f"""
        SELECT 
            seller_state, 
            COUNT(DISTINCT trim(lower(provider_key))) as active_sellers_count
        FROM 
            {table_name}
        WHERE 
            order_date >= %s AND order_date <= %s
    """

    parameters = [start_date, end_date]

    query_conditions = [
        ("category = %s", [category]) if category and category != 'None' else None,
        ("sub_category = %s", [sub_category]) if sub_category else None,
        ("domain = %s", [domain]) if domain else None,
        ("upper(seller_state) = upper(%s)", [state]) if state else None
    ]

    query_conditions = [condition for condition in query_conditions if condition is not None]

    for condition, param in query_conditions:
        query += f" AND {condition}"
        parameters.extend(param)

    query += f"""
        AND seller_state IS NOT NULL
        GROUP BY 
            seller_state
        HAVING COUNT(DISTINCT provider_key) > {constant.ACTIVE_SELLERS_MASKING}
        ORDER BY 
            active_sellers_count DESC
    """

    connector.execute(query, tuple(parameters))
    df = pd.DataFrame(connector.fetchall(), columns=[desc[0] for desc in connector.description])
    return df


@log_function_call(ondcLogger)
def fetch_downloadable_data(connector, start_date, end_date, domain=None, tab_name=None):
    if tab_name and tab_name == 'State wise orders':
        query = f'''
                    WITH DistrictRanking AS (
                        SELECT
                            swdlo.order_date,
                            coalesce(swdlo.delivery_state, 'Missing') as delivery_state,
                            coalesce(swdlo.delivery_district, 'Missing') as delivery_district,
                            SUM(swdlo.total_orders_delivered) AS total_orders_in_district,
                            ROW_NUMBER() OVER (PARTITION BY swdlo.delivery_state, swdlo.order_date 
                            ORDER BY SUM(swdlo.total_orders_delivered) DESC) AS rank_in_state
                        FROM
                            {constant.DISTRICT_TABLE} swdlo
                        WHERE
                            swdlo.order_date BETWEEN %s AND %s
                        GROUP BY
                            swdlo.order_date,
                            swdlo.delivery_state,
                            swdlo.delivery_district
                    ),
                    ActiveSellers AS (
                        SELECT
                            ds.order_date,
                            coalesce(ds.seller_state, 'Missing') AS delivery_state,
                            COUNT(DISTINCT trim(lower(ds.provider_key))) AS total_active_sellers
                        FROM
                            {constant.SELLER_TABLE} ds
                        WHERE
                            ds.order_date BETWEEN %s AND %s
                        GROUP BY
                            ds.order_date, ds.seller_state
                    ),
                    AggregatedData AS (
                        SELECT
                            swdlo.order_date AS "Order Date",
                            coalesce(swdlo.delivery_state, 'Missing') AS "Delivery State",
                            COUNT(DISTINCT swdlo.delivery_district) AS "Total Districts",
                            SUM(swdlo.total_orders_delivered) AS "Delivered Orders",
                            SUM(swdlo.total_items) AS "Total Delivered Items",
                            ROUND(COALESCE(SUM(swdlo.total_items::numeric) / 
                            NULLIF(SUM(swdlo.total_orders_delivered::numeric), 0), 0), 2) 
                            AS "Average Items per Order",
                            ROUND(COALESCE(100 * SUM(swdlo.intrastate_orders::numeric) / 
                            NULLIF(SUM(swdlo.total_orders_delivered::numeric), 0), 0), 2) 
                            AS "Intrastate Orders Percentage"
                        FROM
                            {constant.DISTRICT_TABLE} swdlo
                        WHERE
                            swdlo.order_date BETWEEN %s AND %s
                        GROUP BY
                            swdlo.order_date, swdlo.delivery_state
                    )
                    SELECT
                        TO_CHAR(AD."Order Date", 'YYYY-MM-DD') AS "Order Date",
                        AD."Delivery State",
                        AD."Total Districts",
                        AD."Delivered Orders" as "Confirmed Orders",
                        AD."Total Delivered Items" as "Total Confirmed Items",
                        AD."Average Items per Order",
                        AD."Intrastate Orders Percentage",
                        COALESCE(
                            CASE
                                WHEN ASel.total_active_sellers < 3 THEN 0
                                ELSE ASel.total_active_sellers
                            END, 0) AS "Total Active Sellers",
                        DR.delivery_district AS "Most Ordering District"
                    FROM
                        AggregatedData AD
                    LEFT JOIN
                        ActiveSellers ASel ON coalesce(AD."Delivery State", 'Missing') = coalesce(ASel.delivery_state, 'Missing') 
                        AND AD."Order Date" = ASel.order_date
                    LEFT JOIN
                        (SELECT * FROM DistrictRanking WHERE rank_in_state = 1) DR 
                        ON AD."Delivery State" = DR.delivery_state AND AD."Order Date" = DR.order_date
                    ORDER BY AD."Order Date", AD."Delivery State"
                '''
        parameters = [start_date, end_date, start_date, end_date, start_date, end_date]

    elif tab_name and tab_name == 'Category wise orders':
        query = f'''
                        WITH DistrictAggregates AS (
                            SELECT
                                order_date,
                                coalesce(delivery_state, 'Missing') as delivery_state,
                                category,
                                sub_category,
                                coalesce(delivery_district, 'Missing') as delivery_district,
                                SUM(total_orders_delivered) AS orders_delivered
                            FROM
                                {constant.SUB_CATEGORY_TABLE}
                            WHERE
                                order_date BETWEEN %s AND %s
                            GROUP BY
                                order_date,
                                delivery_state,
                                category,
                                sub_category,
                                delivery_district
                        ), RankedDistricts AS (
                            SELECT
                                order_date,
                                delivery_state,
                                category,
                                sub_category,
                                delivery_district,
                                ROW_NUMBER() OVER (PARTITION BY order_date, delivery_state, category, sub_category 
                                ORDER BY orders_delivered DESC) AS district_rank
                            FROM
                                DistrictAggregates
                        ), ActiveSellers AS (
                            SELECT
                                dp.order_date,
                                coalesce(dp.seller_state, 'Missing') AS delivery_state,
                                dp.category,
                                dp.sub_category,
                                COUNT(distinct dp.provider_key) AS total_active_sellers
                            FROM
                                {constant.SELLER_TABLE} dp
                            WHERE
                                 dp.order_date BETWEEN %s AND %s
                            GROUP BY
                                dp.order_date,
                                dp.seller_state,
                                dp.category,
                                dp.sub_category
                        )
                        SELECT
                            TO_CHAR(swsclo.order_date, 'YYYY-MM-DD') AS "Order Date",
                            coalesce(swsclo.delivery_state, 'Missing') AS "Delivery State",
                            COALESCE(swsclo.category, 'Missing') AS "Category",
                            COALESCE(swsclo.sub_category, 'Missing') AS "Sub Category",
                            SUM(swsclo.total_orders_delivered) AS "Confirmed Orders",
                            ROUND(COALESCE(SUM(swsclo.total_items::numeric) / 
                            NULLIF(SUM(swsclo.total_orders_delivered::numeric), 0), 0), 2) AS "Average Items per Order",
                            ROUND(COALESCE(100 * SUM(swsclo.intrastate_orders::numeric) / 
                            NULLIF(SUM(swsclo.total_orders_delivered::numeric), 0), 0), 2) 
                            AS "Intrastate Orders Percentage",
                            SUM(swsclo.total_items) AS "Total Confirmed Items",
                            COALESCE(MAX(CASE
                                WHEN ASel.total_active_sellers < 3 THEN 0
                                    ELSE ASel.total_active_sellers
                                END), 0) AS "Total Active Sellers",
                            RD.delivery_district AS "Most Delivering District"
                        FROM
                            {constant.SUB_CATEGORY_TABLE} swsclo
                        FULL OUTER JOIN
                            ActiveSellers ASel ON coalesce(swsclo.delivery_state, 'Missing') = coalesce(ASel.delivery_state, 'Missing')
                            AND swsclo.category = ASel.category
                            AND swsclo.sub_category = ASel.sub_category
                            AND swsclo.order_date = ASel.order_date
                        LEFT JOIN
                            (SELECT * FROM RankedDistricts WHERE district_rank = 1) RD 
                            ON swsclo.delivery_state = RD.delivery_state
                            AND swsclo.category = RD.category
                            AND swsclo.sub_category = RD.sub_category
                            AND swsclo.order_date = RD.order_date
                        WHERE
                            swsclo.order_date BETWEEN %s AND %s
                        GROUP BY
                            swsclo.order_date,
                            swsclo.delivery_state,
                            swsclo.category,
                            swsclo.sub_category,
                            RD.delivery_district
                        ORDER BY
                            swsclo.order_date,
                            swsclo.delivery_state,
                            RD.delivery_district,
                            swsclo.category,
                            swsclo.sub_category
                '''

        parameters = [start_date, end_date, start_date, end_date, start_date, end_date]

    elif tab_name and tab_name == 'District wise orders':
        query = f'''
                       WITH ActiveSellers AS (
                            SELECT
                                dp.order_date,
                                coalesce(dp.seller_state, 'Missing') as delivery_state,
                                coalesce(dp.seller_district, 'Missing') as delivery_district,
                                COUNT(distinct dp.provider_key) AS total_active_sellers
                            FROM
                                {constant.SELLER_TABLE} dp
                            WHERE
                                 dp.order_date BETWEEN %s AND %s
                            GROUP BY
                                dp.order_date, dp.seller_state, dp.seller_district
                        )
                        SELECT
                            TO_CHAR(swdlo.order_date, 'YYYY-MM-DD') AS "Order Date",
                            coalesce(swdlo.delivery_state, 'Missing') AS "Delivery State",
                            coalesce(swdlo.delivery_district, 'Missing') AS "Delivery District",
                            SUM(swdlo.total_orders_delivered) AS "Confirmed Orders",
                            SUM(swdlo.total_items) AS "Total Confirmed Items",
                            ROUND(COALESCE(SUM(swdlo.total_items::numeric) / 
                            NULLIF(SUM(swdlo.total_orders_delivered::numeric), 0), 0), 2) AS "Average Items per Order",
                            ROUND(COALESCE(SUM(swdlo.intradistrict_orders::numeric) / 
                            NULLIF(SUM(swdlo.total_orders_delivered::numeric), 0) * 100, 0), 2) 
                            AS "Intradistrict Orders Percentage",
                            COALESCE(
                            CASE
                                WHEN ASel.total_active_sellers < 3 THEN 0
                                ELSE ASel.total_active_sellers
                            END, 0) AS "Total Active Sellers"
                        FROM
                            {constant.DISTRICT_TABLE} swdlo
                        LEFT JOIN
                            ActiveSellers ASel ON swdlo.order_date = ASel.order_date
                                               AND swdlo.delivery_state = ASel.delivery_state
                                               AND swdlo.delivery_district = ASel.delivery_district
                        WHERE
                            swdlo.order_date BETWEEN %s AND %s
                        GROUP BY
                            swdlo.order_date, swdlo.delivery_state, swdlo.delivery_district, ASel.total_active_sellers
                        ORDER BY
                            swdlo.order_date, swdlo.delivery_state, swdlo.delivery_district
                '''

        parameters = [start_date, end_date, start_date, end_date]

    elif tab_name and tab_name == 'Digital Voucher':
        query = f'''
                    select 
                        TO_CHAR(rvdlo.order_date, 'YYYY-MM-DD') AS "Order Date",
                        sum(rvdlo.total_orders_delivered) as "Confirmed Orders",
                        sum(rvdlo.total_items) as "Total Confirmed Items",
                        round(sum(rvdlo.total_items)::numeric/sum(rvdlo.total_orders_delivered)::numeric,2) 
                        as "Average Items per Order"
                    FROM {constant.RV_DISTRICT_TABLE} rvdlo 
                    WHERE
                        rvdlo.order_date BETWEEN %s AND %s
                        group by rvdlo.order_date 
                        order by rvdlo.order_date
                '''

        parameters = [start_date, end_date]

    connector.execute(query, tuple(parameters))
    df = pd.DataFrame(connector.fetchall(), columns=[desc[0] for desc in connector.description])

    download_table_col_reference = {
        'avg_items': 'Average Items per Order',
        'intradistrict': 'Intradistrict Orders Percentage',
        'intrastate': 'Intrastate Orders Percentage',
        'items': 'Total Confirmed Items',
        'orders': 'Confirmed Orders'
    }

    for col_name, col_label in download_table_col_reference.items():
        if col_label in df:
            df[col_label] = df[col_label].astype(float)

    return df


@log_function_call(ondcLogger)
def fetch_downloadable_data_logistics(connector, start_date, end_date, domain=None, tab_name=None):
    if tab_name and tab_name == 'State wise orders':
        query = f''' 
                     WITH DistrictAggregates AS (
                        SELECT
                            swdlo.order_date,
                            coalesce(swdlo.delivery_state, 'Missing') as delivery_state,
                            coalesce(swdlo.delivery_district, 'Missing') as delivery_district,
                            SUM(swdlo.total_orders_delivered) AS total_orders_in_district,
                            SUM(swdlo.total_items) AS total_items_in_district
                        FROM
                            {constant.LOGISTICS_DISTRICT_TABLE} swdlo
                        WHERE
                            swdlo.order_date BETWEEN %s AND %s 
                        GROUP BY
                            swdlo.order_date,
                            swdlo.delivery_state,
                            swdlo.delivery_district
                    ), RankedDistricts AS (
                        SELECT
                            order_date,
                            delivery_state,
                            delivery_district,
                            total_orders_in_district,
                            total_items_in_district,
                            ROW_NUMBER() OVER (
                                PARTITION BY order_date, delivery_state 
                                ORDER BY total_orders_in_district DESC
                            ) AS rank_in_state
                        FROM
                            DistrictAggregates
                    ), StateAggregates AS (
                        SELECT
                            DA.order_date,
                            coalesce(DA.delivery_state, 'Missing') as delivery_state,
                            SUM(DA.total_orders_in_district) AS "Statewide Confirmed Orders",
                            SUM(DA.total_items_in_district) AS "Statewide Total Confirmed Items",
                            ROUND(COALESCE(SUM(DA.total_items_in_district)::NUMERIC / 
                            NULLIF(SUM(DA.total_orders_in_district), 0), 0), 2) AS "Statewide Average Items per Order",
                            MAX(CASE WHEN DA.rank_in_state = 1 THEN DA.delivery_district END) 
                            AS "Most Ordering District",
                            MAX(CASE WHEN DA.rank_in_state = 1 THEN DA.total_orders_in_district END) 
                            AS "Most Orders in District"
                        FROM
                            RankedDistricts DA
                        GROUP BY
                            DA.order_date, DA.delivery_state
                    )
                    SELECT
                        TO_CHAR(SA.order_date, 'YYYY-MM-DD') AS "Order Date",
                        SA.delivery_state AS "Delivery State",
                        SA."Statewide Confirmed Orders" AS "Confirmed Orders",
                        SA."Statewide Average Items per Order" AS "Average Items per Order",
                        SA."Most Ordering District"
                    FROM 
                        StateAggregates SA
                    ORDER BY  
                        SA.order_date, SA.delivery_state;

                '''
        parameters = [start_date, end_date]

    elif tab_name and tab_name == 'District wise orders':
        query = f''' 
                      SELECT 
                        TO_CHAR(swdlo.order_date, 'YYYY-MM-DD') AS "Order Date",
                        coalesce(swdlo.delivery_state, 'Missing') AS "Delivery State",
                        coalesce(swdlo.delivery_district, 'Missing') AS "Delivery District",
                        SUM(swdlo.total_orders_delivered) AS "Confirmed Orders",
                        SUM(swdlo.total_items) AS "Total Confirmed Items",
                        ROUND(COALESCE(SUM(swdlo.total_items::numeric) / 
                        NULLIF(SUM(swdlo.total_orders_delivered::numeric), 0), 0), 2) AS "Average Items per Order"
                    FROM 
                        {constant.LOGISTICS_DISTRICT_TABLE} swdlo 
                    WHERE 
                        swdlo.order_date BETWEEN %s AND %s 
                    GROUP BY 
                        swdlo.order_date, swdlo.delivery_state, swdlo.delivery_district 
                    ORDER BY  
                        swdlo.order_date, swdlo.delivery_state, swdlo.delivery_district;
                '''

        parameters = [start_date, end_date]


    connector.execute(query, tuple(parameters))
    df = pd.DataFrame(connector.fetchall(), columns=[desc[0] for desc in connector.description])

    for col_name, col_label in constant.download_table_col_reference.items():
        if col_label in df:
            df[col_label] = df[col_label].astype(float)

    return df


@log_function_call(ondcLogger)
def fetch_downloadable_data_b2b(connector, start_date, end_date, domain=None, tab_name=None):
    if tab_name and tab_name == 'State wise orders':
        query = f''' 
                     WITH DistrictAggregates AS (
                        SELECT
                            swdlo.order_date,
                            coalesce(swdlo.delivery_state, 'Missing') as delivery_state,
                            coalesce(swdlo.delivery_district, 'Missing') as delivery_district,
                            SUM(swdlo.total_orders_delivered) AS total_orders_in_district,
                            SUM(swdlo.total_items) AS total_items_in_district
                        FROM
                            {constant.B2B_DISTRICT_TABLE} swdlo
                        WHERE
                            swdlo.order_date BETWEEN %s AND %s 
                        GROUP BY
                            swdlo.order_date,
                            swdlo.delivery_state,
                            swdlo.delivery_district
                    ), RankedDistricts AS (
                        SELECT
                            order_date,
                            delivery_state,
                            delivery_district,
                            total_orders_in_district,
                            total_items_in_district,
                            ROW_NUMBER() OVER (
                                PARTITION BY order_date, delivery_state 
                                ORDER BY total_orders_in_district DESC
                            ) AS rank_in_state
                        FROM
                            DistrictAggregates
                    ), StateAggregates AS (
                        SELECT
                            DA.order_date,
                            coalesce(DA.delivery_state, 'Missing') as delivery_state,
                            SUM(DA.total_orders_in_district) AS "Statewide Confirmed Orders",
                            SUM(DA.total_items_in_district) AS "Statewide Total Confirmed Items",
                            ROUND(COALESCE(SUM(DA.total_items_in_district)::NUMERIC / 
                            NULLIF(SUM(DA.total_orders_in_district), 0), 0), 2) AS "Statewide Average Items per Order",
                            MAX(CASE WHEN DA.rank_in_state = 1 THEN DA.delivery_district END) 
                            AS "Most Ordering District",
                            MAX(CASE WHEN DA.rank_in_state = 1 THEN DA.total_orders_in_district END) 
                            AS "Most Orders in District"
                        FROM
                            RankedDistricts DA
                        GROUP BY
                            DA.order_date, DA.delivery_state
                    )
                    SELECT
                        TO_CHAR(SA.order_date, 'YYYY-MM-DD') AS "Order Date",
                        SA.delivery_state AS "Delivery State",
                        SA."Statewide Confirmed Orders" AS "Confirmed Orders",
                        SA."Statewide Average Items per Order" AS "Average Items per Order",
                        SA."Most Ordering District"
                    FROM 
                        StateAggregates SA
                    ORDER BY  
                        SA.order_date, SA.delivery_state;

                '''
        parameters = [start_date, end_date]

    elif tab_name and tab_name == 'District wise orders':
        query = f''' 
                      SELECT 
                        TO_CHAR(swdlo.order_date, 'YYYY-MM-DD') AS "Order Date",
                        coalesce(swdlo.delivery_state, 'Missing') AS "Delivery State",
                        coalesce(swdlo.delivery_district, 'Missing') AS "Delivery District",
                        SUM(swdlo.total_orders_delivered) AS "Confirmed Orders",
                        SUM(swdlo.total_items) AS "Total Confirmed Items",
                        ROUND(COALESCE(SUM(swdlo.total_items::numeric) / 
                        NULLIF(SUM(swdlo.total_orders_delivered::numeric), 0), 0), 2) AS "Average Items per Order"
                    FROM 
                        {constant.B2B_DISTRICT_TABLE} swdlo 
                    WHERE 
                        swdlo.order_date BETWEEN %s AND %s 
                    GROUP BY 
                        swdlo.order_date, swdlo.delivery_state, swdlo.delivery_district 
                    ORDER BY  
                        swdlo.order_date, swdlo.delivery_state, swdlo.delivery_district;
                '''

        parameters = [start_date, end_date]


    connector.execute(query, tuple(parameters))
    df = pd.DataFrame(connector.fetchall(), columns=[desc[0] for desc in connector.description])

    for col_name, col_label in constant.download_table_col_reference.items():
        if col_label in df:
            df[col_label] = df[col_label].astype(float)

    return df


@log_function_call(ondcLogger)
def fetch_downloadable_data_overall(connector, start_date, end_date, domain=None, tab_name=None):
    # table_name = constant.MONTHLY_PROVIDERS
    stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
    edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

    # Extract month and year
    start_month = stdate_obj.month
    end_month = edate_obj.month
    start_year = stdate_obj.year
    end_year = edate_obj.year

    if tab_name and tab_name == 'State wise orders':
        query = f'''
                    WITH DistrictRanking AS (
                        SELECT
                            swdlo.order_year,
                            swdlo.order_month,
                            trim(to_char(make_date(swdlo.order_year::int, swdlo.order_month::int, 1), 'Month')) || '-' || swdlo.order_year AS order_date,
                            coalesce(swdlo.delivery_state, 'Missing') as delivery_state,
                            coalesce(swdlo.delivery_district, 'Missing') as delivery_district,
                            SUM(swdlo.total_orders_delivered) AS total_orders_in_district,
                            ROW_NUMBER() OVER (PARTITION BY swdlo.delivery_state, swdlo.order_year, swdlo.order_month
                            ORDER BY SUM(swdlo.total_orders_delivered) DESC) AS rank_in_state
                        FROM
                            {constant.MONTHLY_DISTRICT_TABLE} swdlo
                        WHERE
                            (swdlo.order_year > %s OR (swdlo.order_year = %s AND swdlo.order_month >= %s))
                            AND (swdlo.order_year < %s OR (swdlo.order_year = %s AND swdlo.order_month <= %s))
                            AND swdlo.domain_name = 'Retail' 
                            AND swdlo.sub_domain in ('B2B', 'B2C')
                        GROUP BY
                            swdlo.order_year, 
                            swdlo.order_month,
                            swdlo.delivery_state,
                            swdlo.delivery_district
                    ),
                    ActiveSellers AS (
                        SELECT 
                            ds.order_year,
                            ds.order_month,
                            trim(to_char(make_date(ds.order_year::int, ds.order_month::int, 1), 'Month')) || '-' || ds.order_year AS order_date,                          
                            coalesce(ds.seller_state, 'Missing') AS delivery_state,
                            COUNT(DISTINCT trim(lower(ds.provider_key))) AS total_active_sellers
                        FROM
                            {constant.MONTHLY_PROVIDERS} ds
                        WHERE
                            (ds.order_year > %s OR (ds.order_year = %s AND ds.order_month >= %s))
                            AND (ds.order_year < %s OR (ds.order_year = %s AND ds.order_month <= %s))
                        GROUP BY
                            ds.order_year,
                            ds.order_month, ds.seller_state
                    ),
                    AggregatedData AS (
                        SELECT 
                            swdlo.order_year,
                            swdlo.order_month,  
                            trim(to_char(make_date(swdlo.order_year::int, swdlo.order_month::int, 1), 'Month')) || '-' || swdlo.order_year AS "Order Date",                          
                            coalesce(swdlo.delivery_state, 'Missing') AS "Delivery State",
                            COUNT(DISTINCT swdlo.delivery_district) AS "Total Districts",
                            SUM(swdlo.total_orders_delivered) AS "Delivered Orders",
                            ROUND(COALESCE(100 * SUM(swdlo.intrastate_orders::numeric) / 
                            NULLIF(SUM(swdlo.total_orders_delivered::numeric), 0), 0), 2) 
                            AS "Intrastate Orders Percentage"
                        FROM
                            {constant.MONTHLY_DISTRICT_TABLE} swdlo
                        WHERE
                            (swdlo.order_year > %s OR (swdlo.order_year = %s AND swdlo.order_month >= %s))
                            AND (swdlo.order_year < %s OR (swdlo.order_year = %s AND swdlo.order_month <= %s))
                            AND swdlo.domain_name = 'Retail' 
                            AND swdlo.sub_domain in ('B2B', 'B2C')
                        GROUP BY
                            swdlo.order_year,
                            swdlo.order_month, swdlo.delivery_state
                    )
                    SELECT
                        AD."Order Date",
                        AD."Delivery State",
                        AD."Total Districts",
                        AD."Delivered Orders" as "Confirmed Orders",
                        AD."Intrastate Orders Percentage",
                        COALESCE(
                            CASE
                                WHEN ASel.total_active_sellers < 3 THEN 0
                                ELSE ASel.total_active_sellers
                            END, 0) AS "Total Active Sellers",
                        DR.delivery_district AS "Most Ordering District"
                    FROM
                        AggregatedData AD
                    LEFT JOIN
                        ActiveSellers ASel ON coalesce(AD."Delivery State", 'Missing') = coalesce(ASel.delivery_state, 'Missing') 
                        AND AD."Order Date" = ASel.order_date
                    LEFT JOIN
                        (SELECT * FROM DistrictRanking WHERE rank_in_state = 1) DR 
                        ON AD."Delivery State" = DR.delivery_state AND AD."Order Date" = DR.order_date
                    ORDER BY "Order Date", AD."Delivery State"
                '''
        parameters = [start_year, start_year, start_month, end_year, end_year, end_month,
                      start_year, start_year, start_month, end_year, end_year, end_month,
                      start_year, start_year, start_month, end_year, end_year, end_month]




    elif tab_name and tab_name == 'District wise orders':

        query = f'''

                       WITH ActiveSellers AS (

                            SELECT

                                dp.order_year,

                                dp.order_month,  

                                trim(to_char(make_date(dp.order_year::int, dp.order_month::int, 1), 'Month')) || '-' || dp.order_year AS order_date,

                                coalesce(dp.seller_state, 'Missing') as delivery_state,

                                coalesce(dp.seller_district, 'Missing') as delivery_district,

                                COUNT(distinct dp.provider_key) AS total_active_sellers

                            FROM

                                {constant.MONTHLY_PROVIDERS} dp

                            WHERE

                                (dp.order_year > %s OR (dp.order_year = %s AND dp.order_month >= %s))

                                AND (dp.order_year < %s OR (dp.order_year = %s AND dp.order_month <= %s))

                            GROUP BY

                                dp.order_year,

                                dp.order_month,  order_date, dp.seller_state, dp.seller_district

                        )

                        SELECT

                            trim(to_char(make_date(swdlo.order_year::int, swdlo.order_month::int, 1), 'Month')) || '-' || swdlo.order_year AS "Order Date",

                            coalesce(swdlo.delivery_state, 'Missing') AS "Delivery State",

                            coalesce(swdlo.delivery_district, 'Missing') AS "Delivery District",

                            SUM(swdlo.total_orders_delivered) AS "Confirmed Orders",

                            ROUND(COALESCE(SUM(swdlo.intradistrict_orders::numeric) / 

                            NULLIF(SUM(swdlo.total_orders_delivered::numeric), 0) * 100, 0), 2) 

                            AS "Intradistrict Orders Percentage",

                            COALESCE(

                            CASE

                                WHEN ASel.total_active_sellers < {constant.ACTIVE_SELLERS_MASKING} THEN 0

                                ELSE ASel.total_active_sellers

                            END, 0) AS "Total Active Sellers"

                        FROM

                            {constant.MONTHLY_DISTRICT_TABLE} swdlo

                        LEFT JOIN

                            ActiveSellers ASel ON swdlo.order_month = ASel.order_month

                                                AND swdlo.order_year = ASel.order_year

                                               AND swdlo.delivery_state = ASel.delivery_state

                                               AND swdlo.delivery_district = ASel.delivery_district

                        WHERE

                            (swdlo.order_year > %s OR (swdlo.order_year = %s AND swdlo.order_month >= %s))

                            AND (swdlo.order_year < %s OR (swdlo.order_year = %s AND swdlo.order_month <= %s))

                            AND swdlo.domain_name = 'Retail' 

                            AND swdlo.sub_domain in ('B2B', 'B2C')

                        GROUP BY

                            "Order Date", swdlo.delivery_state, swdlo.delivery_district, ASel.total_active_sellers

                        ORDER BY

                            "Order Date", swdlo.delivery_state, swdlo.delivery_district

                '''

        parameters = [start_year, start_year, start_month, end_year, end_year, end_month,

                      start_year, start_year, start_month, end_year, end_year, end_month]


    elif tab_name and tab_name == 'Digital Voucher':

        query = f'''

                    SELECT 

                        trim(to_char(make_date(rvdlo.order_year::int, rvdlo.order_month::int, 1), 'Month')) || '-' || rvdlo.order_year AS "Order Date",

                        sum(rvdlo.total_orders_delivered) as "Confirmed Orders"

                    FROM {constant.MONTHLY_DISTRICT_TABLE} rvdlo 

                    WHERE

                        (rvdlo.order_year > %s OR (rvdlo.order_year = %s AND rvdlo.order_month >= %s))

                        AND (rvdlo.order_year < %s OR (rvdlo.order_year = %s AND rvdlo.order_month <= %s))

                        AND rvdlo.domain_name = 'Retail' 

                        AND rvdlo.sub_domain = 'Voucher'

                    GROUP BY "Order Date"

                    ORDER BY "Order Date"

                '''

        parameters = [start_year, start_year, start_month, end_year, end_year, end_month]

    connector.execute(query, tuple(parameters))
    df = pd.DataFrame(connector.fetchall(), columns=[desc[0] for desc in connector.description])

    download_table_col_reference = {
        'avg_items': 'Average Items per Order',
        'intradistrict': 'Intradistrict Orders Percentage',
        'intrastate': 'Intrastate Orders Percentage',
        'items': 'Total Confirmed Items',
        'orders': 'Confirmed Orders'
    }

    for col_name, col_label in download_table_col_reference.items():
        if col_label in df:
            df[col_label] = df[col_label].astype(float)

    return df


@log_function_call(ondcLogger)
def fetch_downloadable_data_logistics_overall(connector, start_date, end_date, domain=None, tab_name=None):
    # table_name = constant.MONTHLY_PROVIDERS
    stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
    edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

    # Extract month and year
    start_month = stdate_obj.month
    end_month = edate_obj.month
    start_year = stdate_obj.year
    end_year = edate_obj.year

    if tab_name and tab_name == 'State wise orders':
        query = f'''
                    WITH DistrictRanking AS (
                        SELECT
                            swdlo.order_year,
                            swdlo.order_month,
                            trim(to_char(make_date(swdlo.order_year::int, swdlo.order_month::int, 1), 'Month')) || '-' || swdlo.order_year AS order_date,
                            coalesce(swdlo.delivery_state, 'Missing') as delivery_state,
                            coalesce(swdlo.delivery_district, 'Missing') as delivery_district,
                            SUM(swdlo.total_orders_delivered) AS total_orders_in_district,
                            ROW_NUMBER() OVER (PARTITION BY swdlo.delivery_state, swdlo.order_year, swdlo.order_month
                            ORDER BY SUM(swdlo.total_orders_delivered) DESC) AS rank_in_state
                        FROM
                            {constant.MONTHLY_DISTRICT_TABLE} swdlo
                        WHERE
                            (swdlo.order_year > %s OR (swdlo.order_year = %s AND swdlo.order_month >= %s))
                            AND (swdlo.order_year < %s OR (swdlo.order_year = %s AND swdlo.order_month <= %s))
                            AND swdlo.domain_name = 'Logistics' 
                        GROUP BY
                            swdlo.order_year, 
                            swdlo.order_month,
                            swdlo.delivery_state,
                            swdlo.delivery_district
                    ),
                    ActiveSellers AS (
                        SELECT 
                            ds.order_year,
                            ds.order_month,
                            trim(to_char(make_date(ds.order_year::int, ds.order_month::int, 1), 'Month')) || '-' || ds.order_year AS order_date,                          
                            coalesce(ds.seller_state, 'Missing') AS delivery_state,
                            COUNT(DISTINCT trim(lower(ds.provider_key))) AS total_active_sellers
                        FROM
                            {constant.LOGISTICS_MONTHLY_PROVIDERS} ds
                        WHERE
                            (ds.order_year > %s OR (ds.order_year = %s AND ds.order_month >= %s))
                            AND (ds.order_year < %s OR (ds.order_year = %s AND ds.order_month <= %s))
                        GROUP BY
                            ds.order_year,
                            ds.order_month, ds.seller_state
                    ),
                    AggregatedData AS (
                        SELECT 
                            swdlo.order_year,
                            swdlo.order_month,  
                            trim(to_char(make_date(swdlo.order_year::int, swdlo.order_month::int, 1), 'Month')) || '-' || swdlo.order_year AS "Order Date",                          
                            coalesce(swdlo.delivery_state, 'Missing') AS "Delivery State",
                            COUNT(DISTINCT swdlo.delivery_district) AS "Total Districts",
                            SUM(swdlo.total_orders_delivered) AS "Delivered Orders",
                            ROUND(COALESCE(100 * SUM(swdlo.intrastate_orders::numeric) / 
                            NULLIF(SUM(swdlo.total_orders_delivered::numeric), 0), 0), 2) 
                            AS "Intrastate Orders Percentage"
                        FROM
                            {constant.MONTHLY_DISTRICT_TABLE} swdlo
                        WHERE
                            (swdlo.order_year > %s OR (swdlo.order_year = %s AND swdlo.order_month >= %s))
                            AND (swdlo.order_year < %s OR (swdlo.order_year = %s AND swdlo.order_month <= %s))
                            AND swdlo.domain_name = 'Logistics' 
                        GROUP BY
                            swdlo.order_year,
                            swdlo.order_month, swdlo.delivery_state
                    )
                    SELECT
                        AD."Order Date",
                        AD."Delivery State",
                        AD."Total Districts",
                        AD."Delivered Orders" as "Confirmed Orders",
                        AD."Intrastate Orders Percentage",
                        COALESCE(
                            CASE
                                WHEN ASel.total_active_sellers < 3 THEN 0
                                ELSE ASel.total_active_sellers
                            END, 0) AS "Total Active Sellers",
                        DR.delivery_district AS "Most Ordering District"
                    FROM
                        AggregatedData AD
                    LEFT JOIN
                        ActiveSellers ASel ON coalesce(AD."Delivery State", 'Missing') = coalesce(ASel.delivery_state, 'Missing') 
                        AND AD."Order Date" = ASel.order_date
                    LEFT JOIN
                        (SELECT * FROM DistrictRanking WHERE rank_in_state = 1) DR 
                        ON AD."Delivery State" = DR.delivery_state AND AD."Order Date" = DR.order_date
                    ORDER BY "Order Date", AD."Delivery State"
                '''
        parameters = [start_year, start_year, start_month, end_year, end_year, end_month,
                      start_year, start_year, start_month, end_year, end_year, end_month,
                      start_year, start_year, start_month, end_year, end_year, end_month]




    elif tab_name and tab_name == 'District wise orders':

        query = f'''

                       WITH ActiveSellers AS (

                            SELECT

                                dp.order_year,

                                dp.order_month,  

                                trim(to_char(make_date(dp.order_year::int, dp.order_month::int, 1), 'Month')) || '-' || dp.order_year AS order_date,

                                coalesce(dp.seller_state, 'Missing') as delivery_state,

                                coalesce(dp.seller_district, 'Missing') as delivery_district,

                                COUNT(distinct dp.provider_key) AS total_active_sellers

                            FROM

                                {constant.LOGISTICS_MONTHLY_PROVIDERS} dp

                            WHERE

                                (dp.order_year > %s OR (dp.order_year = %s AND dp.order_month >= %s))

                                AND (dp.order_year < %s OR (dp.order_year = %s AND dp.order_month <= %s))

                            GROUP BY

                                dp.order_year,

                                dp.order_month,  order_date, dp.seller_state, dp.seller_district

                        )

                        SELECT

                            trim(to_char(make_date(swdlo.order_year::int, swdlo.order_month::int, 1), 'Month')) || '-' || swdlo.order_year AS "Order Date",

                            coalesce(swdlo.delivery_state, 'Missing') AS "Delivery State",

                            coalesce(swdlo.delivery_district, 'Missing') AS "Delivery District",

                            SUM(swdlo.total_orders_delivered) AS "Confirmed Orders",

                            ROUND(COALESCE(SUM(swdlo.intradistrict_orders::numeric) / 

                            NULLIF(SUM(swdlo.total_orders_delivered::numeric), 0) * 100, 0), 2) 

                            AS "Intradistrict Orders Percentage",

                            COALESCE(

                            CASE

                                WHEN ASel.total_active_sellers < {constant.ACTIVE_SELLERS_MASKING} THEN 0

                                ELSE ASel.total_active_sellers

                            END, 0) AS "Total Active Sellers"

                        FROM

                            {constant.MONTHLY_DISTRICT_TABLE} swdlo

                        LEFT JOIN

                            ActiveSellers ASel ON swdlo.order_month = ASel.order_month

                                                AND swdlo.order_year = ASel.order_year

                                               AND swdlo.delivery_state = ASel.delivery_state

                                               AND swdlo.delivery_district = ASel.delivery_district

                        WHERE

                            (swdlo.order_year > %s OR (swdlo.order_year = %s AND swdlo.order_month >= %s))

                            AND (swdlo.order_year < %s OR (swdlo.order_year = %s AND swdlo.order_month <= %s))

                            AND swdlo.domain_name = 'Logistics' 


                        GROUP BY

                            "Order Date", swdlo.delivery_state, swdlo.delivery_district, ASel.total_active_sellers

                        ORDER BY

                            "Order Date", swdlo.delivery_state, swdlo.delivery_district

                '''

        parameters = [start_year, start_year, start_month, end_year, end_year, end_month,

                      start_year, start_year, start_month, end_year, end_year, end_month]



    connector.execute(query, tuple(parameters))
    df = pd.DataFrame(connector.fetchall(), columns=[desc[0] for desc in connector.description])

    download_table_col_reference = {
        'avg_items': 'Average Items per Order',
        'intradistrict': 'Intradistrict Orders Percentage',
        'intrastate': 'Intrastate Orders Percentage',
        'items': 'Total Confirmed Items',
        'orders': 'Confirmed Orders'
    }

    for col_name, col_label in download_table_col_reference.items():
        if col_label in df:
            df[col_label] = df[col_label].astype(float)

    return df


@log_function_call(ondcLogger)
def get_max_state_sellers(connector, start_date, end_date, state=None, category=None, sub_category=None):

    selected_view = constant.SELLER_TABLE

    params = [start_date, end_date]

    query = f"""
        SELECT 
            'State' AS record_type,
            seller_state as location,
            order_date,
            seller_count
        FROM 
            (
                SELECT
                    seller_state,
                    order_date,
                    COUNT(DISTINCT trim(lower(provider_key))) AS seller_count,
                    RANK() OVER (PARTITION BY seller_state ORDER BY COUNT(DISTINCT provider_key) DESC) AS rank
                FROM
                    {selected_view}
                WHERE 
                    order_date BETWEEN %s AND %s
                    and seller_state <> ''
    """

    if state:
        query += constant.seller_state_sub_query
        params.append(state)

    if category and category != 'None':
        query += constant.category_sub_query
        params.append(category)

    if sub_category and sub_category != 'None':
        query += constant.sub_category_sub_query
        params.append(sub_category)

    query += f"""
                GROUP BY
                    seller_state, order_date
                HAVING COUNT(DISTINCT provider_key) > {constant.ACTIVE_SELLERS_MASKING} 
                ORDER BY
                    seller_state, rank, order_date
            ) AS RankedOrders
        WHERE 
            rank = 1
        ORDER BY 
            seller_count DESC
        LIMIT 1
    """

    connector.execute(query, tuple(params))
    df = pd.DataFrame(connector.fetchall(), columns=[desc[0] for desc in connector.description])
    return df


@log_function_call(ondcLogger)
def get_max_district_sellers(connector, start_date, end_date, state=None, category=None, sub_category=None):

    selected_view = constant.SELLER_TABLE
    params = [start_date, end_date]

    query = f"""
            SELECT 
                'District' AS record_type,
                seller_district as location,
                order_date,
                seller_count
            FROM 
                (
                    SELECT
                        seller_district,
                        order_date,
                        COUNT(DISTINCT provider_key) AS seller_count,
                        RANK() OVER (PARTITION BY seller_district ORDER BY COUNT(DISTINCT provider_key) DESC) AS rank
                    FROM
                        {selected_view}
                    WHERE 
                        order_date BETWEEN %s AND %s
                        and seller_district <> '' and upper(seller_district) <> upper('Undefined')
        """

    if state:
        query += constant.seller_state_sub_query
        params.append(state)

    if category and category != 'None':
        query += constant.category_sub_query
        params.append(category)

    if sub_category and sub_category != 'None':
        query += constant.sub_category_sub_query
        params.append(sub_category)

    query += f"""
                    GROUP BY
                        seller_district, order_date
                    HAVING COUNT(DISTINCT provider_key) > {constant.ACTIVE_SELLERS_MASKING}
                    ORDER BY
                        seller_district, rank, order_date
                ) AS RankedOrders
            WHERE 
                rank = 1
            ORDER BY 
                seller_count DESC
            LIMIT 1
        """

    connector.execute(query, tuple(params))
    df = pd.DataFrame(connector.fetchall(), columns=[desc[0] for desc in connector.description])
    return df

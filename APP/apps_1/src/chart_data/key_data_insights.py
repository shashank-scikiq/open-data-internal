import pandas as pd
import os
from apps.logging_conf import log_function_call, ondcLogger

DISTRICT_TABLE = os.environ.get("DISTRICT_TABLE")
SUB_CATEGORY_TABLE = os.environ.get("SUB_CATEGORY_TABLE")
CATEGORY_TABLE = os.environ.get("CATEGORY_TABLE")

KEY_DATA_INSIGHTS_TABLE = os.environ.get("KEY_DATA_INSIGHTS_TABLE")
KEY_INSIGHTS_SUB_CATEGORY_TABLE = os.environ.get("KEY_INSIGHTS_SUB_CATEGORY_TABLE")
KEY_INSIGHTS_SELLER = os.environ.get("KEY_INSIGHTS_SELLER")

KDI_CURRENT_ORDERS_THRESHOLD = os.environ.get("KDI_CURRENT_ORDERS_THRESHOLD")


@log_function_call(ondcLogger)
def fetch_max_gain_by_state(connector):
    query = f'''  
                WITH state_aggregates AS (
                    SELECT
                        delivery_state,
                        max(current_period) as current_period,
                        max(prev_period) as prev_period,
                        SUM(current_mtd_demand) AS current_demand,
                        SUM(prev_mtd_demand) AS prev_demand
                    FROM {os.getenv("POSTGRES_SCHEMA")}.{os.getenv("KEY_DATA_INSIGHTS_TABLE")}
                    GROUP BY delivery_state
                    HAVING SUM(current_mtd_demand) > {KDI_CURRENT_ORDERS_THRESHOLD}
                    ),
                    gain_calculations AS (
                    SELECT
                        delivery_state,
                        current_period,
                        prev_period,
                        round(COALESCE( round((current_demand - prev_demand) / NULLIF(prev_demand, 0) * 100, 2), 0),2) 
                        AS total_gain_percent
                    FROM state_aggregates
                    )
                    SELECT delivery_state, current_period, prev_period, total_gain_percent
                    FROM gain_calculations
                    ORDER BY total_gain_percent DESC
                    LIMIT 1;

            '''

    connector.execute(query)
    df = pd.DataFrame(connector.fetchall(), columns=[desc[0] for desc in connector.description])
    return df


@log_function_call(ondcLogger)
def fetch_max_gain_by_subcategory(connector):
    query = f'''

            select upper(sub_category) as sub_category,
                current_period,
                prev_period,
                gain_percent
                from {os.getenv("POSTGRES_SCHEMA")}.{os.getenv("KEY_INSIGHTS_SUB_CATEGORY_TABLE")}
                where current_mtd_demand > {KDI_CURRENT_ORDERS_THRESHOLD}
                order by gain_percent desc
                limit 1


            '''

    connector.execute(query)
    df = pd.DataFrame(connector.fetchall(), columns=[desc[0] for desc in connector.description])
    return df


@log_function_call(ondcLogger)
def fetch_max_gain_by_district(connector):
    query = f'''

             WITH state_aggregates AS (
                SELECT
                    delivery_district,
                    MAX(current_period) as current_period,
                    MAX(prev_period) as prev_period,
                    SUM(current_mtd_demand) AS current_demand,
                    SUM(prev_mtd_demand) AS prev_demand
                FROM {os.getenv("POSTGRES_SCHEMA")}.{os.getenv("KEY_DATA_INSIGHTS_TABLE")}
                GROUP BY delivery_district
                HAVING SUM(current_mtd_demand) > {KDI_CURRENT_ORDERS_THRESHOLD}
                ),
                gain_calculations AS (
                SELECT
                    delivery_district,
                    current_period,
                    prev_period,
                    round(coalesce(round((current_demand - prev_demand) / NULLIF(prev_demand, 0) * 100,2),0),2) 
                    AS total_gain_percent
                FROM state_aggregates
                )
                SELECT upper(delivery_district) as delivery_district, current_period, prev_period, total_gain_percent
                FROM gain_calculations
                WHERE delivery_district is not null 
                ORDER BY total_gain_percent DESC
                LIMIT 1;


        '''
    # print(query)
    connector.execute(query)
    df = pd.DataFrame(connector.fetchall(), columns=[desc[0] for desc in connector.description])
    # print(df)
    return df


@log_function_call(ondcLogger)
def fetch_max_gain_by_district_weekwise(connector):
    query = f'''
        WITH state_aggregates AS (
            SELECT
                delivery_district,
                MAX(current_wtd_period) as current_period,
                MAX(prev_wtd_period) as prev_period,
                SUM(current_wtd_intradistrict) AS current_intradistrict,
                SUM(prev_wtd_intradistrict) AS prev_intradistrict
            FROM {os.getenv("POSTGRES_SCHEMA")}.{os.getenv("KEY_DATA_INSIGHTS_TABLE")}
            GROUP BY delivery_district
            HAVING SUM(current_mtd_demand) > {KDI_CURRENT_ORDERS_THRESHOLD}
            ),
            gain_calculations AS (
            SELECT
                delivery_district,
                current_period,
                prev_period,
                round(coalesce((current_intradistrict - prev_intradistrict) / NULLIF(prev_intradistrict, 0) * 100, 2),2) 
                AS intradistrict_gain_percent
            FROM state_aggregates
            )
            SELECT upper(delivery_district) as delivery_district, 
            current_period,
            prev_period,
            intradistrict_gain_percent
            FROM gain_calculations
            WHERE delivery_district is not null 
            ORDER BY intradistrict_gain_percent DESC
            LIMIT 1;

    '''

    connector.execute(query)
    df = pd.DataFrame(connector.fetchall(), columns=[desc[0] for desc in connector.description])
    return df


@log_function_call(ondcLogger)
def fetch_max_intrastate_gain_by_state(connector):
    query = f'''
    WITH state_aggregates AS (
        SELECT
            delivery_state,
            MAX(current_period) as current_period,
            MAX(prev_period) as prev_period,
            SUM(current_mtd_intrastate) AS current_intrastate,
            SUM(prev_mtd_intrastate) AS prev_intrastate
        FROM {os.getenv("POSTGRES_SCHEMA")}.{os.getenv("KEY_DATA_INSIGHTS_TABLE")}
        GROUP BY delivery_state
        HAVING SUM(current_mtd_demand) > {KDI_CURRENT_ORDERS_THRESHOLD}
        ),
        gain_calculations AS (
        SELECT
            delivery_state,
            current_period,
            prev_period,
            round(coalesce( round((current_intrastate - prev_intrastate) / NULLIF(prev_intrastate, 0) * 100, 2),0),2)
             AS intrastate_gain_percent
        FROM state_aggregates
        )
        SELECT upper(delivery_state) as delivery_state, current_period, prev_period, intrastate_gain_percent
        FROM gain_calculations
        WHERE delivery_state is not null
        ORDER BY intrastate_gain_percent DESC
        LIMIT 1;
    '''

    connector.execute(query)
    df = pd.DataFrame(connector.fetchall(), columns=[desc[0] for desc in connector.description])
    return df


@log_function_call(ondcLogger)
def fetch_sellers_perc_with_orders(connector):
    query = f'''
        select * from {KEY_INSIGHTS_SELLER}

    '''

    connector.execute(query)
    df = pd.DataFrame(connector.fetchall(), columns=[desc[0] for desc in connector.description])
    return df


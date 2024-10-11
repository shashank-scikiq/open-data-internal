__author__ = "Shashank Katyayan"

from datetime import datetime
import json
from apps.logging_conf import log_function_call, ondcLogger
from decimal import getcontext
from apps.utils import constant

getcontext().prec = 4


class DotDict(dict):
    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, attr, value):
        self[attr] = value

    def __delattr__(self, attr):
        del self[attr]


class DataAccessLayer:

    def __init__(self, db_utility):
        self.db_utility = db_utility

    def get_query_month_parameters(self, start_date, end_date):
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        start_month = stdate_obj.month
        start_year = stdate_obj.year
        end_month = edate_obj.month
        end_year = edate_obj.year

        parameters = {
            'start_month': start_month,
            'start_year': start_year,
            'end_month': end_month,
            'end_year': end_year
        }
        return parameters
    
    @log_function_call(ondcLogger)
    def fetch_total_orders_summary(self, start_date, end_date, category=None,
                                   sub_category=None, domain=None, sub_domain=None, state=None):
        domain = 'Retail' if domain is None else domain
        sub_domain = 'B2B' if sub_domain is None else sub_domain

        table_name = constant.MONTHLY_DISTRICT_TABLE
        parameters = self.get_query_month_parameters(start_date, end_date)

        query = """
            WITH DistrictRanking AS (
                SELECT
                    delivery_state AS delivery_state_code,
                    delivery_state,
                    delivery_district,
                    SUM(total_orders_delivered) AS total_orders_in_district,
                    ROW_NUMBER() OVER (PARTITION BY delivery_state ORDER BY SUM(total_orders_delivered) DESC) AS rank_in_state
                FROM
                    {table_name}
                WHERE
                    (order_year > %(start_year)s OR (order_year = %(start_year)s AND order_month >= %(start_month)s))
                    AND (order_year < %(end_year)s OR (order_year = %(end_year)s AND order_month <= %(end_month)s))
                    AND delivery_state <> '' AND delivery_state IS NOT NULL
        """

        if domain:
            query += " AND domain_name = %(domain)s"
            parameters['domain'] = domain

        query += " AND sub_domain = %(sub_domain)s"
        parameters['sub_domain'] = sub_domain

        query += f"""
                GROUP BY
                    delivery_state, delivery_district
            ),
            ActiveSellers AS (
                SELECT
                    seller_state AS seller_state_code,
                    seller_state,
                    COUNT(DISTINCT TRIM(LOWER(provider_key))) AS total_active_sellers
                FROM
                    {constant.MONTHLY_PROVIDERS}
                WHERE
                    (order_year > %(start_year)s OR (order_year = %(start_year)s AND order_month >= %(start_month)s))
                    AND (order_year < %(end_year)s OR (order_year = %(end_year)s AND order_month <= %(end_month)s))
        """

        if state:
            query += " AND seller_state = %(state)s"
            parameters['state'] = state

        query += """
                GROUP BY
                    seller_state
            ),
            AggregatedData AS (
                SELECT
                    delivery_state_code AS delivery_state_code,
                    delivery_state AS delivery_state,
                    COUNT(DISTINCT CONCAT(delivery_state, '_', delivery_district)) as total_districts,
                    SUM(total_orders_delivered) AS delivered_orders
                FROM
                    {table_name}
                WHERE
                    (order_year > %(start_year)s OR (order_year = %(start_year)s AND order_month >= %(start_month)s))
                    AND (order_year < %(end_year)s OR (order_year = %(end_year)s AND order_month <= %(end_month)s))
                    AND delivery_state <> '' AND delivery_state IS NOT NULL
        """

        if domain:
            query += " AND domain_name = %(domain)s"
        
        query += " AND sub_domain = %(sub_domain)s"

        query += """
                GROUP BY
                    delivery_state_code, delivery_state
            ),
            StateRanking AS (
                SELECT
                    delivery_state_code AS delivery_state_code,
                    delivery_state,
                    SUM(total_orders_delivered) AS total_orders_in_state,
                    ROW_NUMBER() OVER (ORDER BY SUM(total_orders_delivered) DESC) AS rank_in_state
                FROM
                    {table_name}
                WHERE
                    (order_year > %(start_year)s OR (order_year = %(start_year)s AND order_month >= %(start_month)s))
                    AND (order_year < %(end_year)s OR (order_year = %(end_year)s AND order_month <= %(end_month)s))
                    AND delivery_state <> '' AND delivery_state_code IS NOT NULL
        """

        if domain:
            query += " AND domain_name = %(domain)s"
        
        query += " AND sub_domain = %(sub_domain)s"

        query += f"""
                GROUP BY
                    delivery_state_code,
                    delivery_state
            ),
            ActiveSellersTotal AS (
                SELECT
                    'TT' AS seller_state_code,
                    'TOTAL' AS seller_state,
                    COUNT(DISTINCT TRIM(LOWER(provider_key))) AS total_active_sellers
                FROM
                    {constant.MONTHLY_PROVIDERS}
                WHERE
                    (order_year > %(start_year)s OR (order_year = %(start_year)s AND order_month >= %(start_month)s))
                    AND (order_year < %(end_year)s OR (order_year = %(end_year)s AND order_month <= %(end_month)s))
            ),
            AggregatedDataTotal AS (
                SELECT
                    'TT' AS delivery_state_code,
                    'TOTAL' AS delivery_state,
                    COUNT(DISTINCT CONCAT(delivery_state, '_', delivery_district)) AS total_districts,
                    SUM(total_orders_delivered) AS delivered_orders
                FROM
                    {table_name}
                WHERE
                    (order_year > %(start_year)s OR (order_year = %(start_year)s AND order_month >= %(start_month)s))
                    AND (order_year < %(end_year)s OR (order_year = %(end_year)s AND order_month <= %(end_month)s))
            """

        if domain:
            query += " AND domain_name = %(domain)s"
            parameters['domain'] = domain
        
        query += " AND sub_domain = %(sub_domain)s"
        parameters['sub_domain'] = sub_domain

        query += """
            )
            SELECT
                COALESCE(AD.delivery_state_code, 'Missing') AS delivery_state_code,
                COALESCE(AD.delivery_state, 'Missing') AS delivery_state,
                AD.total_districts,
                AD.delivered_orders,
                COALESCE(ASel.total_active_sellers, 0) AS total_active_sellers,
                DR.delivery_district AS most_ordering_district
            FROM
                AggregatedData AD
            LEFT JOIN
                ActiveSellers ASel ON AD.delivery_state = ASel.seller_state
            LEFT JOIN
                (SELECT * FROM DistrictRanking WHERE rank_in_state = 1) DR ON AD.delivery_state = DR.delivery_state
            UNION ALL
            SELECT
                'TT' AS delivery_state_code,
                'TOTAL' AS delivery_state,
                ADT.total_districts,
                ADT.delivered_orders,
                COALESCE(ASelt.total_active_sellers, 0) AS total_active_sellers,
                SRnk.delivery_state AS most_ordering_district
            FROM
                AggregatedDataTotal ADT
            LEFT JOIN
                ActiveSellersTotal ASelt ON 1=1
            LEFT JOIN
                StateRanking SRnk ON SRnk.rank_in_state = 1
        """

        query = query.format(table_name=table_name)
        orders_count = self.db_utility.execute_query(query, parameters)
        return orders_count

    @log_function_call(ondcLogger)
    def fetch_total_orders_summary_prev(self, start_date, end_date, category=None,
                                        sub_category=None, domain=None, state=None):
        table_name = constant.MONTHLY_DISTRICT_TABLE
        parameters = self.get_query_month_parameters(start_date, end_date)

        query = f"""
            WITH ActiveSellers AS (
                SELECT
                    ds.seller_state AS seller_state_code,
                    ds.seller_state AS seller_state,
                    COUNT(DISTINCT TRIM(LOWER(ds.provider_key)))  AS total_active_sellers
                FROM
                    {constant.MONTHLY_PROVIDERS} ds
                WHERE
                    (ds.order_year > %(start_year)s OR (ds.order_year = %(start_year)s AND ds.order_month >= %(start_month)s))
                    AND (ds.order_year < %(end_year)s OR (ds.order_year = %(end_year)s AND ds.order_month <= %(end_month)s))
        """

        if state:
            query += " AND ds.seller_state = %(state)s"
            parameters['state'] = state

        query += f"""
                GROUP BY ds.seller_state, ds.seller_state_code
            ),
            AggregatedData AS (
                SELECT
                    swdlo.delivery_state_code AS delivery_state_code,
                    swdlo.delivery_state AS delivery_state,
                    COUNT(DISTINCT swdlo.delivery_district) AS total_districts,
                    SUM(swdlo.total_orders_delivered) AS delivered_orders
                FROM
                    {table_name} swdlo
                WHERE
                    (swdlo.order_year > %(start_year)s OR (swdlo.order_year = %(start_year)s AND swdlo.order_month >= %(start_month)s))
                    AND (swdlo.order_year < %(end_year)s OR (swdlo.order_year = %(end_year)s AND swdlo.order_month <= %(end_month)s))
                    AND swdlo.delivery_state <> '' AND swdlo.delivery_state IS NOT NULL and swdlo.domain_name = 'Retail' and swdlo.sub_domain = 'B2B'

                GROUP BY swdlo.delivery_state_code, swdlo.delivery_state
            ),
            ActiveSellersTotal AS (
                SELECT
                    'TT' AS seller_state_code,
                    'TOTAL' AS seller_state,
                    COUNT(DISTINCT TRIM(LOWER(ds.provider_key))) AS total_active_sellers
                FROM
                    {constant.MONTHLY_PROVIDERS} ds
                WHERE
                    (ds.order_year > %(start_year)s OR (ds.order_year = %(start_year)s AND ds.order_month >= %(start_month)s))
                    AND (ds.order_year < %(end_year)s OR (ds.order_year = %(end_year)s AND ds.order_month <= %(end_month)s))
            ),
            AggregatedDataTotal AS (
                SELECT
                    'TT' AS delivery_state_code,
                    'TOTAL' AS delivery_state,
                    COUNT(DISTINCT CONCAT(delivery_state, '_', delivery_district)) AS total_districts,
                    SUM(swdlo.total_orders_delivered) AS delivered_orders
                FROM
                    {table_name} swdlo
                WHERE
                    (swdlo.order_year > %(start_year)s OR (swdlo.order_year = %(start_year)s AND swdlo.order_month >= %(start_month)s))
                    AND (swdlo.order_year < %(end_year)s OR (swdlo.order_year = %(end_year)s AND swdlo.order_month <= %(end_month)s))
                    and swdlo.domain_name = 'Retail' and swdlo.sub_domain = 'B2B'
            )
            SELECT
                COALESCE(AD.delivery_state_code, 'Missing') AS delivery_state_code,
                COALESCE(AD.delivery_state, 'Missing') AS delivery_state,
                AD.total_districts,
                AD.delivered_orders,
                COALESCE(
                    CASE
                        WHEN ASel.total_active_sellers < 3 THEN 0
                        ELSE ASel.total_active_sellers
                    END, 0) AS total_active_sellers
            FROM
                AggregatedData AD
            LEFT JOIN
                ActiveSellers ASel ON AD.delivery_state = ASel.seller_state
            UNION ALL
            SELECT
                'TT' AS delivery_state_code,
                'TOTAL' AS delivery_state,
                ADT.total_districts,
                ADT.delivered_orders,
                COALESCE(
                    CASE
                        WHEN ASelt.total_active_sellers < 3 THEN 0
                        ELSE ASelt.total_active_sellers
                    END, 0) AS total_active_sellers
            FROM
                AggregatedDataTotal ADT
            LEFT JOIN
                ActiveSellersTotal ASelt ON 1=1
        """
        orders_count = self.db_utility.execute_query(query, parameters)
        return orders_count
    
    @log_function_call(ondcLogger)
    def fetch_cumulative_orders_statedata_summary(self, start_date, end_date,
                                                  category=None, sub_category=None,
                                                  domain=None, sub_domain=None, state=None):

        domain = 'Retail' if domain is None else domain
        sub_domain = 'B2B' if sub_domain is None else sub_domain

        params = DotDict(self.get_query_month_parameters(start_date, end_date))
        table_name = constant.MONTHLY_DISTRICT_TABLE
        query = f'''
            SELECT 
                delivery_state_code AS delivery_state_code,
                delivery_state AS delivery_state,
                delivery_district AS delivery_district,
                SUM(total_orders_delivered) AS total_orders_delivered,
                SUM(intradistrict_orders) AS intradistrict_orders,
                SUM(intrastate_orders) AS intrastate_orders
            FROM {table_name}
            WHERE 
                (order_year > %s OR (order_year = %s AND order_month >= %s))
                AND (order_year < %s OR (order_year = %s AND order_month <= %s))
        '''

        parameters = [params.start_year, params.start_year, params.start_month,
                      params.end_year, params.end_year, params.end_month]

        conditions = []

        if domain:
            conditions.append("AND domain_name = %s")
            parameters.append(domain)
        if sub_domain:
            conditions.append("AND sub_domain = %s")
            parameters.append(sub_domain)

        if state:
            conditions.append("AND upper(delivery_state) = upper(%s)")
            parameters.append(state)

        conditions_str = ' '.join(conditions)
        query = query + conditions_str + '''
            GROUP BY delivery_state_code, delivery_state, delivery_district 
            ORDER BY delivery_state_code, total_orders_delivered DESC
        '''

        aggregated_df = self.db_utility.execute_query(query, parameters)

        return aggregated_df
    
    @log_function_call(ondcLogger)
    def fetch_district_count(self, start_date, end_date,
                                                  category=None, sub_category=None,
                                                  domain=None, state=None):
        domain = 'Retail' if domain is None else domain

        params = DotDict(self.get_query_month_parameters(start_date, end_date))
        table_name = constant.MONTHLY_DISTRICT_TABLE
        query = f'''
                    SELECT 
                        delivery_state_code AS delivery_state_code,
                        delivery_state AS delivery_state,
                        count(distinct concat(delivery_state, delivery_district)) AS district_count
                    FROM {table_name}
                    WHERE 
                        (order_year = %s AND order_month = %s)
                    
                '''

        parameters = [params.end_year, params.end_month]

        if domain:
            query += " AND domain_name = %s AND sub_domain = 'B2B'"
            parameters.append(domain)
        query += " group by delivery_state_code, delivery_state"
        district_count = self.db_utility.execute_query(query, parameters)

        return district_count
    
    @log_function_call(ondcLogger)
    def fetch_cumulative_orders_statewise_summary(self, start_date, end_date,
                                                  category=None, sub_category=None, domain=None, state=None):
        domain = 'Retail' if domain is None else domain
        sub_domain = 'B2B'
        table_name = constant.MONTHLY_DISTRICT_TABLE
        params = DotDict(self.get_query_month_parameters(start_date, end_date))
        query = f"""
                SELECT 
                    delivery_state_code AS delivery_state_code,
                    delivery_state AS delivery_state,
                    SUM(total_orders_delivered) AS total_orders,
                    SUM(intradistrict_orders) AS intradistrict_orders,
                    SUM(intrastate_orders) AS intrastate_orders
                FROM {table_name}
                WHERE sub_domain = 'B2B' and
                    (order_year > %s OR (order_year = %s AND order_month >= %s))
                    AND (order_year < %s OR (order_year = %s AND order_month <= %s))
            """

        parameters = [params.start_year, params.start_year, params.start_month,
                      params.end_year, params.end_year, params.end_month]

        conditions = []

        if domain:
            conditions.append("AND domain_name = %s")
            parameters.append(domain)

        if state:
            conditions.append("AND upper(delivery_state) = upper(%s)")
            parameters.append(state)

        if category and category != 'None':
            conditions.append("AND category = %s")
            parameters.append(category)

        if sub_category:
            conditions.append("AND sub_category = %s")
            parameters.append(sub_category)

        conditions_str = ' '.join(conditions)
        query = query + conditions_str + ' GROUP BY delivery_state_code, delivery_state ORDER BY total_orders DESC'

        aggregated_df = self.db_utility.execute_query(query, parameters)

        return aggregated_df

    @log_function_call(ondcLogger)
    def fetch_overall_active_sellers(self, start_date, end_date, category=None,
                                     sub_category=None, domain=None, state=None):

        params = DotDict(self.get_query_month_parameters(start_date, end_date))
        table_name = constant.MONTHLY_PROVIDERS

        query = f"""
            SELECT 
                seller_state AS seller_state,
                seller_state_code AS seller_state_code,
                COUNT(DISTINCT TRIM(LOWER(provider_key))) AS active_sellers_count
            FROM 
                {table_name}
            WHERE
                (order_year > %s OR (order_year = %s AND order_month >= %s))
                AND (order_year < %s OR (order_year = %s AND order_month <= %s))
                AND seller_state <> ''
                AND seller_state is not null
        """

        parameters = [params.start_year, params.start_year, params.start_month,
                      params.end_year, params.end_year, params.end_month]

        conditions = []

        if state:
            conditions.append("AND upper(seller_state) = upper(%s)")
            parameters.append(state)

        conditions_str = ' '.join(conditions)
        query = query + conditions_str + " GROUP BY seller_state, seller_state_code"

        df = self.db_utility.execute_query(query, parameters)

        return df




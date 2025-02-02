__author__ = "Shashank Katyayan"

from datetime import datetime
import json
from apps.logging_conf import log_function_call, ondcLogger
from decimal import getcontext
from apps.utils import constant
from apps.utils.constant import MONTHLY_DISTRICT_TABLE

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
                                   sub_category=None, domain=None, state=None):

        table_name = constant.MONTHLY_DISTRICT_TABLE
        # stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        # edate_obj = datetime.strptime(end_date, '%Y-%m-%d')
        #
        # start_month = stdate_obj.month
        # start_year = stdate_obj.year
        # end_month = edate_obj.month
        # end_year = edate_obj.year
        #
        # parameters = {
        #     'start_month': start_month,
        #     'start_year': start_year,
        #     'end_month': end_month,
        #     'end_year': end_year
        # }
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
                    {constant.LOGISTICS_MONTHLY_PROVIDERS}
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
                    COUNT(DISTINCT delivery_district) AS total_districts,
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
                    {constant.LOGISTICS_MONTHLY_PROVIDERS}
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
                    COUNT(DISTINCT ds.provider_key) AS total_active_sellers
                FROM
                    {constant.LOGISTICS_MONTHLY_PROVIDERS} ds
                WHERE
                    (ds.order_year > %(start_year)s OR (ds.order_year = %(start_year)s AND ds.order_month >= %(start_month)s))
                    AND (ds.order_year < %(end_year)s OR (ds.order_year = %(end_year)s AND ds.order_month <= %(end_month)s))
        """

        if state:
            query += " AND ds.seller_state = %(state)s"
            parameters['state'] = state

        query += """
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
                    AND swdlo.delivery_state <> '' AND swdlo.delivery_state IS NOT NULL
        """

        if domain:
            query += " AND swdlo.domain_name = %(domain)s"
            parameters['domain'] = domain

        query += f"""
                GROUP BY swdlo.delivery_state_code, swdlo.delivery_state
            ),
            ActiveSellersTotal AS (
                SELECT
                    'TT' AS seller_state_code,
                    'TOTAL' AS seller_state,
                    COUNT(DISTINCT TRIM(LOWER(ds.provider_key))) AS total_active_sellers
                FROM
                    {constant.LOGISTICS_MONTHLY_PROVIDERS} ds
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
        """

        if domain:
            query += " AND swdlo.domain_name = %(domain)s"
            parameters['domain'] = domain

        query += """
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

        query = query.format(table_name=table_name)

        orders_count = self.db_utility.execute_query(query, parameters)
        return orders_count

    @log_function_call(ondcLogger)
    def fetch_retail_overall_orders(self, start_date, end_date, category=None,
                                    sub_category=None, domain_name=None, state=None):
        selected_view = constant.MONTHLY_DISTRICT_TABLE
        parameters = self.get_query_month_parameters(start_date, end_date)

        query = f"""
            SELECT 
                order_month AS order_month,
                order_year AS order_year,
                SUM(total_orders_delivered) AS total_orders_delivered
            FROM 
                {selected_view}
            WHERE 
                (order_year > %(start_year)s OR (order_year = %(start_year)s AND order_month >= %(start_month)s))
                AND (order_year < %(end_year)s OR (order_year = %(end_year)s AND order_month <= %(end_month)s))
        """

        if domain_name:
            query += " AND domain_name = %(domain_name)s"
            parameters['domain_name'] = domain_name

        if state:
            query += " AND delivery_state = %(state)s"
            parameters['state'] = state

        query += """
            GROUP BY 
                order_month, order_year 
            ORDER BY 
                order_year, order_month
        """

        df = self.db_utility.execute_query(query, parameters)
        return df

    @log_function_call(ondcLogger)
    def fetch_retail_overall_top_states_orders(self, start_date, end_date, category=None,
                                               sub_category=None, domain_name=None, state=None):
        try:
            selected_view = MONTHLY_DISTRICT_TABLE
            parameters = self.get_query_month_parameters(start_date, end_date)

            query = f'''
                WITH TopStates AS (
                    SELECT 
                        COALESCE(delivery_state, 'MISSING') as delivery_state,
                        SUM(total_orders_delivered) AS total_orders_delivered
                    FROM 
                        {selected_view}
                    WHERE 
                        (order_year > %(start_year)s OR (order_year = %(start_year)s AND order_month >= %(start_month)s))
                        AND (order_year < %(end_year)s OR (order_year = %(end_year)s AND order_month <= %(end_month)s))
                        AND delivery_state != 'MISSING'
            '''

            if state and state != 'None' and state != 'null':
                query += ' AND upper(delivery_state) = upper(%(state)s)'
                parameters['state'] = state

            if domain_name and domain_name != 'None':
                query += ' AND domain_name = %(domain_name)s'
                parameters['domain_name'] = domain_name

            query += f'''
                    GROUP BY 
                        delivery_state
                    ORDER BY 
                        total_orders_delivered DESC
                    LIMIT 3
                ),
                FinalResult AS (
                    SELECT 
                        om.order_month as order_month,
                        om.order_year as order_year,
                        COALESCE(om.delivery_state, 'MISSING') as delivery_state,
                        SUM(om.total_orders_delivered) AS total_orders_delivered
                    FROM 
                        {selected_view} om
                    INNER JOIN 
                        TopStates ts ON COALESCE(om.delivery_state, 'MISSING') = UPPER(ts.delivery_state)
                    WHERE 
                        (om.order_year > %(start_year)s OR (om.order_year = %(start_year)s AND om.order_month >= %(start_month)s))
                        AND (om.order_year < %(end_year)s OR (om.order_year = %(end_year)s AND om.order_month <= %(end_month)s))
            '''

            if state and state != 'None' and state != 'null':
                query += ' AND upper(om.delivery_state) = upper(%(state)s)'

            if domain_name and domain_name != 'None':
                query += ' AND om.domain_name = %(domain_name)s'

            query += '''
                    GROUP BY 
                        om.order_year, om.order_month, om.delivery_state
                    ORDER BY 
                        om.order_year, om.order_month, total_orders_delivered DESC
                )
                SELECT * FROM FinalResult 
            '''

            df = self.db_utility.execute_query(query, parameters)
            return df

        except Exception as e:
            ondcLogger.error(str(e))
            raise

    @log_function_call(ondcLogger)
    def fetch_overall_top_district_orders(self, start_date, end_date, category=None,
                                          sub_category=None, domain=None, state=None):

        selected_view = constant.MONTHLY_DISTRICT_TABLE
        params = DotDict(self.get_query_month_parameters(start_date, end_date))
        query_template = """
            WITH 
            TopDistricts AS (
                SELECT 
                    delivery_district,
                    SUM(total_orders_delivered) AS total_order_demand
                FROM {selected_view}
                WHERE (order_year > %s OR (order_year = %s AND order_month >= %s))
                      AND (order_year < %s OR (order_year = %s AND order_month <= %s))
                      AND delivery_district <> '' 
                      AND delivery_district IS NOT NULL
                      AND delivery_state IS NOT NULL 
                      AND delivery_state <> '' 
                      {conditions}
                GROUP BY delivery_district
                ORDER BY total_order_demand DESC
                LIMIT 3
            ),
            FinalResult AS (
                SELECT
                    foslm.order_month AS order_month,
                    foslm.order_year AS order_year,
                    td.delivery_district AS delivery_district,
                    COALESCE(SUM(foslm.total_orders_delivered), 0) AS total_orders_delivered
                FROM TopDistricts td
                LEFT JOIN {selected_view} foslm 
                    ON foslm.delivery_district = td.delivery_district 
                WHERE (foslm.order_year > %s OR (foslm.order_year = %s AND foslm.order_month >= %s))
                      AND (foslm.order_year < %s OR (foslm.order_year = %s AND foslm.order_month <= %s))
                      AND td.delivery_district <> '' 
                      AND upper(td.delivery_district) <> upper('undefined') 
                      AND td.delivery_district IS NOT NULL
                      {final_conditions}
                GROUP BY foslm.order_month, foslm.order_year, td.delivery_district
                ORDER BY foslm.order_year, foslm.order_month, total_orders_delivered DESC
            )
            SELECT * FROM FinalResult;
        """

        conditions = []
        final_conditions = []
        parameters = [params.start_year, params.start_year,
                      params.start_month, params.end_year, params.end_year, params.end_month]

        if domain:
            conditions.append("AND domain_name = %s")
            parameters.append(domain)

        if state:
            conditions.append("AND upper(delivery_state) = upper(%s)")
            parameters.append(state)

        parameters.extend([params.start_year, params.start_year, params.start_month,
                           params.end_year, params.end_year, params.end_month])

        if domain:
            final_conditions.append("AND foslm.domain_name = %s")
            parameters.append(domain)

        if state:
            final_conditions.append("AND upper(foslm.delivery_state) = upper(%s)")
            parameters.append(state)

        conditions_str = ' '.join(conditions)
        final_conditions_str = ' '.join(final_conditions)

        query = query_template.format(selected_view=selected_view, conditions=conditions_str,
                                      final_conditions=final_conditions_str)

        df = self.db_utility.execute_query(query, parameters)

        return df

    @log_function_call(ondcLogger)
    def fetch_overall_cumulative_sellers(self, start_date, end_date, category=None,
                                         sub_category=None, domain_name=None, state=None):
        table_name = constant.LOGISTICS_MONTHLY_PROVIDERS
        parameters = self.get_query_month_parameters(start_date, end_date)

        query = f"""
            SELECT 
                order_month,
                order_year,
                COUNT(DISTINCT TRIM(LOWER(provider_key))) AS total_orders_delivered
            FROM 
                {table_name}
            WHERE
                (order_year > %(start_year)s OR (order_year = %(start_year)s AND order_month >= %(start_month)s))
                AND (order_year < %(end_year)s OR (order_year = %(end_year)s AND order_month <= %(end_month)s))
        """

        if state:
            query += " AND delivery_state = %(state)s"
            parameters['state'] = state

        query += " GROUP BY order_month, order_year ORDER BY order_year, order_month"

        df = self.db_utility.execute_query(query, parameters)
        return df

    def fetch_overall_top_states_hyperlocal_orders(self, start_date, end_date, category=None, sub_category=None,
                                                   domain_name=None, state=None):
        selected_view = constant.MONTHLY_DISTRICT_TABLE
        params = DotDict(self.get_query_month_parameters(start_date, end_date))
        parameters = [params.start_year, params.start_year,
                      params.start_month, params.end_year, params.end_year, params.end_month]

        base_query = f"""
            WITH TopStates AS (
                SELECT 
                    COALESCE(delivery_state, 'MISSING') AS delivery_state,
                    SUM(total_orders_delivered) AS total_orders_delivered,
                    SUM(intrastate_orders) AS intrastate_orders_total,
                    ROUND(SUM(intrastate_orders::numeric) / NULLIF(SUM(total_orders_delivered::numeric), 0), 2) * 100 AS intrastate_orders_percentage
                FROM 
                    {selected_view}
                WHERE 
                    (order_year > %s OR (order_year = %s AND order_month >= %s))
                    AND (order_year < %s OR (order_year = %s AND order_month <= %s))
                    AND delivery_state != 'MISSING'
                    AND delivery_state != ''
        """

        if domain_name:
            base_query += " AND domain_name = %s"
            parameters.append(domain_name)

        if state:
            base_query += " AND upper(delivery_state) = upper(%s)"
            parameters.append(state)

        base_query += f"""
                GROUP BY 
                    delivery_state
                HAVING SUM(total_orders_delivered) >= 1
                ORDER BY 
                    intrastate_orders_percentage DESC,
                    delivery_state ASC
                LIMIT 3
            ),
            FinalResult AS (
                SELECT 
                    om.order_month AS order_month,
                    om.order_year AS order_year,
                    COALESCE(om.delivery_state, 'MISSING') AS delivery_state,
                    SUM(om.total_orders_delivered) AS total_orders_delivered,
                    ROUND(SUM(om.intrastate_orders::numeric) / NULLIF(SUM(om.total_orders_delivered::numeric), 0), 2) * 100 AS intrastate_orders_percentage
                FROM 
                    {selected_view} om
                INNER JOIN 
                    TopStates ts ON COALESCE(om.delivery_state, 'MISSING') = ts.delivery_state
                WHERE 
                    (om.order_year > %s OR (om.order_year = %s AND om.order_month >= %s))
                    AND (om.order_year < %s OR (om.order_year = %s AND om.order_month <= %s))
                    AND om.total_orders_delivered >= 1
        """

        parameters.extend([params.start_year, params.start_year, params.start_month,
                           params.end_year, params.end_year, params.end_month])

        if domain_name:
            base_query += " AND om.domain_name = %s"
            parameters.append(domain_name)

        if state:
            base_query += " AND upper(om.delivery_state) = upper(%s)"
            parameters.append(state)

        base_query += """
                GROUP BY 
                    om.order_month, om.order_year, om.delivery_state
                ORDER BY 
                    om.order_year, om.order_month, intrastate_orders_percentage DESC,
                    om.delivery_state ASC
            )
            SELECT * FROM FinalResult 
            where intrastate_orders_percentage > 0; 
        """

        df = self.db_utility.execute_query(base_query, parameters)

        return df

    @log_function_call(ondcLogger)
    def fetch_overall_top_district_hyperlocal_orders(self, start_date, end_date, category=None, sub_category=None,
                                                     domain_name=None, state=None):

        selected_view = constant.MONTHLY_DISTRICT_TABLE
        parameters = self.get_query_month_parameters(start_date, end_date)

        base_query = f"""
            WITH TopDistricts AS (
                SELECT 
                    delivery_district,
                    SUM(total_orders_delivered) AS total_order_demand,
                    SUM(intradistrict_orders) AS intradistrict_orders,
                    ROUND((SUM(intradistrict_orders::numeric) / NULLIF(SUM(total_orders_delivered::numeric), 0)), 2) * 100 AS intradistrict_percentage
                FROM 
                    {selected_view}
                WHERE 
                    (order_year > %(start_year)s OR (order_year = %(start_year)s AND order_month >= %(start_month)s))
                    AND (order_year < %(end_year)s OR (order_year = %(end_year)s AND order_month <= %(end_month)s))
                    AND delivery_district <> '' AND UPPER(delivery_district) <> 'UNDEFINED'
                    AND delivery_district IS NOT NULL 
        """

        if domain_name:
            base_query += " AND domain_name = %(domain_name)s"
            parameters['domain_name'] = domain_name

        if state:
            base_query += " AND upper(delivery_state) = upper(%(state)s)"
            parameters['state'] = state

        base_query += f"""
                GROUP BY 
                    delivery_district
                HAVING SUM(total_orders_delivered) >= 1
                ORDER BY 
                    intradistrict_percentage DESC,
                    delivery_district ASC
                
                LIMIT 3
            ),
            FinalResult AS (
                SELECT 
                    om.order_month AS order_month,
                    om.order_year AS order_year,
                    om.delivery_district AS delivery_district,
                    SUM(om.total_orders_delivered) AS total_orders_delivered,
                    SUM(om.intradistrict_orders) AS intradistrict_orders,
                    ROUND((SUM(om.intradistrict_orders::numeric) / NULLIF(SUM(om.total_orders_delivered::numeric), 0)), 2) * 100 AS intrastate_orders_percentage
                FROM 
                    {selected_view} om
                JOIN 
                    TopDistricts td ON om.delivery_district = td.delivery_district
                WHERE 
                    (om.order_year > %(start_year)s OR (om.order_year = %(start_year)s AND om.order_month >= %(start_month)s))
                    AND (om.order_year < %(end_year)s OR (om.order_year = %(end_year)s AND om.order_month <= %(end_month)s))
        """

        if domain_name:
            base_query += " AND om.domain_name = %(domain_name)s"

        if state:
            base_query += " AND upper(om.delivery_state) = upper(%(state)s)"

        base_query += """
                GROUP BY 
                    om.order_month, om.order_year, om.delivery_district
                ORDER BY 
                    om.order_year, om.order_month, intrastate_orders_percentage DESC,
                    om.delivery_district ASC
            )
            SELECT * FROM FinalResult
            where intrastate_orders_percentage > 0;
        """

        base_query = base_query.format(selected_view=selected_view)
        df = self.db_utility.execute_query(base_query, parameters)

        return df

    @log_function_call(ondcLogger)
    def fetch_overall_top5_seller_states(self, start_date, end_date, category=None, sub_category=None, domain=None,
                                 state=None):

        table_name = constant.LOGISTICS_DISTRICT_TABLE

        query = f"""
            SELECT 
                sub.delivery_state,
                COALESCE(NULLIF(TRIM(sub.seller_state), ''), 'Missing') AS seller_state,
                sub.order_demand,
                ROUND(sub.flow_percentage,2) as flow_percentage
            FROM (
                SELECT 
                    om.delivery_state,
                    om.seller_state,
                    SUM(om.total_orders_delivered) AS order_demand,
                    (SUM(om.total_orders_delivered) * 100.0) / total.total_orders AS flow_percentage,
                    ROW_NUMBER() OVER (
                        PARTITION BY om.delivery_state 
                        ORDER BY SUM(om.total_orders_delivered) DESC
                    ) as rn
                FROM 
                    {table_name} om
                INNER JOIN (
                    SELECT 
                        swdlo.delivery_state, 
                        SUM(swdlo.total_orders_delivered) AS total_orders 
                    FROM {table_name} swdlo
                    WHERE swdlo.order_date BETWEEN %s AND %s
                      AND swdlo.delivery_state <> ''
                      AND swdlo.delivery_state is not NULL
        """

        parameters = [start_date, end_date]

        query += """
                    GROUP BY swdlo.delivery_state
                ) total ON om.delivery_state = total.delivery_state
                WHERE 
                 om.order_date BETWEEN %s AND %s
        """

        parameters.extend([start_date, end_date])

        if state:
            query += constant.tdr_delivery_state_sub_query
            parameters.append(state)

        query += """
                GROUP BY 
                    om.delivery_state, om.seller_state, total.total_orders
            ) sub
            WHERE sub.rn <= 4
            ORDER BY sub.delivery_state, sub.flow_percentage DESC;
        """

        df = self.db_utility.execute_query(query, parameters)
        return df

    @log_function_call(ondcLogger)
    def fetch_overall_top5_seller_districts(self, start_date, end_date, category=None, sub_category=None, domain=None,
                                    state=None, district=None):

        table_name = constant.LOGISTICS_DISTRICT_TABLE

        query = f"""
            SELECT 
                sub.delivery_district,
                COALESCE(NULLIF(TRIM(sub.seller_district), ''), 'Missing') AS seller_district,
                sub.order_demand,
                ROUND(sub.flow_percentage, 2) AS flow_percentage
            FROM (
                SELECT 
                    om.delivery_district,
                    om.seller_district,
                    SUM(om.total_orders_delivered) AS order_demand,
                    (SUM(om.total_orders_delivered) * 100.0) / total.total_orders AS flow_percentage,
                    ROW_NUMBER() OVER (
                        PARTITION BY om.delivery_district 
                        ORDER BY SUM(om.total_orders_delivered) DESC
                    ) AS rn
                FROM 
                    {table_name} om
                INNER JOIN (
                    SELECT 
                        swdlo.delivery_district, 
                        SUM(swdlo.total_orders_delivered) AS total_orders 
                    FROM {table_name} swdlo
                    WHERE swdlo.order_date BETWEEN %s AND %s
                      AND swdlo.delivery_district <> ''
                      AND swdlo.delivery_district is not NULL
        """

        parameters = [start_date, end_date]

        if state:
            query += constant.swdlo_delivery_st_sq
            parameters.append(state)

        query += """
                    GROUP BY swdlo.delivery_district
                ) total ON upper(om.delivery_district) = upper(total.delivery_district)
                WHERE om.order_date BETWEEN %s AND %s 
                AND om.delivery_district is not NULL
                AND om.delivery_district <> ''
        """

        parameters.extend([start_date, end_date])

        if state:
            query += constant.tdr_delivery_state_sub_query
            parameters.append(state)
        if district:
            query += " AND upper(om.delivery_district) = upper(%s)"
            parameters.append(district)

        query += """
                GROUP BY 
                    om.delivery_district, om.seller_district, total.total_orders
            ) sub
            WHERE sub.rn <= 4
            ORDER BY sub.delivery_district, sub.flow_percentage DESC;
        """

        df = self.db_utility.execute_query(query, parameters)
        return df

    @log_function_call(ondcLogger)
    def fetch_cumulative_orders_statedata_summary(self, start_date, end_date,
                                                  category=None, sub_category=None,
                                                  domain=None, state=None):

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
    def fetch_overall_active_sellers(self, start_date, end_date, category=None,
                                     sub_category=None, domain=None, state=None):

        params = DotDict(self.get_query_month_parameters(start_date, end_date))
        table_name = constant.LOGISTICS_MONTHLY_PROVIDERS

        query = f"""
            SELECT 
                seller_state AS seller_state,
                seller_state_code AS seller_state_code,
                COUNT(DISTINCT provider_key) AS active_sellers_count
            FROM 
                {table_name}
            WHERE
                (order_year > %s OR (order_year = %s AND order_month >= %s))
                AND (order_year < %s OR (order_year = %s AND order_month <= %s))
        """

        parameters = [params.start_year, params.start_year, params.start_month, params.end_year,
                      params.end_year, params.end_month]

        conditions = []

        if state:
            conditions.append("AND upper(seller_state) = upper(%s)")
            parameters.append(state)

        conditions_str = ' '.join(conditions)
        query = query + conditions_str + " GROUP BY seller_state, seller_state_code"

        df = self.db_utility.execute_query(query, parameters)

        return df

    @log_function_call(ondcLogger)
    def fetch_overall_active_sellers_statedata(self, start_date, end_date,
                                               category=None, sub_category=None,
                                               domain=None, state=None):

        table_name = constant.LOGISTICS_MONTHLY_PROVIDERS
        params = DotDict(self.get_query_month_parameters(start_date, end_date))
        query = f"""
            SELECT 
                seller_state AS seller_state,
                seller_state_code AS seller_state_code,
                seller_district AS seller_district,
                COUNT(DISTINCT provider_key) AS active_sellers_count
            FROM 
                {table_name}
            WHERE
                (order_year > %s OR (order_year = %s AND order_month >= %s))
                AND (order_year < %s OR (order_year = %s AND order_month <= %s))
        """

        parameters = [params.start_year, params.start_year, params.start_month,
                      params.end_year, params.end_year, params.end_month]

        conditions = []

        if state:
            conditions.append("AND upper(seller_state) = upper(%s)")
            parameters.append(state)

        conditions_str = ' '.join(conditions)
        query = query + conditions_str + " GROUP BY seller_district, seller_state, seller_state_code"

        df = self.db_utility.execute_query(query, parameters)

        return df

    @log_function_call(ondcLogger)
    def fetch_cumulative_orders_statewise_summary(self, start_date, end_date,
                                                  category=None, sub_category=None, domain=None, state=None):
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
                WHERE
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

    def fetch_district_count(self, start_date, end_date,
                             category=None, sub_category=None,
                             domain=None, state=None):
        domain = 'Logistics' if domain is None else domain

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
            query += " AND domain_name = %s"
            parameters.append(domain)
        query += " group by delivery_state_code, delivery_state"
        district_count = self.db_utility.execute_query(query, parameters)

        return district_count




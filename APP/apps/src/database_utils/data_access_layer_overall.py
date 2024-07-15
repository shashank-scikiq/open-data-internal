import pandas as pd
from apps.logging_conf import log_function_call, ondcLogger
from decimal import Decimal, getcontext
from apps.utils.constant import (B2B_SELLER_TABLE, B2B_DISTRICT_TABLE, LOGISTICS_DISTRICT_TABLE, MONTHLY_DISTRICT_TABLE,
                                 category_sub_query, sub_category_sub_query,
                                 domain_sub_query, delivery_state_sub_query, seller_state_sub_query, NO_DATA_MSG)
from datetime import datetime

from apps.utils import constant


getcontext().prec = 4


class DataAccessLayerOverall:

    def __init__(self, db_utility):
        self.db_utility = db_utility
        self.numeric_columns = ['total_orders_delivered', 'total_items', 'intradistrict_orders', 'intrastate_orders']
        self.sunburst_numeric_col = 'total_orders_delivered'


    @log_function_call(ondcLogger)
    def fetch_total_orders_summary(self, start_date, end_date, category=None,
                                   sub_category=None, domain=None, state=None):
        table_name = MONTHLY_DISTRICT_TABLE
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
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

        query = """
            WITH DistrictRanking AS (
                SELECT
                    delivery_state_code AS delivery_state_code,
                    delivery_state AS delivery_state,
                    delivery_district AS delivery_district,
                    SUM(total_orders_delivered) AS total_orders_in_district,
                    ROW_NUMBER() OVER (PARTITION BY delivery_state ORDER BY SUM(total_orders_delivered) DESC) AS rank_in_state
                FROM
                    {table_name}
                WHERE
                    order_month >= %(start_month)s AND order_year >= %(start_year)s AND
                    order_month <= %(end_month)s AND order_year >= %(end_year)s
                    AND delivery_state <> ''
        """.format(table_name=table_name)

        if domain:
            query += " AND domain_name = %(domain)s"
            parameters['domain'] = domain

        query += f"""
                GROUP BY
                    delivery_state_code,
                    delivery_state,
                    delivery_district
            ),
            ActiveSellers AS (
                SELECT
                    seller_state AS seller_state_code,
                    seller_state AS seller_state,
                    COUNT(DISTINCT provider_key) AS total_active_sellers
                FROM
                    {constant.MONTHLY_PROVIDERS}
                WHERE
                    order_month >= %(start_month)s AND order_year >= %(start_year)s AND
                    order_month <= %(end_month)s AND order_year >= %(end_year)s
        """

        if category:
            query += " AND category = %(category)s"
            parameters['category'] = category

        if sub_category:
            query += " AND sub_category = %(sub_category)s"
            parameters['sub_category'] = sub_category

        if domain:
            query += " AND domain_name = %(domain)s"
            parameters['domain'] = domain

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
                    order_month >= %(start_month)s AND order_year >= %(start_year)s AND
                    order_month <= %(end_month)s AND order_year >= %(end_year)s
                    AND delivery_state <> ''
        """.format(table_name=table_name)

        if domain:
            query += " AND domain_name = %(domain)s"
            parameters['domain'] = domain

        query += """
                GROUP BY
                    delivery_state_code,
                    delivery_state
            ),
            StateRanking AS (
                SELECT
                    delivery_state_code AS delivery_state_code,
                    delivery_state AS delivery_state,
                    SUM(total_orders_delivered) AS total_orders_in_state,
                    ROW_NUMBER() OVER (ORDER BY SUM(total_orders_delivered) DESC) AS rank_in_state
                FROM
                    {table_name}
                WHERE
                    order_month >= %(start_month)s AND order_year >= %(start_year)s AND
                    order_month <= %(end_month)s AND order_year >= %(end_year)s
                    AND delivery_state <> ''
        """.format(table_name=table_name)

        if domain:
            query += " AND domain_name = %(domain)s"
            parameters['domain'] = domain

        query += f"""
                GROUP BY
                    delivery_state_code,
                    delivery_state
            ),
            ActiveSellersTotal AS (
                SELECT
                    'TT' AS seller_state_code,
                    'TOTAL' AS seller_state,
                    COUNT(DISTINCT provider_key) AS total_active_sellers
                FROM
                    {constant.MONTHLY_PROVIDERS}
                WHERE
                    order_month >= %(start_month)s AND order_year >= %(start_year)s AND
                    order_month <= %(end_month)s AND order_year >= %(end_year)s
        """

        if category:
            query += " AND category = %(category)s"
            parameters['category'] = category

        if sub_category:
            query += " AND sub_category = %(sub_category)s"
            parameters['sub_category'] = sub_category

        if domain:
            query += " AND domain_name = %(domain)s"
            parameters['domain'] = domain

        if state:
            query += " AND seller_state = %(state)s"
            parameters['state'] = state

        query += """
            ),
            AggregatedDataTotal AS (
                SELECT
                    'TT' AS delivery_state_code,
                    'TOTAL' AS delivery_state,
                    COUNT(DISTINCT delivery_district) AS total_districts,
                    SUM(total_orders_delivered) AS delivered_orders
                FROM
                    {table_name}
                WHERE
                    order_month >= %(start_month)s AND order_year >= %(start_year)s AND
                    order_month <= %(end_month)s AND order_year >= %(end_year)s
        """.format(table_name=table_name)

        if domain:
            query += " AND domain_name = %(domain)s"
            parameters['domain'] = domain

        query += """
            )
            SELECT
                AD.delivery_state_code AS delivery_state_code,
                AD.delivery_state AS delivery_state,
                AD.total_districts AS total_districts,
                AD.delivered_orders AS delivered_orders,
                COALESCE(ASel.total_active_sellers, 0) AS total_active_sellers
            FROM
                AggregatedData AD
            LEFT JOIN
                ActiveSellers ASel ON AD.delivery_state_code = ASel.seller_state_code
            UNION ALL
            SELECT
                'TT' AS delivery_state_code,
                'TOTAL' AS delivery_state,
                ADT.total_districts AS total_districts,
                ADT.delivered_orders AS delivered_orders,
                COALESCE(ASelt.total_active_sellers, 0) AS total_active_sellers
            FROM
                AggregatedDataTotal ADT
            LEFT JOIN
                ActiveSellersTotal ASelt ON 1 = 1
        """.format(table_name=table_name)

        orders_count = self.db_utility.execute_query(query, parameters)
        return orders_count
    @log_function_call(ondcLogger)
    def fetch_total_orders_summary_prev(self, start_date, end_date, category=None,
                                        sub_category=None, domain=None, state=None):
        table_name = MONTHLY_DISTRICT_TABLE
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
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

        query = f"""
            WITH ActiveSellers AS (
                SELECT
                    seller_state AS seller_state_code,
                    seller_state AS seller_state,
                    COUNT(DISTINCT provider_key) AS total_active_sellers
                FROM
                    {constant.MONTHLY_PROVIDERS}
                WHERE
                    order_month >= %(start_month)s AND order_year >= %(start_year)s AND
                    order_month <= %(end_month)s AND order_year >= %(end_year)s
                    AND seller_state <> ''
        """

        if category:
            query += " AND category = %(category)s"
            parameters['category'] = category

        if sub_category:
            query += " AND sub_category = %(sub_category)s"
            parameters['sub_category'] = sub_category

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
                    order_month >= %(start_month)s AND order_year >= %(start_year)s AND
                    order_month <= %(end_month)s AND order_year >= %(end_year)s
                    AND delivery_state <> ''
        """.format(table_name=table_name)

        if domain:
            query += " AND domain_name = %(domain)s"
            parameters['domain'] = domain

        query += f"""
                GROUP BY
                    delivery_state_code,
                    delivery_state
            ),
            ActiveSellersTotal AS (
                SELECT
                    'TT' AS seller_state_code,
                    'TOTAL' AS seller_state,
                    COUNT(DISTINCT provider_key) AS total_active_sellers
                FROM
                    {constant.MONTHLY_PROVIDERS}
                WHERE
                    order_month >= %(start_month)s AND order_year >= %(start_year)s AND
                    order_month <= %(end_month)s AND order_year >= %(end_year)s
        """

        if category:
            query += " AND category = %(category)s"
            parameters['category'] = category

        if sub_category:
            query += " AND sub_category = %(sub_category)s"
            parameters['sub_category'] = sub_category

        if domain:
            query += " AND domain_name = %(domain)s"
            parameters['domain'] = domain

        if state:
            query += " AND seller_state = %(state)s"
            parameters['state'] = state

        query += """
            ),
            AggregatedDataTotal AS (
                SELECT
                    'TT' AS delivery_state_code,
                    'TOTAL' AS delivery_state,
                    COUNT(DISTINCT delivery_district) AS total_districts,
                    SUM(total_orders_delivered) AS delivered_orders
                FROM
                    {table_name}
                WHERE
                    order_month >= %(start_month)s AND order_year >= %(start_year)s AND
                    order_month <= %(end_month)s AND order_year >= %(end_year)s
        """.format(table_name=table_name)

        if domain:
            query += " AND domain_name = %(domain)s"
            parameters['domain'] = domain

        query += """
            )
            SELECT
                AD.delivery_state_code AS delivery_state_code,
                AD.delivery_state AS delivery_state,
                AD.total_districts AS total_districts,
                AD.delivered_orders AS delivered_orders,
                COALESCE(ASel.total_active_sellers, 0) AS total_active_sellers
            FROM
                AggregatedData AD
            LEFT JOIN
                ActiveSellers ASel ON AD.delivery_state_code = ASel.seller_state_code
            UNION ALL
            SELECT
                'TT' AS delivery_state_code,
                'TOTAL' AS delivery_state,
                ADT.total_districts AS total_districts,
                ADT.delivered_orders AS delivered_orders,
                COALESCE(ASelt.total_active_sellers, 0) AS total_active_sellers
            FROM
                AggregatedDataTotal ADT
            LEFT JOIN
                ActiveSellersTotal ASelt ON 1 = 1
        """.format(table_name=table_name)

        orders_count = self.db_utility.execute_query(query, parameters)
        return orders_count

    @log_function_call(ondcLogger)
    def fetch_retail_overall_orders(self, start_date, end_date, category=None,
                                sub_category=None, domain_name=None, state=None):

        selected_view = constant.MONTHLY_DISTRICT_TABLE
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        end_month = edate_obj.month
        start_year = stdate_obj.year
        end_year = edate_obj.year

        parameters = [start_month, start_year, end_month, end_year ]

        query = f"""
            SELECT order_month as order_month,
                    order_year as order_year,
                sum(total_orders_delivered) AS total_orders_delivered
            FROM 
                {selected_view}
            WHERE 
                order_month >= %s  AND order_year >= %s AND
                order_month <= %s AND order_year >= %s
        """

        if domain_name:
            query += constant.domain_sub_query
            parameters.append(domain_name)
        if state:
            query += constant.delivery_state_sub_query
            parameters.append(state)

        query += """
                GROUP BY order_month, order_year 
                ORDER BY 
                    order_year, order_month
        """

        df = self.db_utility.execute_query(query, parameters)

        return df


    @log_function_call(ondcLogger)
    def fetch_retail_overall_top_states_orders(self, start_date, end_date, category=None,
                                sub_category=None, domain_name=None, state=None):
        try:
            selected_view = constant.MONTHLY_DISTRICT_TABLE
            stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
            edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

            # Extract month and year
            start_month = stdate_obj.month
            end_month = edate_obj.month
            start_year = stdate_obj.year
            end_year = edate_obj.year

            parameters = [start_month, start_year, end_month, end_year]

            query = f'''
                WITH TopStates AS (
                    SELECT 
                        COALESCE(delivery_state, 'MISSING') as delivery_state,
                        sum(total_orders_delivered) AS total_orders_delivered
                    FROM 
                        {selected_view}
                    WHERE 
                        order_month >= %s  AND order_year >= %s AND
                        order_month <= %s AND order_year >= %s
                        and delivery_state != 'MISSING'
            '''

            if state and state != 'None' and state!='null':
                query += constant.delivery_state_sub_query
                parameters.append(state)

            if domain_name and domain_name != 'None':
                query += ''' AND domain_name = %s '''
                parameters.append(domain_name)

            query += '''
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
                        {0} om
                    INNER JOIN 
                        TopStates ts ON COALESCE(om.delivery_state, 'MISSING') = upper(ts.delivery_state)
                    WHERE 
                        om.order_month >= %s  AND om.order_year >= %s AND
                        om.order_month <= %s AND om.order_year >= %s
            '''.format(selected_view)

            parameters.extend([start_month, start_year, end_month, end_year])

            if state and state != 'None' and state!='null':
                query += constant.tdr_delivery_state_sub_query
                parameters.append(state)

            query += '''
                    GROUP BY 
                        om.order_year, om.order_month, om.delivery_state
                    ORDER BY 
                        om.order_year, om.order_month, total_orders_delivered desc
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
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        start_year = stdate_obj.year
        end_month = edate_obj.month
        end_year = edate_obj.year

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
        parameters = [start_year, start_year, start_month, end_year, end_year, end_month]

        if domain:
            conditions.append("AND domain_name = %s")
            parameters.append(domain)

        if state:
            conditions.append("AND upper(delivery_state) = upper(%s)")
            parameters.append(state)

        parameters.extend([start_year, start_year, start_month, end_year, end_year, end_month])

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

        table_name = constant.MONTHLY_PROVIDERS
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        end_month = edate_obj.month
        start_year = stdate_obj.year
        end_year = edate_obj.year

        query = f"""
                    SELECT 
                        order_month,
                        order_year,
                        COUNT(DISTINCT trim(lower(provider_key))) AS total_orders_delivered
                    FROM 
                        {table_name}
                    WHERE
                        order_month >= %s  AND order_year >= %s AND
                        order_month <= %s AND order_year >= %s 
                """

        parameters = [start_month, start_year, end_month, end_year]

        # if domain_name:
        #     query += constant.domain_sub_query
        #     parameters.append(domain_name)

        if state:
            query += constant.delivery_state_sub_query
            parameters.append(state)

        query += " GROUP BY 1, 2"

        df = self.db_utility.execute_query(query, parameters)

        return df


    @log_function_call(ondcLogger)
    def fetch_overall_top_states_hyperlocal_orders(self, start_date, end_date, category=None, sub_category=None,
                                           domain_name=None, state=None):

        selected_view = constant.MONTHLY_DISTRICT_TABLE
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        end_month = edate_obj.month
        start_year = stdate_obj.year
        end_year = edate_obj.year


        parameters = [start_month, start_year, end_month, end_year]

        base_query = f'''
                    WITH TopStates AS (
                        SELECT 
                            COALESCE(delivery_state, 'MISSING') as delivery_state,
                            sum(total_orders_delivered) AS total_orders_delivered,
                            SUM(intrastate_orders) AS intrastate_orders_total,
                            ROUND(SUM(intrastate_orders::numeric) / 
                            NULLIF(SUM(total_orders_delivered::numeric), 0) * 100, 2) AS intrastate_orders_percentage
                        FROM {selected_view}
                        WHERE 
                            order_month >= %s  AND order_year >= %s AND
                            order_month <= %s AND order_year >= %s 
                            and delivery_state != 'MISSING'
                    '''

        if domain_name:
            base_query += constant.domain_sub_query
            parameters.append(domain_name)


        if state:
            base_query += constant.delivery_state_sub_query
            parameters.append(state)

        base_query += f'''
                    GROUP BY 
                        delivery_state
                    ORDER BY 
                        intrastate_orders_percentage DESC
                        LIMIT 3
                )
                SELECT 
                    om.order_month as order_month,
                    om.order_year as order_year,
                    COALESCE(om.delivery_state, 'MISSING')  as delivery_state,
                    SUM(om.total_orders_delivered) AS total_orders_delivered,
                    ROUND(SUM(om.intrastate_orders::numeric) / 
                    NULLIF(SUM(om.total_orders_delivered::numeric), 0) * 100, 2) AS intrastate_orders_percentage
                FROM {selected_view} om
                INNER JOIN 
                    TopStates ts ON COALESCE(om.delivery_state, 'MISSING')  = ts.delivery_state
                WHERE 
                    om.order_month >= %s  AND om.order_year >= %s AND
                    om.order_month <= %s AND om.order_year >= %s 
        '''

        parameters.append(start_month)
        parameters.append(start_year)
        parameters.append(end_month)
        parameters.append(end_year)

        if domain_name:
            base_query += constant.tdr_domain_sub_query
            parameters.append(domain_name)

        if state:
            base_query += constant.tdr_delivery_state_sub_query
            parameters.append(state)

        base_query += ('\nGROUP BY om.order_month, om.order_year, om.delivery_state '
                       'ORDER BY om.order_month, om.order_year, intrastate_orders_percentage DESC')

        df = self.db_utility.execute_query(base_query, parameters)

        return df

    def fetch_overall_top_district_hyperlocal_orders(self, start_date, end_date, category=None, sub_category=None,
                                             domain_name=None, state=None):

        selected_view = constant.MONTHLY_DISTRICT_TABLE
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        end_month = edate_obj.month
        start_year = stdate_obj.year
        end_year = edate_obj.year

        query = f"""
            WITH TopDistricts AS (
                SELECT 
                    delivery_district,
                    sum(total_orders_delivered) AS total_order_demand,
                    SUM(intradistrict_orders) AS intradistrict_orders,
                    ROUND((SUM(intradistrict_orders::numeric) / 
                    NULLIF(SUM(total_orders_delivered::numeric), 0)) * 100, 2) AS intradistrict_percentage
                FROM 
                    {selected_view}
                WHERE 
                    order_month >= %s  AND order_year >= %s AND
                    order_month <= %s AND order_year >= %s 
                    AND delivery_district <> '' and upper(delivery_district) <> 'UNDEFINED'
                    and delivery_district is not null

        """

        parameters = [start_month, start_year, end_month, end_year]

        if domain_name:
            query += constant.domain_sub_query
            parameters.append(domain_name)
        if state:
            query += constant.delivery_state_sub_query
            parameters.append(state)

        query += """
                GROUP BY 
                    delivery_district
                ORDER BY 
                    intradistrict_percentage DESC
                LIMIT 3
            ),
            FinalResult AS (
                SELECT 
                    om.order_month as order_month,
                    om.order_year as order_year,
                    om.delivery_district as delivery_district,
                    SUM(om.total_orders_delivered) AS total_orders_delivered,
                    SUM(om.intradistrict_orders) AS intradistrict_orders,
                    ROUND((SUM(om.intradistrict_orders::numeric) / 
                    NULLIF(SUM(om.total_orders_delivered::numeric), 0)) * 100, 2) AS intrastate_orders_percentage
                FROM 
        """

        query += f"{selected_view} om"

        query += """
                INNER JOIN 
                    TopDistricts td ON om.delivery_district = td.delivery_district
                WHERE 
                    om.order_month >= %s  AND om.order_year >= %s AND
                    om.order_month <= %s AND om.order_year >= %s 
        """

        parameters.extend([start_month, start_year, end_month, end_year])

        if domain_name:
            query += constant.tdr_domain_sub_query
            parameters.append(domain_name)
        if state:
            query += constant.tdr_delivery_state_sub_query
            parameters.append(state)

        query += """
                GROUP BY 
                    om.order_month, om.order_year, om.delivery_district
                ORDER BY 
                    om.order_month, om.order_year, intrastate_orders_percentage DESC
            )
            SELECT * FROM FinalResult;
        """

        df = self.db_utility.execute_query(query, parameters)

        return df


    @log_function_call(ondcLogger)
    def fetch_most_orders_delivered_to_summary(self, start_date, end_date, category=None,
                                           sub_category=None, domain=None, state=None):

        # Convert string to datetime object
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        end_month = edate_obj.month
        start_year = stdate_obj.year
        end_year = edate_obj.year

        table_name = MONTHLY_DISTRICT_TABLE

        parameters = [start_month, start_year, end_month, end_year,]
        where_conditions = " AND swdlo.delivery_state IS NOT NULL AND swdlo.delivery_state <> ''"

        if category and category != 'None':
            where_conditions += " AND swdlo.category = %s"
            parameters.append(category)
        if sub_category:
            where_conditions += " AND swdlo.sub_category = %s"
            parameters.append(sub_category)
        if domain:
            where_conditions += " AND swdlo.domain = %s"
            parameters.append(domain)
        if state:
            where_conditions += " AND upper(swdlo.delivery_state) = upper(%s)"
            parameters.append(state)

        if not state:
            query = f"""
                    SELECT
                        swdlo.delivery_state,
                        SUM(swdlo.total_orders_delivered) AS total_orders_in_state
                    FROM
                        {table_name} swdlo
                    WHERE
                        swdlo.order_month >= %s AND swdlo.order_year >= %s AND
                        swdlo.order_month <= %s AND swdlo.order_year >= %s 
                        {where_conditions}
                    GROUP BY
                        swdlo.delivery_state
                    ORDER BY
                        total_orders_in_state DESC
                    LIMIT 1;
                """
        else:
            query = f"""
                    WITH StateDistricts AS (
                        SELECT
                            swdlo.delivery_district,
                            SUM(swdlo.total_orders_delivered) AS total_orders_in_district
                        FROM
                            {table_name} swdlo
                        WHERE
                            swdlo.order_date BETWEEN %s AND %s
                            {where_conditions}
                        GROUP BY
                            swdlo.delivery_district
                        ORDER BY
                            total_orders_in_district DESC
                        LIMIT 1
                    )
                    SELECT
                        delivery_district AS top_district,
                        total_orders_in_district
                    FROM
                        StateDistricts;
                """

        most_delivering_areas = self.db_utility.execute_query(query, parameters, return_type='sql')

        value = NO_DATA_MSG

        try:
            if most_delivering_areas and isinstance(most_delivering_areas, list) and most_delivering_areas[0]:
                value = most_delivering_areas[0][0]
        except Exception as e:
            print(f"Error: {e}")

        return value


    @log_function_call(ondcLogger)
    def fetch_cumulative_orders_statedata_summary(self, start_date, end_date,
                                                  category=None, sub_category=None,
                                                  domain=None, state=None):
        # Convert string to datetime object
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        start_year = stdate_obj.year
        end_month = edate_obj.month
        end_year = edate_obj.year

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

        parameters = [start_year, start_year, start_month, end_year, end_year, end_month]

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

        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        start_year = stdate_obj.year
        end_month = edate_obj.month
        end_year = edate_obj.year

        table_name = constant.MONTHLY_PROVIDERS

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

        parameters = [start_year, start_year, start_month, end_year, end_year, end_month]

        conditions = []

        # if category and category != 'None':
        #     conditions.append("AND category = %s")
        #     parameters.append(category)
        #
        # if sub_category:
        #     conditions.append("AND sub_category = %s")
        #     parameters.append(sub_category)

        # if domain:
        #     conditions.append("AND domain_name = %s")
        #     parameters.append(domain)

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

        table_name = constant.MONTHLY_PROVIDERS
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        start_year = stdate_obj.year
        end_month = edate_obj.month
        end_year = edate_obj.year

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

        parameters = [start_year, start_year, start_month, end_year, end_year, end_month]

        conditions = []

        # if category and category != 'None':
        #     conditions.append("AND category = %s")
        #     parameters.append(category)
        #
        # if sub_category:
        #     conditions.append("AND sub_category = %s")
        #     parameters.append(sub_category)
        #
        # if domain:
        #     conditions.append("AND domain_name = %s")
        #     parameters.append(domain)

        if state:
            conditions.append("AND upper(seller_state) = upper(%s)")
            parameters.append(state)

        conditions_str = ' '.join(conditions)
        query = query + conditions_str + " GROUP BY seller_district, seller_state, seller_state_code"

        df = self.db_utility.execute_query(query, parameters)

        return df


    @log_function_call(ondcLogger)
    def fetch_district_count_summary(self,  start_date, end_date, category=None,
                                 sub_category=None, domain=None, state=None):
        table_name = MONTHLY_DISTRICT_TABLE
        # Convert string to datetime object
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        end_month = edate_obj.month
        start_year = stdate_obj.year
        end_year = edate_obj.year

        query = f"""
                       select 
                       count(distinct delivery_district) as delivery_district_count
                    FROM 
                        {table_name}
                    WHERE
                        order_month >= %s AND order_year >= %s AND
                        order_month <= %s AND order_year >= %s 
                """

        parameters = [ start_month, start_year, end_month, end_year]

        if category and category != 'None':
            query += category_sub_query
            parameters.append(category)

        if sub_category:
            query += sub_category_sub_query
            parameters.append(sub_category)

        if domain:
            query += domain_sub_query
            parameters.append(domain)

        if state:
            query += delivery_state_sub_query
            parameters.append(state)

        districts_count = self.db_utility.execute_query(query, parameters, return_type='sql')
        if isinstance(districts_count, list) and districts_count:
            try:
                return districts_count[0][0]
            except Exception as e:
                print(f"Error: {e}")
                return 0
        else:
            return 0


    @log_function_call(ondcLogger)
    def fetch_cumulative_orders_statewise_summary(self, start_date, end_date,
                                                  category=None, sub_category=None, domain=None, state=None):
        table_name = constant.MONTHLY_DISTRICT_TABLE  # Ensure you import this constant from your constants module
        # Convert string to datetime object
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        start_year = stdate_obj.year
        end_month = edate_obj.month
        end_year = edate_obj.year

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

        parameters = [start_year, start_year, start_month, end_year, end_year, end_month]

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


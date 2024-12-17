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
    def fetch_top_district_sellers(self, start_date, end_date, category=None, sub_category=None,
                                            domain=None, state=None, seller_type='Total'):

        table_name = constant.ACTIVE_TOTAL_SELLER_TBL
        if domain == 'Logistics':
            table_name = constant.LOGISTICS_MONTHLY_PROVIDERS

        parameters = self.get_query_month_parameters(start_date, end_date)

        query = f"""
            WITH TopDistricts AS (
                SELECT 
                    seller_district,
                    SUM(total_sellers) as active_sellers_count
                FROM 
                    {table_name}
                WHERE
                    (year_val > %(start_year)s OR (year_val = %(start_year)s AND mnth_val >= %(start_month)s))
                    AND (year_val < %(end_year)s OR (year_val = %(end_year)s AND mnth_val <= %(end_month)s))
                    AND seller_district <> 'Undefined'
                    AND seller_district IS NOT NULL
                    AND seller_district <> ''
                    AND category = 'AGG'
                    AND seller_district <> 'Missing'
                    AND seller_district <> 'AGG'
        """

        if state:
            query += " AND COALESCE(UPPER(seller_state), 'MISSING') = UPPER(%(state)s)"
            parameters['state'] = state.upper()

        query += f"""
                GROUP BY 
                    seller_district
                 
                ORDER BY 
                    active_sellers_count DESC
                LIMIT 3
            ),
            FinalResult AS (
                SELECT 
                    om.mnth_val AS order_month,
                    om.year_val AS order_year,
                    om.seller_district AS district,
                    SUM(total_sellers) as active_sellers_count
                FROM 
                    {table_name} om
                INNER JOIN 
                    TopDistricts td ON om.seller_district = td.seller_district
                WHERE
                    (om.year_val > %(start_year)s OR (om.year_val = %(start_year)s AND om.mnth_val >= %(start_month)s))
                    AND (om.year_val < %(end_year)s OR (om.year_val = %(end_year)s AND om.mnth_val <= %(end_month)s))
        """

        if state:
            query += " AND COALESCE(UPPER(om.seller_state), 'MISSING') = UPPER(%(state)s)"
            parameters['state'] = state.upper()

        query += """
                GROUP BY 
                    om.mnth_val, om.year_val, om.seller_district
                ORDER BY 
                    om.year_val, om.mnth_val, active_sellers_count DESC
            )
            SELECT * FROM FinalResult;
        """
        
        df = self.db_utility.execute_query(query, parameters)
        return df

    @log_function_call(ondcLogger)
    def fetch_top_state_sellers(self, start_date, end_date, category=None, sub_category=None,
                                          domain=None, state=None, seller_type='Total'):
        base_table = constant.ACTIVE_TOTAL_SELLER_TBL
        if domain == 'Logistics':
            base_table = constant.LOGISTICS_MONTHLY_PROVIDERS

        parameters = self.get_query_month_parameters(start_date, end_date)

        query = f'''
            WITH StateSellerCounts AS (
                SELECT 
                    COALESCE(seller_state, 'MISSING') AS seller_state,
                    SUM(total_sellers) AS active_sellers_count
                FROM 
                    {base_table}
                WHERE
                    (year_val > %(start_year)s OR (year_val = %(start_year)s AND mnth_val >= %(start_month)s))
                    AND (year_val < %(end_year)s OR (year_val = %(end_year)s AND mnth_val <= %(end_month)s))
                    AND seller_state <> ''
                    AND seller_state is not null
                    AND category = 'AGG'
                    AND seller_state <> 'AGG'
                    AND seller_state <> 'Missing'
        '''

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
                om.mnth_val AS order_month,
                om.year_val AS order_year,
                COALESCE(om.seller_state, 'MISSING') AS state,
                SUM(total_sellers) AS active_sellers_count,
                rs.state_rank
            FROM 
                {base_table} om
            INNER JOIN 
                RankedStates rs ON COALESCE(om.seller_state, 'MISSING') = rs.seller_state
            WHERE
                (om.year_val > %(start_year)s OR (om.year_val = %(start_year)s AND om.mnth_val >= %(start_month)s))
                AND (om.year_val < %(end_year)s OR (om.year_val = %(end_year)s AND om.mnth_val <= %(end_month)s))
        '''

        if state:
            query += " AND COALESCE(UPPER(om.seller_state), 'MISSING') = UPPER(%(state)s)"
            parameters['state'] = state.upper()

        query += '''
            GROUP BY 
                om.mnth_val, om.year_val, om.seller_state, rs.state_rank
            ORDER BY 
                rs.state_rank, om.year_val, om.mnth_val
        '''
        
        df = self.db_utility.execute_query(query, parameters)
        return df

    @log_function_call(ondcLogger)
    def fetch_total_orders_summary(self, start_date, end_date, category=None,
                                   sub_category=None, domain=None, state=None):
        domain = 'Retail' if domain is None else domain

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

        query += f"""
                GROUP BY
                    delivery_state, delivery_district
            ),
            ActiveSellers AS (
                SELECT
                    seller_state AS seller_state_code,
                    seller_state,
                    SUM(total_sellers) AS total_active_sellers
                FROM
                    {constant.ACTIVE_TOTAL_SELLER_TBL}
                WHERE
                    
                    ((year_val * 100) + mnth_val)= ((%(end_year)s * 100) + %(end_month)s)
                    
                    AND category = 'AGG'
                    AND sub_category ='AGG'
                    AND seller_state != 'Missing'
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
                    AND delivery_state <> '' AND delivery_state_code IS NOT NULL AND delivery_state <> 'Missing'
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
                    SUM(total_sellers) AS total_active_sellers
                FROM
                    {constant.ACTIVE_TOTAL_SELLER_TBL}
                WHERE
                    ((year_val * 100) + mnth_val)= ((%(end_year)s * 100) + %(end_month)s)
                    AND seller_state = 'AGG'    
                    AND seller_district = 'AGG'
                    AND category = 'AGG'
                    AND sub_category ='AGG'
                    AND seller_state != 'Missing'
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

        domain = 'Retail' if domain is None else domain

        table_name = constant.MONTHLY_DISTRICT_TABLE
        parameters = self.get_query_month_parameters(start_date, end_date)

        query = f"""
            WITH ActiveSellers AS (
                SELECT
                    ds.seller_state AS seller_state_code,
                    ds.seller_state AS seller_state,
                    SUM(total_sellers)  AS total_active_sellers
                FROM
                    {constant.ACTIVE_TOTAL_SELLER_TBL} ds
                WHERE
                    ((ds.year_val * 100) + ds.mnth_val)= ((%(end_year)s * 100) + %(end_month)s)
                    
                    AND category = 'AGG'
                    AND sub_category ='AGG'
                    AND seller_state != 'Missing'
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
                    SUM(total_sellers) AS total_active_sellers
                FROM
                    {constant.ACTIVE_TOTAL_SELLER_TBL} ds
                WHERE
                    ((ds.year_val * 100) + ds.mnth_val)= ((%(end_year)s * 100) + %(end_month)s)
                    
                    AND category = 'AGG'
                    AND sub_category ='AGG'
                    AND seller_state != 'Missing'
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
                                    sub_category=None, domain_name='Retail', state=None):
        domain_name = 'Retail' if domain_name is None else domain_name
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

            domain_name = 'Retail' if domain_name is None else domain_name

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
                    HAVING delivery_state NOT IN ('Missing')
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
        domain = 'Retail' if domain is None else domain

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
                HAVING delivery_district NOT IN ('Missing')
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
        parameters = [params.start_year, params.start_year, params.start_month,
                      params.end_year, params.end_year, params.end_month]

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
                                         sub_category=None, domain_name=None, state=None, seller_type='Total'):
        table_name = constant.ACTIVE_TOTAL_SELLER_TBL
        parameters = self.get_query_month_parameters(start_date, end_date)

        query = f"""
            SELECT 
                mnth_val as order_month,
                year_val as order_year,
                SUM(total_sellers) AS total_orders_delivered
            FROM 
                {table_name}
            WHERE
                ((year_val*100) + mnth_val) between ((%(start_year)s*100) + %(start_month)s) and ((%(end_year)s*100) + %(end_month)s)
                AND seller_state = 'AGG'
                AND seller_district = 'AGG'
                AND category = 'AGG'
        """

        if state:
            query += " AND delivery_state = %(state)s"
            parameters['state'] = state

        query += " GROUP BY mnth_val, year_val ORDER BY year_val, mnth_val"
        df = self.db_utility.execute_query(query, parameters)
        
        return df

    @log_function_call(ondcLogger)
    def fetch_overall_top_states_hyperlocal_orders(self, start_date, end_date, category=None, sub_category=None,
                                                   domain_name=None, state=None):
        domain_name = 'Retail' if domain_name is None else domain_name

        selected_view = constant.MONTHLY_DISTRICT_TABLE
        params = DotDict(self.get_query_month_parameters(start_date, end_date))
        parameters = [params.start_year, params.start_year, params.start_month,
                      params.end_year, params.end_year, params.end_month]

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
                    AND delivery_state is not NULL
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
            select * from FinalResult 
            where intrastate_orders_percentage > 0
        """

        base_query = base_query.format(selected_view=selected_view)
        df = self.db_utility.execute_query(base_query, parameters)

        return df

    @log_function_call(ondcLogger)
    def fetch_overall_top_district_hyperlocal_orders(self, start_date, end_date, category=None, sub_category=None,
                                                     domain_name=None, state=None):
        domain_name = 'Retail' if domain_name is None else domain_name
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
                    AND delivery_district <> ''
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
                    intradistrict_percentage DESC
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
                INNER JOIN 
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
                    om.order_year, om.order_month, intrastate_orders_percentage DESC
            )
            SELECT * FROM FinalResult 
            where intrastate_orders_percentage > 0
        """

        base_query = base_query.format(selected_view=selected_view)
        df = self.db_utility.execute_query(base_query, parameters)

        return df

    @log_function_call(ondcLogger)
    def fetch_overall_top5_seller_states(self, start_date, end_date, category=None, sub_category=None, domain=None,
                                 state=None):

        domain = 'Retail' if domain is None else domain
        table_name = constant.MONTHLY_DISTRICT_TABLE

        params = DotDict(self.get_query_month_parameters(start_date, end_date))
        query = f"""
            SELECT 
                sub.delivery_state,
                sub.seller_state,
                sub.order_demand,
                sub.flow_percentage as flow_percentage
            FROM (
                SELECT 
                    om.delivery_state,
                    om.seller_state,
                    SUM(om.total_orders_delivered) AS order_demand,
                    (SUM(om.total_orders_delivered::integer) * 100.0) / total.total_orders AS flow_percentage,
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
                    where (swdlo.order_year > %s OR (swdlo.order_year = %s AND swdlo.order_month >= %s))
                    AND (swdlo.order_year < %s OR (swdlo.order_year = %s AND swdlo.order_month <= %s))
                    AND swdlo.domain_name = 'Retail'
                     -- AND swdlo.delivery_state <> ''
        """

        parameters = [params.start_year, params.start_year, params.start_month,
                      params.end_year, params.end_year, params.end_month]


        query += """
                    GROUP BY swdlo.delivery_state
                ) total ON om.delivery_state = total.delivery_state
                WHERE 
                 (om.order_year > %s OR (om.order_year = %s AND om.order_month >= %s))
                    AND (om.order_year < %s OR (om.order_year = %s AND om.order_month <= %s))
                    
        """

        parameters.extend([params.start_year, params.start_year, params.start_month,
                           params.end_year, params.end_year, params.end_month])

        if state:
            query += constant.tdr_delivery_state_sub_query
            parameters.append(state)

        if domain:
            query += constant.tdr_domain_sub_query
            parameters.append(domain)

        query += """
                GROUP BY 
                    om.delivery_state, om.seller_state, total.total_orders
            ) sub
            WHERE sub.rn <= 4
            and sub.seller_state != ''
            and sub.seller_state is not NULL
            ORDER BY sub.delivery_state, sub.flow_percentage DESC;
        """
        
        df = self.db_utility.execute_query(query, parameters)
        return df

    @log_function_call(ondcLogger)
    def fetch_overall_top5_seller_districts(self, start_date, end_date, category=None, sub_category=None, domain=None,
                                    state=None, district=None):

        domain = 'Retail' if domain is None else domain
        table_name = constant.MONTHLY_DISTRICT_TABLE

        params = DotDict(self.get_query_month_parameters(start_date, end_date))
        query = f"""
            SELECT 
                sub.delivery_district,
                sub.seller_district,
                sub.order_demand,
                ROUND(sub.flow_percentage::numeric, 2) AS flow_percentage
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
                    WHERE (swdlo.order_year > %s OR (swdlo.order_year = %s AND swdlo.order_month >= %s))
                    AND (swdlo.order_year < %s OR (swdlo.order_year = %s AND swdlo.order_month <= %s))
                    AND swdlo.domain_name = 'Retail'
                    AND swdlo.delivery_district <> ''
                    AND swdlo.seller_district <> ''
                    AND swdlo.seller_district is not NULL
        """

        parameters = [params.start_year, params.start_year, params.start_month,
                      params.end_year, params.end_year, params.end_month]

        if state:
            query += constant.swdlo_delivery_st_sq
            parameters.append(state)

        if domain:
            query += constant.swdlo_domain_sub_query
            parameters.append(domain)

        query += """
                    GROUP BY swdlo.delivery_district
                ) total ON upper(om.delivery_district) = upper(total.delivery_district)
                where (om.order_year > %s OR (om.order_year = %s AND om.order_month >= %s))
                    AND (om.order_year < %s OR (om.order_year = %s AND om.order_month <= %s))
        """

        parameters.extend([params.start_year, params.start_year, params.start_month,
                           params.end_year, params.end_year, params.end_month])

        if state:
            query += constant.tdr_delivery_state_sub_query
            parameters.append(state)
        if district:
            query += " AND upper(om.delivery_district) = upper(%s)"
            parameters.append(district)
        if domain:
            query += " AND om.domain_name = %s"
            parameters.append(domain)

        query += """
                GROUP BY 
                    om.delivery_district, om.seller_district, total.total_orders
            ) sub
            WHERE sub.rn <= 4
            and sub.seller_district != ''
            ORDER BY sub.delivery_district, sub.flow_percentage DESC;
        """
        
        df = self.db_utility.execute_query(query, parameters)
        return df

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
            query += " AND domain_name = %s"
            parameters.append(domain)
        query += " group by delivery_state_code, delivery_state"
        district_count = self.db_utility.execute_query(query, parameters)

        return district_count

    @log_function_call(ondcLogger)
    def fetch_cumulative_orders_statedata_summary(self, start_date, end_date,
                                                  category=None, sub_category=None,
                                                  domain=None, state=None):

        domain = 'Retail' if domain is None else domain

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
        table_name = constant.ACTIVE_TOTAL_SELLER_TBL

        query = f"""
            SELECT 
                seller_state AS seller_state,
                seller_state_code AS seller_state_code,
                SUM(total_sellers) AS active_sellers_count
            FROM 
                {table_name}
            WHERE
                (year_val > %s OR (year_val = %s AND mnth_val >= %s))
                AND (year_val < %s OR (year_val = %s AND mnth_val <= %s))
                AND seller_state <> ''
                AND seller_state is not null
                AND category = 'AGG'
                AND sub_category = 'AGG'
                AND seller_state <> 'Missing'
                AND seller_state <> 'AGG'
                AND seller_district = 'AGG'
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

    @log_function_call(ondcLogger)
    def fetch_overall_active_sellers_statedata(self, start_date, end_date,
                                               category=None, sub_category=None,
                                               domain=None, state=None):
        table_name = constant.MONTHLY_PROVIDERS
        params = DotDict(self.get_query_month_parameters(start_date, end_date))
        query = f"""
            SELECT 
                seller_state AS seller_state,
                seller_state_code AS seller_state_code,
                -- seller_district AS seller_district,
                COUNT(DISTINCT TRIM(LOWER(provider_key))) AS active_sellers_count
            FROM 
                {table_name}
            WHERE
                (order_year > %s OR (order_year = %s AND order_month >= %s))
                AND (order_year < %s OR (order_year = %s AND order_month <= %s))

                AND seller_state <> ''
                AND seller_state is not null
                AND seller_district is not null
                AND seller_district <> ''
        """

        parameters = [params.start_year, params.start_year, params.start_month,
                      params.end_year, params.end_year, params.end_month]

        conditions = []

        if state:
            conditions.append("AND upper(seller_state) = upper(%s)")
            parameters.append(state)

        conditions_str = ' '.join(conditions)
        query = query + conditions_str + " GROUP BY  seller_state, seller_state_code"

        df = self.db_utility.execute_query(query, parameters)
        
        return df

    @log_function_call(ondcLogger)
    def fetch_cumulative_orders_statewise_summary(self, start_date, end_date,
                                                  category=None, sub_category=None, domain=None, state=None):
        domain = 'Retail' if domain is None else domain
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

    @log_function_call(ondcLogger)
    def fetch_overall_top_delivery_state(self, start_date, end_date, category=None, sub_category=None, domain='Retail',
                                     state=None):

        table_name = constant.MONTHLY_DISTRICT_TABLE

        params = DotDict(self.get_query_month_parameters(start_date, end_date))
        
        query = f"""
            SELECT 
                sub.seller_state as delivery_state,
                sub.delivery_state as seller_state,
                sub.order_demand,
                sub.flow_percentage
            FROM (
                SELECT 
                    om.seller_state,
                    om.delivery_state,
                    SUM(om.total_orders_delivered) AS order_demand,
                    (SUM(om.total_orders_delivered) * 100.0) / total.total_orders AS flow_percentage,
                    ROW_NUMBER() OVER (
                        PARTITION BY om.seller_state 
                        ORDER BY SUM(om.total_orders_delivered) DESC
                    ) AS rn
                FROM 
                    {table_name} om
                INNER JOIN (
                    SELECT 
                        swdlo.seller_state, 
                        SUM(swdlo.total_orders_delivered) AS total_orders 
                    FROM {table_name} swdlo
                    WHERE 
                        ((swdlo.order_year * 100) + swdlo.order_month) BETWEEN 
                        (({params.start_year}*100) + {params.start_month}) AND
                        (({params.end_year}*100) + {params.end_month})
                    AND swdlo.domain_name = 'Retail' 
                    AND swdlo.sub_domain = 'B2C'
                    AND swdlo.seller_state <> ''
                    AND swdlo.seller_state <> 'Missing'
                    GROUP BY swdlo.seller_state
                ) total ON om.seller_state = total.seller_state
                WHERE 
                    ((om.order_year * 100) + om.order_month) BETWEEN
                    (({params.start_year}*100) + {params.start_month}) AND
                    (({params.end_year}*100) + {params.end_month})
                    AND om.domain_name = 'Retail'
                    AND om.sub_domain = 'B2C'
                    AND UPPER(om.seller_state) = UPPER('{state}')
                    AND om.delivery_state <> ''
                    AND om.delivery_state <> 'Missing'
        """


        query += """
                GROUP BY 
                    om.seller_state, om.delivery_state, total.total_orders
            ) sub
            WHERE sub.rn <= 4 and delivery_state <> 'Missing'
            ORDER BY sub.seller_state, sub.flow_percentage DESC;
        """
        
        df = self.db_utility.execute_query(query)
        return df
    
    @log_function_call(ondcLogger)
    def fetch_overall_top5_delivery_districts(self, start_date, end_date, category=None, sub_category=None, domain=None,
                                          state=None, seller_district=None):

       
        domain = 'Retail' if domain is None else domain

        
        table_name = constant.MONTHLY_DISTRICT_TABLE

        
        params = DotDict(self.get_query_month_parameters(start_date, end_date))

        
        query = f"""
            SELECT 
                sub.seller_district,
                sub.delivery_district,
                sub.order_demand,
                ROUND(sub.flow_percentage::numeric, 2) AS flow_percentage
            FROM (
                SELECT 
                    om.seller_district,
                    om.delivery_district,
                    SUM(om.total_orders_delivered) AS order_demand,
                    (SUM(om.total_orders_delivered) * 100.0) / total.total_orders AS flow_percentage,
                    ROW_NUMBER() OVER (
                        PARTITION BY om.seller_district 
                        ORDER BY SUM(om.total_orders_delivered) DESC
                    ) AS rn
                FROM 
                    {table_name} om
                INNER JOIN (
                    SELECT 
                        swdlo.seller_district, 
                        SUM(swdlo.total_orders_delivered) AS total_orders 
                    FROM {table_name} swdlo
                    WHERE 
                        (swdlo.order_year = %s AND swdlo.order_month BETWEEN %s AND %s)
                        AND swdlo.domain_name = %s
                        AND swdlo.delivery_district <> ''
                        AND swdlo.seller_district <> ''
                        AND swdlo.seller_district IS NOT NULL
                        and swdlo.seller_district <> 'Missing'
        """

        
        parameters = [params.start_year, params.start_month, params.end_month, domain]

        
        if seller_district:
            query += " AND upper(swdlo.seller_district) = upper(%s)"
            parameters.append(seller_district)

        
        query += """
                    GROUP BY swdlo.seller_district
                ) total ON upper(om.seller_district) = upper(total.seller_district)
                WHERE 
                    (om.order_year = %s AND om.order_month BETWEEN %s AND %s)
                    AND om.domain_name = %s
                    and om.delivery_district <> 'Missing'
        """

        
        parameters.extend([params.start_year, params.start_month, params.end_month, domain])

        
        if seller_district:
            query += " AND upper(om.seller_district) = upper(%s)"
            parameters.append(seller_district)

        
        query += """
                GROUP BY 
                    om.seller_district, om.delivery_district, total.total_orders
            ) sub
            WHERE sub.rn <= 4
            AND sub.delivery_district != ''
            ORDER BY sub.seller_district, sub.flow_percentage DESC;
        """
        
        df = self.db_utility.execute_query(query, parameters)
        return df



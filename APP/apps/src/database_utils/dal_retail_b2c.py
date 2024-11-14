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
    def fetch_top_district_sellers(self, start_date, end_date, category=None, sub_category=None,
                                            domain='Retail', state=None, seller_type='Total'):
        
        table_name = constant.ACTIVE_TOTAL_SELLER_TBL

        seller_column = 'total_sellers' if seller_type == 'Total' else 'active_sellers'
        
        parameters = self.get_query_month_parameters(start_date, end_date)

        query = f"""
            WITH TopDistricts AS (
                SELECT 
                    seller_district,
                    max({seller_column}) AS active_sellers_count
                FROM 
                    {table_name}
                WHERE
                    ((year_val*100)+mnth_val) = ((%(end_year)s*100)+%(end_month)s)
                    AND seller_district <> 'Undefined'
                    AND seller_district IS NOT NULL
                    AND seller_district <> ''
                    AND seller_district <> 'AGG'
                    AND seller_district <> 'Missing'
                    AND seller_district <> 'Misssing'
        """

        if state:
            query += " AND COALESCE(seller_state) = UPPER(%(state)s)"
            parameters['state'] = state.upper()
        else:
            query += " AND seller_state <> 'AGG'"
        
        if bool(category) and (category != 'None'):
            query += f" AND upper(category)=upper('{category}')"
            parameters['category'] = category
        else:
            query += " AND category='AGG'"

        if bool(sub_category) and (sub_category != 'None'):
            query += f" AND upper(sub_category)=upper('{sub_category}')"
            parameters['sub_category'] = sub_category
        else:
            query += " AND sub_category='AGG'"

        query += f"""
                group by 1
                ORDER BY 
                    active_sellers_count DESC
                LIMIT 3
            ),
            FinalResult AS (
                SELECT 
                    om.mnth_val AS order_month,
                    om.year_val AS order_year,
                    om.seller_district AS district,
                    max(om.{seller_column}) as active_sellers_count
                FROM 
                    {table_name} om
                INNER JOIN 
                    TopDistricts td ON om.seller_district = td.seller_district
                WHERE
                    ((om.year_val*100)+om.mnth_val) between 
                    ((%(start_year)s*100)+%(start_month)s) and ((%(end_year)s*100)+%(end_month)s)
        """

        if state:
            query += " AND COALESCE(UPPER(om.seller_state), 'MISSING') = UPPER(%(state)s)"
        else:
            query += " AND COALESCE(UPPER(om.seller_state), 'MISSING') <> 'AGG'"
        
        if bool(category) and (category != 'None'):
            query += f" AND upper(om.category)=upper('{category}')"
        else:
            query += " AND om.category='AGG'"

        if bool(sub_category) and (sub_category != 'None'):
            query += f" AND upper(om.sub_category)=upper('{sub_category}')"
        else:
            query += " AND om.sub_category='AGG'"

        query += f"""
                group by 1,2,3
                ORDER BY 
                    om.year_val, om.mnth_val
            )
            SELECT * FROM FinalResult;
        """

        df = self.db_utility.execute_query(query, parameters)
        return df

    @log_function_call(ondcLogger)
    def fetch_top_state_sellers(self, start_date, end_date, category=None, sub_category=None,
                                          domain='Retail', state=None, seller_type='Total'):
        base_table = constant.ACTIVE_TOTAL_SELLER_TBL

        seller_column = 'total_sellers' if seller_type == 'Total' else 'active_sellers'
        # base_table = constant.MONTHLY_PROVIDERS

        parameters = self.get_query_month_parameters(start_date, end_date)

        query = f'''
            WITH StateSellerCounts AS (
                SELECT 
                    COALESCE(seller_state, 'MISSING') AS seller_state,
                    max({seller_column}) AS active_sellers_count
                FROM 
                    {base_table}
                WHERE
                    ((year_val*100)+mnth_val) = ((%(end_year)s*100)+%(end_month)s)
                    AND seller_district = 'AGG'
                    and not seller_state in ('Missing', 'Misssing', '')
        '''

        if state:
            query += " AND COALESCE(seller_state) = UPPER(%(state)s)"
            parameters['state'] = state.upper()
        else:
            query += " AND seller_state <> 'AGG'"
        
        if bool(category) and (category != 'None'):
            query += f" AND upper(category)=upper('{category}')"
            parameters['category'] = category
        else:
            query += " AND category='AGG'"

        if bool(sub_category) and (sub_category != 'None'):
            query += f" AND upper(sub_category)=upper('{sub_category}')"
            parameters['sub_category'] = sub_category
        else:
            query += " AND sub_category='AGG'"

        query += f'''
            group by 1
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
                max(om.{seller_column}) as active_sellers_count,
                rs.state_rank
            FROM 
                {base_table} om
            INNER JOIN 
                RankedStates rs ON COALESCE(om.seller_state, 'MISSING') = rs.seller_state
            WHERE
                ((om.year_val*100)+om.mnth_val) between 
                ((%(start_year)s*100)+%(start_month)s) and ((%(end_year)s*100)+%(end_month)s)
                AND seller_district = 'AGG'
        '''

        if state:
            query += " AND COALESCE(UPPER(om.seller_state), 'MISSING') = UPPER(%(state)s)"
        else:
            query += " AND COALESCE(UPPER(om.seller_state), 'MISSING') <> 'AGG'"
        
        if bool(category) and (category != 'None'):
            query += f" AND upper(om.category)=upper('{category}')"
        else:
            query += " AND om.category='AGG'"

        if bool(sub_category) and (sub_category != 'None'):
            query += f" AND upper(om.sub_category)=upper('{sub_category}')"
        else:
            query += " AND om.sub_category='AGG'"

        query += '''
        group by 1,2,3, 5
            ORDER BY 
                rs.state_rank, om.year_val, om.mnth_val
        '''
        
        df = self.db_utility.execute_query(query, parameters)
        return df

    @log_function_call(ondcLogger)
    def fetch_total_orders_summary(self, start_date, end_date, category=None,
                                   sub_category=None, domain='Retail', state=None):
        table_name = constant.MONTHLY_DISTRICT_TABLE
        provider_table = constant.ACTIVE_TOTAL_SELLER_TBL
        aggregate_value = "'AGG'"

        if (category):
            table_name = constant.CAT_MONTHLY_DISTRICT_TABLE

        if (sub_category):
            table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE
        
        parameters = self.get_query_month_parameters(start_date, end_date)
    
        query = f"""
            WITH 
            req_table as (
                select 
                    * 
                from {table_name} 
                where
                    ((order_year*100) + order_month) between 
                        (({parameters['start_year']} * 100) + {parameters['start_month']}) 
                        and 
                        (({parameters['end_year']} * 100) + {parameters['end_month']})
                    and sub_domain = 'B2C' """
        
        if bool(category) and (category != 'None'):
            query += f" AND upper(category)=upper('{category}')"

        if bool(sub_category) and (sub_category != 'None'):
            query += f" AND upper(sub_category)=upper('{sub_category}')"

        query +=    f"""),
            DistrictRanking AS (
                SELECT
                    delivery_state AS delivery_state_code,
                    delivery_state,
                    delivery_district,
                    SUM(total_orders_delivered) AS total_orders_in_district,
                    case 
                        when sum(total_orders_delivered) = 0 then 0 
                        else round(cast((sum(total_items)/sum(total_orders_delivered)) as numeric), 2) end
                    as avg_items_per_order_in_district,
                    ROW_NUMBER() OVER (PARTITION BY delivery_state ORDER BY SUM(total_orders_delivered) DESC) AS rank_in_state
                FROM
                    req_table
                WHERE
                    delivery_state <> '' AND delivery_state IS NOT NULL AND delivery_state_code IS NOT NULL
                GROUP BY
                    delivery_state, delivery_district
            ),
            Sellers AS (
                SELECT
                    seller_state_code,
                    seller_state,
                    max(active_sellers) as active_sellers,
                    max(total_sellers) as total_sellers
                FROM
                    {provider_table}
                WHERE
                    ((year_val*100) + mnth_val) = (({parameters['end_year']} * 100) + {parameters['end_month']})
                    and seller_district = {aggregate_value}
                    and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregate_value})
                    and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregate_value})
                    and  upper(seller_state) { f"=upper('{state}')" if state else f"<>{aggregate_value}"}
                group by 1,2
            ),
            AggregatedData AS (
                SELECT
                    delivery_state_code AS delivery_state_code,
                    delivery_state AS delivery_state,
                    COUNT(DISTINCT CONCAT(delivery_state, '_', delivery_district)) as total_districts,
                    SUM(total_orders_delivered) AS delivered_orders,
                    case 
                        when sum(total_orders_delivered) = 0 then 0 
                        else round(cast((sum(total_items)/sum(total_orders_delivered)) as numeric), 2) end
                    as avg_items_per_order_in_district
                FROM
                    req_table
                WHERE
                    delivery_state <> '' AND delivery_state IS NOT NULL
                GROUP BY
                    delivery_state_code, delivery_state
            ),
            StateRanking AS (
                SELECT
                    delivery_state_code AS delivery_state_code,
                    delivery_state,
                    SUM(total_orders_delivered) AS total_orders_in_state,
                    case 
                        when sum(total_orders_delivered) = 0 then 0 
                        else round(cast((sum(total_items)/sum(total_orders_delivered)) as numeric), 2) end
                    as avg_items_per_order_in_district,
                    ROW_NUMBER() OVER (ORDER BY SUM(total_orders_delivered) DESC) AS rank_in_state
                FROM
                    req_table
                WHERE
                    delivery_state <> '' AND delivery_state_code IS NOT NULL
                GROUP BY
                    delivery_state_code,
                    delivery_state
            ),
            ActiveSellersTotal AS (
                SELECT
                    'TT' AS seller_state_code,
                    'TOTAL' AS seller_state,
                    max(total_sellers) as total_sellers,
                    max(active_sellers) as active_sellers
                FROM
                    {provider_table}
                WHERE
                    ((year_val*100) + mnth_val) = (({parameters['end_year']} * 100) + {parameters['end_month']})
                    and seller_district = {aggregate_value}
                    and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregate_value})
                    and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregate_value})
                    and  upper(seller_state) { f"=upper('{state}')" if state else f"={aggregate_value}"}
                group by 1,2
            ),
            AggregatedDataTotal AS (
                SELECT
                    'TT' AS delivery_state_code,
                    'TOTAL' AS delivery_state,
                    COUNT(DISTINCT CONCAT(delivery_state, '_', delivery_district)) AS total_districts,
                    SUM(total_orders_delivered) AS delivered_orders,
                    case 
                        when sum(total_orders_delivered) = 0 then 0 
                        else round(cast((sum(total_items)/sum(total_orders_delivered)) as numeric), 2) end
                    as avg_items_per_order_in_district
                FROM
                    req_table
            )
            SELECT
                COALESCE(AD.delivery_state_code, 'Missing') AS delivery_state_code,
                COALESCE(AD.delivery_state, 'Missing') AS delivery_state,
                AD.total_districts,
                AD.delivered_orders,
                AD.avg_items_per_order_in_district,
                COALESCE(ASel.total_sellers, 0) AS total_sellers,
                COALESCE(case when (ASel.active_sellers = 0 or ASel.total_sellers = 0) then 0.00
                    else round(cast(((ASel.active_sellers*100.0)/ASel.total_sellers) as numeric), 1) end, 0)
                AS active_sellers,
                DR.delivery_district AS most_ordering_district
            FROM
                AggregatedData AD
            LEFT JOIN
                Sellers ASel ON AD.delivery_state = ASel.seller_state
            LEFT JOIN
                (SELECT * FROM DistrictRanking WHERE rank_in_state = 1) DR ON AD.delivery_state = DR.delivery_state
            UNION ALL
            SELECT
                'TT' AS delivery_state_code,
                'TOTAL' AS delivery_state,
                ADT.total_districts,
                ADT.delivered_orders,
                ADT.avg_items_per_order_in_district,
                COALESCE(ASelt.total_sellers, 0) AS total_sellers,
                case when ASelt.active_sellers = 0 or ASelt.total_sellers = 0 then 0
                    else round(cast((ASelt.active_sellers*100.0)/ASelt.total_sellers as numeric), 1) end
                AS active_sellers,
                SRnk.delivery_state AS most_ordering_district
            FROM
                AggregatedDataTotal ADT
            LEFT JOIN
                ActiveSellersTotal ASelt ON 1=1 
            LEFT JOIN
                StateRanking SRnk ON SRnk.rank_in_state = 1
        """
        
        orders_count = self.db_utility.execute_query(query)
        return orders_count

    
    @log_function_call(ondcLogger)
    def fetch_total_orders_summary_prev(self, start_date, end_date, category=None,
                                        sub_category=None, domain='Retail', state=None):
        table_name = constant.MONTHLY_DISTRICT_TABLE
        provider_table = constant.ACTIVE_TOTAL_SELLER_TBL
        aggregate_value = "'AGG'"

        if category:
            table_name = constant.CAT_MONTHLY_DISTRICT_TABLE

        if sub_category:
            table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE

        parameters = self.get_query_month_parameters(start_date, end_date)

        query = f"""
            WITH 
            Sellers AS (
                SELECT
                    ds.seller_state_code AS seller_state_code,
                    ds.seller_state AS seller_state,
                    max(active_sellers) as active_sellers,
                    max(total_sellers) as total_sellers
                FROM
                    {provider_table} ds
                WHERE
                    ((year_val*100) + mnth_val) = (({parameters['end_year']} * 100) + {parameters['end_month']})
                    and seller_district = {aggregate_value}
                    and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregate_value})
                    and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregate_value})
                    and  upper(seller_state) { f"=upper('{state}')" if state else f"<>{aggregate_value}"}
                group by 1,2
            ),
            AggregatedData AS (
                SELECT
                    swdlo.delivery_state_code AS delivery_state_code,
                    swdlo.delivery_state AS delivery_state,
                    COUNT(DISTINCT CONCAT(swdlo.delivery_state, '_', swdlo.delivery_district)) as total_districts,
                    case 
                        when sum(swdlo.total_orders_delivered) = 0 then 0 
                        else round(cast((sum(swdlo.total_items)/sum(swdlo.total_orders_delivered)) as numeric), 1) end
                    as avg_items_per_order_in_district,
                    SUM(swdlo.total_orders_delivered) AS delivered_orders
                FROM
                    {table_name} swdlo
                WHERE
                    ((swdlo.order_year*100) + swdlo.order_month) between 
                        (({parameters['start_year']} * 100) + {parameters['start_month']}) 
                        and 
                        (({parameters['end_year']} * 100) + {parameters['end_month']})
                    AND swdlo.delivery_state <> '' AND swdlo.delivery_state IS NOT NULL
                    AND sub_domain='B2C'
            """

        if bool(category) and (category != 'None'):
            query += f" AND category='{category}'"

        if bool(sub_category) and (sub_category != 'None'):
            query += " AND sub_category='{sub_category}'"

        query += f"""
                GROUP BY
                    swdlo.delivery_state_code, swdlo.delivery_state
            ),
            ActiveSellersTotal AS (
                SELECT
                    'TT' AS seller_state_code,
                    'TOTAL' AS seller_state,
                    max(total_sellers) as total_sellers,
                    max(active_sellers) as active_sellers
                FROM    
                    {provider_table} ds
                WHERE
                    ((year_val*100) + mnth_val) = (({parameters['end_year']} * 100) + {parameters['end_month']})
                    and seller_district = {aggregate_value}
                    and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregate_value})
                    and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregate_value})
                    and  upper(seller_state) { f"=upper('{state}')" if state else f"={aggregate_value}"}
                group by 1,2
            ),
            AggregatedDataTotal AS (
                SELECT
                    'TT' AS delivery_state_code,
                    'TOTAL' AS delivery_state,
                    COUNT(DISTINCT CONCAT(swdlo.delivery_state, '_', swdlo.delivery_district)) AS total_districts,
                    case 
                        when sum(swdlo.total_orders_delivered) = 0 then 0 
                        else round(cast((sum(swdlo.total_items)/sum(swdlo.total_orders_delivered)) as numeric), 1) end
                    as avg_items_per_order_in_district,
                    SUM(swdlo.total_orders_delivered) AS delivered_orders
                FROM
                    {table_name} swdlo
                WHERE
                    ((swdlo.order_year*100) + swdlo.order_month) between 
                        (({parameters['start_year']} * 100) + {parameters['start_month']}) 
                        and 
                        (({parameters['end_year']} * 100) + {parameters['end_month']})
                    AND sub_domain='B2C'
            """

        if bool(category) and (category != 'None'):
            query += f" AND category='{category}'"

        if bool(sub_category) and (sub_category != 'None'):
            query += f" AND sub_category='{sub_category}'"

        query += f"""
            )
               SELECT
                COALESCE(AD.delivery_state_code, 'Missing') AS delivery_state_code,
                COALESCE(AD.delivery_state, 'Missing') AS delivery_state,
                AD.total_districts,
                AD.delivered_orders,
                AD.avg_items_per_order_in_district,
                COALESCE(
                    CASE
                        WHEN ASel.total_sellers < 3 THEN 0
                        ELSE ASel.total_sellers
                        END, 0) AS total_sellers,
                    case when ASel.active_sellers <= 3 or ASel.total_sellers = 0 then 0
                    else round(cast((ASel.active_sellers/ASel.total_sellers)*100 as numeric), 2) end
                AS active_sellers
            FROM
                AggregatedData AD
            LEFT JOIN
                Sellers ASel ON AD.delivery_state = ASel.seller_state
            UNION ALL
            SELECT
                'TT' AS delivery_state_code,
                'TOTAL' AS delivery_state,
                ADT.total_districts,
                ADT.delivered_orders,
                ADT.avg_items_per_order_in_district,
                COALESCE(
                    CASE
                        WHEN ASelt.total_sellers < 3 THEN 0
                        ELSE ASelt.total_sellers
                    END, 0) AS total_sellers,
                
                
                case when ASelt.active_sellers <= 3 or ASelt.total_sellers = 0 then 0
                    else round(cast((ASelt.active_sellers/ASelt.total_sellers)*100 as numeric), 2) end
                AS active_sellers
            FROM
                AggregatedDataTotal ADT
            LEFT JOIN
                ActiveSellersTotal ASelt ON 1=1
        """
        
        orders_count = self.db_utility.execute_query(query)
        return orders_count

    

    @log_function_call(ondcLogger)
    def fetch_retail_overall_orders(self, start_date, end_date, category=None,
                                    sub_category=None, domain_name='Retail', state=None):
        domain_name = 'Retail' if domain_name is None else domain_name
        selected_view = constant.MONTHLY_DISTRICT_TABLE
        if (category):
            selected_view = constant.CAT_MONTHLY_DISTRICT_TABLE
        if(sub_category):
            selected_view = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE
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
                AND domain_name = 'Retail' and sub_domain = 'B2C'
        """

        if state:
            query += " AND delivery_state = %(state)s"
            parameters['state'] = state
        
        if bool(category) and (category != 'None'):
            query += f" AND category='{category}'"

        if bool(sub_category) and (sub_category != 'None'):
            query += f" AND sub_category='{sub_category}'"


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
            selected_view = constant.MONTHLY_DISTRICT_TABLE
            if (category):
                selected_view = constant.CAT_MONTHLY_DISTRICT_TABLE
            if(sub_category):
                selected_view = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE
            parameters = self.get_query_month_parameters(start_date, end_date)

            query = f'''
                WITH TopStates AS (
                    SELECT 
                        COALESCE(delivery_state, 'MISSING') as delivery_state,
                        SUM(total_orders_delivered) AS total_orders_delivered
                    FROM 
                        {selected_view}
                    WHERE 
                        ((order_year*100) + order_month) between 
                            (({parameters['start_year']}*100)+{parameters['start_month']}) and 
                            (({parameters['end_year']}*100) + {parameters['end_month']})
                        AND delivery_state != 'MISSING'
                        and domain_name = 'Retail' and sub_domain='B2C'
            '''

            if state and state != 'None' and state != 'null':
                query += ' AND upper(delivery_state) = upper(%(state)s)'
                parameters['state'] = state
            
            if bool(category) and (category != 'None'):
                query += f" AND upper(category)=upper('{category}')"

            if bool(sub_category) and (sub_category != 'None'):
                query += f" AND upper(sub_category)=upper('{sub_category}')"

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
                        ((om.order_year*100) + om.order_month) between 
                            (({parameters['start_year']}*100)+{parameters['start_month']}) and 
                            (({parameters['end_year']}*100) + {parameters['end_month']})
                        and om.domain_name = 'Retail' and om.sub_domain = 'B2C'
            '''

            if state and state != 'None' and state != 'null':
                query += ' AND upper(om.delivery_state) = upper(%(state)s)'
            
            if bool(category) and (category != 'None'):
                query += f" AND upper(category)=upper('{category}')"

            if bool(sub_category) and (sub_category != 'None'):
                query += f" AND upper(sub_category)=upper('{sub_category}')"

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
                                          sub_category=None, domain='Retail', state=None):

        selected_view = constant.MONTHLY_DISTRICT_TABLE
        if (category):
            selected_view = constant.CAT_MONTHLY_DISTRICT_TABLE
        if(sub_category):
            selected_view = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE

        params = DotDict(self.get_query_month_parameters(start_date, end_date))
        query_template = f"""
            WITH 
            TopDistricts AS (
                SELECT 
                    delivery_district,
                    SUM(total_orders_delivered) AS total_order_demand
                FROM {selected_view}
                WHERE ((order_year*100) + order_month) between 
                            (({params.start_year}*100)+{params.start_month}) and 
                            (({params.end_year}*100) + {params.end_month})
                      AND delivery_district <> '' 
                      AND delivery_district IS NOT NULL
                      AND delivery_state IS NOT NULL 
                      AND delivery_state <> ''
                      and domain_name = 'Retail' and sub_domain = 'B2C'
            """

        if state:
            query_template += f"AND upper(delivery_state) = upper('{state}')"
        
        if bool(category) and (category != 'None'):
            query_template += f" AND upper(category)=upper('{category}')"

        if bool(sub_category) and (sub_category != 'None'):
            query_template += f" AND upper(sub_category)=upper('{sub_category}')"
        
        query_template += f"""
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
                WHERE 
                      ((foslm.order_year*100) + foslm.order_month) between 
                            (({params.start_year}*100)+{params.start_month}) and 
                            (({params.end_year}*100) + {params.end_month})
                      AND td.delivery_district <> '' 
                      AND upper(td.delivery_district) <> upper('undefined') 
                      AND td.delivery_district IS NOT NULL 
                      and foslm.domain_name = 'Retail' and foslm.sub_domain='B2C' """
        
        if bool(category) and (category != 'None'):
            query_template+= f" AND upper(foslm.category)=upper('{category}')"

        if bool(sub_category) and (sub_category != 'None'):
            query_template+= f" AND upper(foslm.sub_category)=upper('{sub_category}')"

        if state:
            query_template+= f"AND upper(foslm.delivery_state) = upper('{state}')"
        
        query_template+= """
                GROUP BY foslm.order_month, foslm.order_year, td.delivery_district
                ORDER BY foslm.order_year, foslm.order_month, total_orders_delivered DESC
            )
            SELECT * FROM FinalResult;
        """


        df = self.db_utility.execute_query(query_template)
        return df

    @log_function_call(ondcLogger)
    def fetch_overall_cumulative_sellers(self, start_date, end_date, category=None,
                                         sub_category=None, domain_name=None, state=None, seller_type='Total'):
        table_name = constant.ACTIVE_TOTAL_SELLER_TBL
        aggregate_value= "'AGG'"
        seller_column = 'total_sellers' if seller_type == 'Total' else 'active_sellers'
        parameters = self.get_query_month_parameters(start_date, end_date)

        query = f"""
            SELECT 
                mnth_val as order_month,
                year_val as order_year,
                max({seller_column}) as total_orders_delivered
            FROM 
                {table_name}
            WHERE
                ((year_val*100) + mnth_val) between
                    (({parameters['start_year']} * 100) + {parameters['start_month']})
                    and
                    (({parameters['end_year']} * 100) + {parameters['end_month']})
                and seller_district = {aggregate_value}
                and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregate_value})
                and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregate_value})
                and  upper(seller_state) { f"=upper('{state}') " if state else '='+aggregate_value}
            group by 1, 2
            order by ((year_val*100) + mnth_val)
        """

        df = self.db_utility.execute_query(query, parameters)
        
        return df

    @log_function_call(ondcLogger)
    def fetch_overall_top_states_hyperlocal_orders(self, start_date, end_date, category=None, sub_category=None,
                                                   domain_name=None, state=None):

        selected_view = constant.MONTHLY_DISTRICT_TABLE
        if (category):
            selected_view = constant.CAT_MONTHLY_DISTRICT_TABLE
        if(sub_category):
            selected_view = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE

        params = DotDict(self.get_query_month_parameters(start_date, end_date))

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
                    ((order_year * 100) + order_month) between
                        (({params.start_year} * 100) + {params.start_month})
                            and 
                        (({params.end_year} * 100) + {params.end_month})
                    AND delivery_state != 'MISSING'
                    AND delivery_state is not NULL
                    AND domain_name = 'Retail' and sub_domain = 'B2C'
        """
        
        if bool(category) and (category != 'None'):
            base_query += f" AND upper(category)=upper('{category}')"

        if bool(sub_category) and (sub_category != 'None'):
            base_query += f" AND upper(sub_category)=upper('{sub_category}')"

        if state:
            base_query += f" AND upper(delivery_state) = upper('{state}')"

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
                    ((om.order_year * 100) + om.order_month) between
                        (({params.start_year} * 100) + {params.start_month})
                            and 
                        (({params.end_year} * 100) + {params.end_month})
                    and om.domain_name = 'Retail' and om.sub_domain = 'B2C'
        """

        if state:
            base_query += f" AND upper(om.delivery_state) = upper('{state}')"
        
        if bool(category) and (category != 'None'):
            base_query += f" AND upper(om.category)=upper('{category}')"

        if bool(sub_category) and (sub_category != 'None'):
            base_query += f" AND upper(om.sub_category)=upper('{sub_category}')"

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
        df = self.db_utility.execute_query(base_query)
        return df

    @log_function_call(ondcLogger)
    def fetch_overall_top_district_hyperlocal_orders(self, start_date, end_date, category=None, sub_category=None,
                                                     domain_name=None, state=None):
        selected_view = constant.MONTHLY_DISTRICT_TABLE
        if (category):
            selected_view = constant.CAT_MONTHLY_DISTRICT_TABLE
        if(sub_category):
            selected_view = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE

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
                    ((order_year * 100) + order_month) between
                        (({parameters['start_year']} * 100) + {parameters['start_month']})
                            and 
                        (({parameters['end_year']} * 100) + {parameters['end_month']})
                    AND delivery_district <> '' AND UPPER(delivery_district) <> 'UNDEFINED'
                    AND delivery_district IS NOT NULL
                    AND delivery_district <> ''
                    AND domain_name = 'Retail' 
                    AND sub_domain = 'B2C'
        """

        if bool(category) and (category != 'None'):
            base_query += f" AND upper(category)=upper('{category}')"

        if bool(sub_category) and (sub_category != 'None'):
            base_query += f" AND upper(sub_category)=upper('{sub_category}')"
        
        if state:
            base_query += f" AND upper(delivery_state) = upper('{state}')"

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
                    ((om.order_year * 100) + om.order_month) between
                        (({parameters['start_year']} * 100) + {parameters['start_month']})
                            and 
                        (({parameters['end_year']} * 100) + {parameters['end_month']})
                    and om.domain_name = 'Retail' and om.sub_domain = 'B2C'
        """

        if state:
            base_query += f" AND upper(om.delivery_state) = upper('{state}')"
        
        if bool(category) and (category != 'None'):
            base_query += f" AND upper(category)=upper('{category}')"

        if bool(sub_category) and (sub_category != 'None'):
            base_query += f" AND upper(sub_category)=upper('{sub_category}')"

        base_query += """
                GROUP BY 
                    om.order_month, om.order_year, om.delivery_district
                ORDER BY 
                    om.order_year, om.order_month, intrastate_orders_percentage DESC
            )
            SELECT * FROM FinalResult 
            where intrastate_orders_percentage > 0
        """

        df = self.db_utility.execute_query(base_query)
        return df

    @log_function_call(ondcLogger)
    def fetch_overall_top5_seller_states(self, start_date, end_date, category=None, sub_category=None, domain='Retail',
                                 state=None):

        table_name = constant.MONTHLY_DISTRICT_TABLE

        if (category):
            table_name = constant.CAT_MONTHLY_DISTRICT_TABLE
        if(sub_category):
            table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE

        params = DotDict(self.get_query_month_parameters(start_date, end_date))
        query = f"""
            SELECT 
                sub.delivery_state,
                -- COALESCE(NULLIF(TRIM(sub.seller_state), ''), 'Missing') AS seller_state,
                sub.seller_state,
                sub.order_demand,
                sub.flow_percentage as flow_percentage
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
                    where 
                        ((swdlo.order_year * 100) + swdlo.order_month) between 
                        (({params.start_year}*100) + {params.start_month}) and
                        (({params.end_year}*100) + {params.end_month})
                    AND swdlo.domain_name = 'Retail' AND swdlo.sub_domain = 'B2C'
                    AND swdlo.delivery_state <> ''

                    GROUP BY swdlo.delivery_state
                ) total ON om.delivery_state = total.delivery_state
                WHERE 
                    ((om.order_year*100) + om.order_month) between
                    (({params.start_year}*100) + {params.start_month}) and
                        (({params.end_year}*100) + {params.end_month})
                    AND om.domain_name = 'Retail'
                    AND om.sub_domain = 'B2C'      
        """

        if state:
            query += f" AND upper(om.delivery_state) = upper('{state}')"
        
        if bool(category) and (category != 'None'):
            query += f" AND upper(category)=upper('{category}')"
        
        if bool(sub_category) and (sub_category != 'None'):
            query += f" AND upper(sub_category)=upper('{sub_category}')"

        query += """
                GROUP BY 
                    om.delivery_state, om.seller_state, total.total_orders
            ) sub
            WHERE sub.rn <= 4
            and sub.seller_state != ''
            and sub.seller_state is not NULL
            ORDER BY sub.delivery_state, sub.flow_percentage DESC;
        """
        df = self.db_utility.execute_query(query)
        return df

    @log_function_call(ondcLogger)
    def fetch_overall_top5_seller_districts(self, start_date, end_date, category=None, sub_category=None, domain='Retail',
                                    state=None, district=None):

        domain = 'Retail' if domain is None else domain
        table_name = constant.MONTHLY_DISTRICT_TABLE

        if (category):
            table_name = constant.CAT_MONTHLY_DISTRICT_TABLE
        if(sub_category):
            table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE

        params = DotDict(self.get_query_month_parameters(start_date, end_date))
        query = f"""
            SELECT 
                sub.delivery_district,
                -- COALESCE(NULLIF(TRIM(sub.seller_district), ''), 'Missing') AS seller_district,
                sub.seller_district,
                sub.order_demand,
                sub.flow_percentage AS flow_percentage
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
                    WHERE 
                        ((swdlo.order_year*100) + swdlo.order_month) between 
                        (({params.start_year}*100) + {params.start_month}) and
                        (({params.end_year}*100) + {params.end_month})
                    AND swdlo.domain_name = 'Retail'
                    AND swdlo.sub_domain = 'B2C'
                    AND swdlo.delivery_district <> ''
                    AND swdlo.seller_district <> ''
                    AND swdlo.seller_district is not NULL
        """

        if state:
            query += f" AND upper(swdlo.delivery_state) = upper('{state}')"

        if bool(category) and (category != 'None'):
            query += f" AND upper(category)=upper('{category}')"
        
        if bool(sub_category) and (sub_category != 'None'):
            query += f" AND upper(sub_category)=upper('{sub_category}')"

        query += f"""
                    GROUP BY swdlo.delivery_district
                ) total ON upper(om.delivery_district) = upper(total.delivery_district)
                where ((om.order_year*100) + om.order_month) between 
                        (({params.start_year}*100) + {params.start_month}) and
                        (({params.end_year}*100) + {params.end_month})
                    AND om.domain_name = 'Retail'
                    AND om.sub_domain = 'B2C'
        """

        if state:
            query += f" AND upper(om.delivery_state) = upper('{state}')"
        
        if district:
            query += f" AND upper(om.delivery_district) = upper('{district}')"

        if bool(category) and (category != 'None'):
            query += f" AND upper(om.category)=upper('{category}')"
        
        if bool(sub_category) and (sub_category != 'None'):
            query += f" AND upper(om.sub_category)=upper('{sub_category}')"

        query += """
                GROUP BY 
                    om.delivery_district, om.seller_district, total.total_orders
            ) sub
            WHERE sub.rn <= 4
            and sub.seller_district != ''
            ORDER BY sub.delivery_district, sub.flow_percentage DESC;
        """

        df = self.db_utility.execute_query(query)
        return df

    @log_function_call(ondcLogger)
    def fetch_district_count(self, start_date, end_date,
                                                  category=None, sub_category=None,
                                                  domain='Retail', state=None):
        domain = 'Retail' if domain is None else domain

        params = DotDict(self.get_query_month_parameters(start_date, end_date))
        table_name = constant.MONTHLY_DISTRICT_TABLE

        if (category):
            table_name = constant.CAT_MONTHLY_DISTRICT_TABLE
        if(sub_category):
            table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE
        
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

        query += " AND domain_name = %s AND sub_domain = 'B2C'"
        parameters.append(domain)

        if bool(category) and (category != 'None'):
            query += " AND category=%s"
            parameters.append(category)
        
        if bool(sub_category) and (sub_category != 'None'):
            query += " AND sub_category=%s"
            parameters.append(sub_category)

        query += " group by delivery_state_code, delivery_state"
        district_count = self.db_utility.execute_query(query, parameters)

        return district_count

    @log_function_call(ondcLogger)
    def fetch_cumulative_orders_statedata_summary(self, start_date, end_date,
                                                  category=None, sub_category=None,
                                                  domain='Retail', state=None):

        params = DotDict(self.get_query_month_parameters(start_date, end_date))
        table_name = constant.MONTHLY_DISTRICT_TABLE
        if (category):
            table_name = constant.CAT_MONTHLY_DISTRICT_TABLE
        if(sub_category):
            table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE
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

                ((order_year*100) + order_month) between 
                    (({params.start_year}*100) + {params.start_month}) and
                    (({params.end_year}*100) + {params.end_month}) and
                domain_name = 'Retail' and sub_domain = 'B2C'
        '''
        conditions = []

        if state:
            conditions.append(f"AND upper(delivery_state) = upper('{state}')")
        
        if bool(category) and (category != 'None'):
            conditions.append(f" AND category='{category}'")

        if bool(sub_category) and (sub_category != 'None'):
            conditions.append(f" AND sub_category='{sub_category}'")

        conditions_str = ' '.join(conditions)
        query = query + conditions_str + '''
            GROUP BY delivery_state_code, delivery_state, delivery_district 
            ORDER BY delivery_state_code, total_orders_delivered DESC
        '''
        
        aggregated_df = self.db_utility.execute_query(query)

        return aggregated_df

    @log_function_call(ondcLogger)
    def fetch_overall_active_sellers(self, start_date, end_date, category=None,
                                     sub_category=None, domain='Retail', state=None):

        params = DotDict(self.get_query_month_parameters(start_date, end_date))
        table_name = constant.ACTIVE_TOTAL_SELLER_TBL
        aggregate_value = "'AGG'"

        query = f"""
            SELECT 
                seller_state AS seller_state,
                seller_state_code AS seller_state_code,
                max(total_sellers)::numeric AS active_sellers_count
            FROM 
                {table_name}
            WHERE
                ((year_val*100) + mnth_val) =
                    (({params.end_year} * 100) + {params.end_month})
                and seller_state not in ('Missing', 'Misssing') 
                
                and seller_district = {aggregate_value}
                and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregate_value})
                and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregate_value})
                and  upper(seller_state) { f"=upper('{state}') " if state else '<>'+aggregate_value}
            group by 1,2
        """
        
        df = self.db_utility.execute_query(query)
        
        return df


    # @log_function_call(ondcLogger)
    # def fetch_overall_active_sellers_statedata(self, start_date, end_date,
    #                                            category=None, sub_category=None,
    #                                            domain='Retail', state=None):
    #     table_name = constant.MONTHLY_PROVIDERS
    #     params = DotDict(self.get_query_month_parameters(start_date, end_date))
    #     query = f"""
    #         SELECT 
    #             seller_state AS seller_state,
    #             seller_state_code AS seller_state_code,
    #             -- seller_district AS seller_district,
    #             COUNT(DISTINCT TRIM(LOWER(provider_key))) AS active_sellers_count
    #         FROM 
    #             {table_name}
    #         WHERE
    #             (order_year > %s OR (order_year = %s AND order_month >= %s))
    #             AND (order_year < %s OR (order_year = %s AND order_month <= %s))
    #             AND seller_state <> ''
    #             AND seller_state is not null
    #             AND seller_district is not null
    #             AND seller_district <> ''
    #     """

    #     parameters = [params.start_year, params.start_year, params.start_month,
    #                   params.end_year, params.end_year, params.end_month]

    #     conditions = []

    #     if state:
    #         conditions.append("AND upper(seller_state) = upper(%s)")
    #         parameters.append(state)
        
    #     # if bool(category) and (category != 'None'):
    #     #     conditions.append(" AND category=%s")
    #     #     parameters.append(category)
    #     # if bool(sub_category) and (sub_category != 'None'):
    #     #     conditions.append(" AND sub_category=%s")
    #     #     parameters.append(sub_category)

    #     conditions_str = ' '.join(conditions)
    #     query = query + conditions_str + " GROUP BY  seller_state, seller_state_code"

    #     df = self.db_utility.execute_query(query, parameters)
        
    #     return df


    @log_function_call(ondcLogger)
    def fetch_cumulative_orders_statewise_summary(self, start_date, end_date,
                                                  category=None, sub_category=None, domain='Retail', state=None):
        table_name = constant.MONTHLY_DISTRICT_TABLE
        if (category):
            table_name = constant.CAT_MONTHLY_DISTRICT_TABLE
        if(sub_category):
            table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE
        
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
                    ((order_year*100)+order_month) between 
                        (({params.start_year} * 100) + {params.start_month}) 
                            and 
                        (({params.end_year} * 100) + {params.end_month})
                        and domain_name = 'Retail' and sub_domain = 'B2C'
            """

        if state:
            query += f" AND upper(delivery_state) = upper('{state}')"

        if bool(category) and (category != 'None'):
            query += f" AND upper(category) = upper('{category}')"

        if sub_category:
            query += f" AND upper(sub_category) = upper('{sub_category}')"

        query  += ' GROUP BY delivery_state_code, delivery_state ORDER BY total_orders DESC'

        
        aggregated_df = self.db_utility.execute_query(query)
        return aggregated_df


    @log_function_call(ondcLogger)
    def fetch_category_penetration_orders(self, start_date, end_date, category=None, sub_category=None, domain='Retail',
                                          state=None):
        selected_view = constant.SUB_CATEGORY_PENETRATION_TABLE
        # params = DotDict(self.get_query_month_parameters(start_date, end_date))
        # parameters = [params.start_year, params.start_year, params.start_month,
        #               params.end_year, params.end_year, params.end_month]
        parameters = [start_date, end_date]

        query = f'''
            SELECT 
                COALESCE(category, 'Missing') AS category,
                COALESCE(sub_category, 'Missing') AS sub_category,
                SUM(total_orders_delivered) AS order_demand  
            FROM 
                {selected_view} 
            WHERE 
                order_date between %s and %s
        '''
                # (order_year > %s OR (order_year = %s AND order_month >= %s))
                # AND (order_year < %s OR (order_year = %s AND order_month <= %s))

        if bool(category) and (category != 'None'):
            query += f" And category='{category}'"
        if bool(sub_category) and (sub_category != 'None'):
            query += f" And sub_category='{sub_category}'"
        
        if state:
            query += " AND upper(delivery_state) = upper(%s)"
            parameters.append(state)

        query += '''
            GROUP BY 
                COALESCE(category, 'Missing'),
                COALESCE(sub_category, 'Missing')
            ORDER BY 
                order_demand DESC;
        '''
        df = self.db_utility.execute_query(query, parameters)
        
        return df

    @log_function_call(ondcLogger)
    def fetch_category_penetration_sellers(self, start_date, end_date, category=None, sub_category=None, domain='Retail',
                                           state=None, seller_type='Total'):
        seller_column = 'total_sellers' if seller_type == 'Total' else 'active_sellers'
        params = DotDict(self.get_query_month_parameters(start_date, end_date))
        parameters = []
        table_name = constant.ACTIVE_TOTAL_SELLER_TBL
        aggregated_value= "'AGG'"
        
        query = f'''
                select 
                    category, 
                    case 
                        when sub_category = {aggregated_value} then 'ALL' 
                        else sub_category 
                    end as sub_category, 
                    max({seller_column}) as active_sellers_count
                from 
                    {table_name}
                where ((year_val*100)+mnth_val) =  (({params.end_year}*100)+{params.end_month})
                    and upper(category) { " = upper('"+ category +"') " if category else ' <> ' + aggregated_value}
                    { (" and upper(sub_category) = upper('" + sub_category + "') ") if sub_category else ' '}
                    and upper(seller_state) = {aggregated_value} 
                    and category <>'Undefined' 
                    and seller_state <> ''
                group by 1,2
                order by category
                '''
        df = self.db_utility.execute_query(query, parameters)

        return df

    @log_function_call(ondcLogger)
    def fetch_states_orders(self, start_date, end_date, category=None,
                            sub_category=None, domain_name=None, state=None):

        table_name = constant.MONTHLY_DISTRICT_TABLE
        if (category):
            table_name = constant.CAT_MONTHLY_DISTRICT_TABLE
        if(sub_category):
            table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE

        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        start_month = stdate_obj.month
        start_year = stdate_obj.year
        end_month = edate_obj.month
        end_year = edate_obj.year

        # parameters = [start_date, end_date]
        parameters = [start_year, start_year, start_month, end_year, end_year, end_month]

        # params = DotDict(self.get_query_month_parameters(start_date, end_date))

        query = f"""
            SELECT 
                delivery_state,
                sum(total_orders_delivered) AS total_orders_delivered
            FROM 
                {table_name}
            WHERE 
                (order_year > %s OR (order_year = %s AND order_month >= %s))
                AND (order_year < %s OR (order_year = %s AND order_month <= %s))
                and delivery_state is not null
                and delivery_state <> ''
        """

        if bool(category) and (category != 'None'):
            query += constant.category_sub_query
            parameters.append(category)
        if bool(sub_category) and (sub_category != 'None'):
            query += constant.sub_category_sub_query
            parameters.append(sub_category)
        if domain_name:
            query += constant.domain_sub_query
            parameters.append(domain_name)
        if state:
            query += constant.delivery_state_sub_query
            parameters.append(state)

        query += """
                GROUP BY 
                    delivery_state
                ORDER BY 
                    total_orders_delivered DESC
        """

        df = self.db_utility.execute_query(query, parameters)
        return df

    @log_function_call(ondcLogger)
    def fetch_max_state_orders(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                               state=None):

        table_name = constant.MONTHLY_DISTRICT_TABLE
        if (category):
            table_name = constant.CAT_MONTHLY_DISTRICT_TABLE
        if(sub_category):
            table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE

        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        start_month = stdate_obj.month
        start_year = stdate_obj.year
        end_month = edate_obj.month
        end_year = edate_obj.year

        # parameters = [start_date, end_date]
        params = [start_year, start_year, start_month, end_year, end_year, end_month]

        query = f"""
            SELECT 
                'State' AS record_type,
                delivery_state as location,
                order_month, order_year,
                order_demand
            FROM 
                (
                    SELECT
                        delivery_state,
                        order_month, order_year,
                        SUM(total_orders_delivered) AS order_demand,
                        RANK() OVER (PARTITION BY delivery_state ORDER BY SUM(total_orders_delivered) DESC) AS rank
                    FROM
                        {table_name}
                    WHERE 
                        (order_year > %s OR (order_year = %s AND order_month >= %s))
                        AND (order_year < %s OR (order_year = %s AND order_month <= %s))
                        and delivery_state <> ''
        """

        if state:
            query += constant.delivery_state_sub_query
            params.append(state)

        if bool(category) and (category != 'None'):
            query += constant.category_sub_query
            params.append(category)

        if bool(sub_category) and (sub_category != 'None'):
            query += constant.sub_category_sub_query
            params.append(sub_category)

        if domain_name:
            query += constant.domain_sub_query
            params.append(domain_name)

        query += """
                    GROUP BY
                        delivery_state, order_month, order_year
                    ORDER BY
                        delivery_state, rank, order_month, order_year
                ) AS RankedOrders
            WHERE 
                rank = 1
            ORDER BY 
                order_demand DESC
            LIMIT 1
        """

        df = self.db_utility.execute_query(query, params)
        return df
    
    def fetch_max_district_orders(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                                  state=None):

        # selected_view = self.get_table_name(category, sub_category)

        # params = [start_date, end_date]

        table_name = constant.MONTHLY_DISTRICT_TABLE
        if (category):
            table_name = constant.CAT_MONTHLY_DISTRICT_TABLE
        if(sub_category):
            table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE

        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        start_month = stdate_obj.month
        start_year = stdate_obj.year
        end_month = edate_obj.month
        end_year = edate_obj.year

        # parameters = [start_date, end_date]
        params = [start_year, start_year, start_month, end_year, end_year, end_month]

        query = f"""
            SELECT 
                'District' AS record_type,
                delivery_district as location,
                order_month, order_year,
                order_count
            FROM 
                (
                    SELECT
                        delivery_district,
                        order_month, order_year,
                        SUM(total_orders_delivered) AS order_count,
                        RANK() OVER (PARTITION BY delivery_district ORDER BY SUM(total_orders_delivered)  DESC) AS rank
                    FROM
                        {table_name}
                    WHERE 
                        (order_year > %s OR (order_year = %s AND order_month >= %s))
                        AND (order_year < %s OR (order_year = %s AND order_month <= %s))
                        and delivery_district <> '' and upper(delivery_district) <> upper('Undefined')
        """

        if state:
            query += constant.delivery_state_sub_query
            params.append(state)

        if bool(category) and (category != 'None'):
            query += constant.category_sub_query
            params.append(category)

        if bool(sub_category) and (sub_category != 'None'):
            query += constant.sub_category_sub_query
            params.append(sub_category)

        if domain_name:
            query += constant.domain_sub_query
            params.append(domain_name)

        query += """
                    GROUP BY
                        delivery_district, order_month, order_year
                    ORDER BY
                        delivery_district, rank, order_month, order_year
                ) AS RankedOrders
            WHERE 
                rank = 1
            ORDER BY 
                order_count DESC
            LIMIT 1
        """

        df = self.db_utility.execute_query(query, params)
        return df


    @log_function_call(ondcLogger)
    def fetch_max_state_sellers(self, start_date, end_date, category=None, sub_category=None, domain='Retail', state=None):

        selected_view = constant.MONTHLY_PROVIDERS

        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        start_month = stdate_obj.month
        start_year = stdate_obj.year
        end_month = edate_obj.month
        end_year = edate_obj.year

        # parameters = [start_date, end_date]
        params = [start_year, start_year, start_month, end_year, end_year, end_month]

        query = f"""
            SELECT 
                'State' AS record_type,
                seller_state as location,
                order_year, order_month,
                seller_count
            FROM 
                (
                    SELECT
                        seller_state,
                        order_year, order_month,
                        COUNT(DISTINCT trim(lower(provider_key))) AS seller_count,
                        RANK() OVER (PARTITION BY seller_state ORDER BY COUNT(DISTINCT provider_key) DESC) AS rank
                    FROM
                        {selected_view}
                    WHERE 
                        (order_year > %s OR (order_year = %s AND order_month >= %s))
                        AND (order_year < %s OR (order_year = %s AND order_month <= %s))
                        and seller_state <> ''
        """

        if state:
            query += constant.seller_state_sub_query
            params.append(state)

        if bool(category) and (category != 'None'):
            query += constant.category_sub_query
            params.append(category)

        if bool(sub_category) and (sub_category != 'None'):
            query += constant.sub_category_sub_query
            params.append(sub_category)

        query += f"""
                    GROUP BY
                        seller_state, order_year, order_month
                    HAVING COUNT(DISTINCT provider_key) > {constant.ACTIVE_SELLERS_MASKING} 
                    ORDER BY
                        seller_state, rank, order_year, order_month
                ) AS RankedOrders
            WHERE 
                rank = 1
            ORDER BY 
                seller_count DESC
            LIMIT 1
        """

        df = self.db_utility.execute_query(query, params)
        return df


    @log_function_call(ondcLogger)
    def fetch_max_district_sellers(self, start_date, end_date, category=None, sub_category=None, domain='Retail', state=None):

        selected_view = constant.MONTHLY_PROVIDERS
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        start_month = stdate_obj.month
        start_year = stdate_obj.year
        end_month = edate_obj.month
        end_year = edate_obj.year

        # parameters = [start_date, end_date]
        params = [start_year, start_year, start_month, end_year, end_year, end_month]

        query = f"""
                SELECT 
                    'District' AS record_type,
                    seller_district as location,
                    order_year, order_month,
                    seller_count
                FROM 
                    (
                        SELECT
                            seller_district,
                            order_year, order_month,
                            COUNT(DISTINCT provider_key) AS seller_count,
                            RANK() OVER (PARTITION BY seller_district ORDER BY COUNT(DISTINCT provider_key) DESC) AS rank
                        FROM
                            {selected_view}
                        WHERE 
                            (order_year > %s OR (order_year = %s AND order_month >= %s))
                            AND (order_year < %s OR (order_year = %s AND order_month <= %s))
                            and seller_district <> '' and upper(seller_district) <> upper('Undefined')
            """

        if state:
            query += constant.seller_state_sub_query
            params.append(state)

        if bool(category) and (category != 'None'):
            query += constant.category_sub_query
            params.append(category)

        if bool(sub_category) and (sub_category != 'None'):
            query += constant.sub_category_sub_query
            params.append(sub_category)

        query += f"""
                        GROUP BY
                            seller_district, order_year, order_month
                        HAVING COUNT(DISTINCT provider_key) > {constant.ACTIVE_SELLERS_MASKING}
                        ORDER BY
                            seller_district, rank, order_year, order_month
                    ) AS RankedOrders
                WHERE 
                    rank = 1
                ORDER BY 
                    seller_count DESC
                LIMIT 1
            """

        df = self.db_utility.execute_query(query, params)
        return df
    

    @log_function_call(ondcLogger)
    def fetch_state_sellers(self, start_date, end_date, category=None, sub_category=None, domain='Retail', state=None):

        table_name = constant.MONTHLY_PROVIDERS

        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        start_month = stdate_obj.month
        start_year = stdate_obj.year
        end_month = edate_obj.month
        end_year = edate_obj.year

        # parameters = [start_date, end_date]
        parameters = [start_year, start_year, start_month, end_year, end_year, end_month]

        # Base SQL query
        query = f"""
            SELECT 
                seller_state, 
                COUNT(DISTINCT trim(lower(provider_key))) as active_sellers_count
            FROM 
                {table_name}
            WHERE 
                (order_year > %s OR (order_year = %s AND order_month >= %s))
                AND (order_year < %s OR (order_year = %s AND order_month <= %s))
        """

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

        df = self.db_utility.execute_query(query, parameters)
        return df

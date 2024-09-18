

__author__ = "Bikas Pandey"

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

    

    
    def fetch_state_sellers(self, start_date, end_date, category=None, sub_category=None, domain=None, state=None):

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

    @log_function_call(ondcLogger)
    def fetch_logistic_searched_data(self, city):
        query = f"""
            WITH A AS (
            SELECT DISTINCT pick_up_pincode, district 
            FROM {constant.LOGISTIC_SEARCH_PINCODE_TBL}
            WHERE district = '{city}'
            )

            SELECT 
                ls.time_of_day, 
                ls.pick_up_pincode, 
                sum(ls.searched) as searched_data,
                sum(ls.confirmed) as confirmed_data, 
                sum(ls.assigned) as assigned_data, 
                A.district
            FROM {constant.LOGISTIC_SEARCH_TBL} ls 
            INNER JOIN A ON ls.pick_up_pincode = A.pick_up_pincode

            group by ls.time_of_day, ls.pick_up_pincode, A.district order by ls.pick_up_pincode, ls.time_of_day
            """
        import pdb 
        pdb.set_trace()
        df = self.db_utility.execute_query(query)
        return df
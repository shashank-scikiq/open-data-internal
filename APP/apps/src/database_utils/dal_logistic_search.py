

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


    @log_function_call(ondcLogger)
    def fetch_logistic_searched_data(self, start_date, end_date, city):
        where_condition = " district in ('Bangalore', 'Bengaluru Rural', 'Bengaluru Urban') " \
            if city == 'Bangalore' else "state = 'DELHI'"
        
        query = f"""
            (SELECT 
                    ls.time_of_day as time_of_day, 
                    ls.pick_up_pincode, 
                    case
                        when sum(ls.searched) = 0 or sum(ls.confirmed) = 0 then 0 
                        else round((sum(ls.confirmed)/sum(ls.searched))*100.0, 1) 
                    end as conversion_rate,
                    case
                        when sum(ls.searched) = 0 or sum(ls.assigned) = 0 then 0 
                        else round((sum(ls.assigned)/sum(ls.searched))*100.0, 1) 
                    end as assigned_rate,
                    sum(ls.searched) as searched_data
                from {constant.LOGISTIC_SEARCH_PINCODE_TBL} ls
                    where date between '{start_date}' and '{end_date}' and {where_condition}
                group by ls.time_of_day, ls.pick_up_pincode )

                    Union
                (SELECT 
                    'Overall' as time_of_day,
                    ls.pick_up_pincode, 
                    case
                        when sum(ls.searched) = 0 or sum(ls.confirmed) = 0 then 0 
                        else round((sum(ls.confirmed)/sum(ls.searched))*100.0, 1) 
                    end as conversion_rate,
                    case
                        when sum(ls.searched) = 0 or sum(ls.assigned) = 0 then 0 
                        else round((sum(ls.assigned)/sum(ls.searched))*100.0, 1) 
                    end as assigned_rate,
                    sum(ls.searched) as searched_data
                from {constant.LOGISTIC_SEARCH_PINCODE_TBL} ls
                    where date between '{start_date}' and '{end_date}' and {where_condition} group by ls.pick_up_pincode  )
                    order by pick_up_pincode, time_of_day"""
        
        df = self.db_utility.execute_query(query)
        return df
    
    @log_function_call(ondcLogger)
    def fetch_logistic_searched_top_card_data(self, start_date, end_date, city):
        where_condition = " district in ('Bangalore', 'Bengaluru Rural', 'Bengaluru Urban') " \
            if city == 'Bangalore' else " state = 'DELHI' "
        
        query = f"""
            WITH A AS (
                SELECT 
                    ls.time_of_day,
                    CASE
                        WHEN SUM(ls.searched) = 0 OR SUM(ls.confirmed) = 0 THEN 0 
                        ELSE ROUND((SUM(ls.confirmed) / SUM(ls.searched)) * 100.0, 1) 
                    END AS total_conversion_percentage,
                    CASE
                        WHEN SUM(ls.searched) = 0 OR SUM(ls.assigned) = 0 THEN 0 
                        ELSE ROUND((SUM(ls.assigned) / SUM(ls.searched)) * 100.0, 1) 
                    END AS total_assigned_percentage,
                    SUM(ls.searched) AS searched_data
                FROM {constant.LOGISTIC_SEARCH_PINCODE_TBL} ls
                    where date between '{start_date}' and '{end_date}' and {where_condition} 
                GROUP BY ls.time_of_day
            ),
            B AS (
                SELECT time_of_day
                FROM (VALUES
                    ('3am-6am'),
                    ('6am-8am'),
                    ('8am-10am'),
                    ('10am-12pm'),
                    ('12pm-3pm'),
                    ('3pm-6pm'),
                    ('6pm-9pm'),
                    ('9pm-12am'),
                    ('12am-3am')
                ) AS time_ranges(time_of_day)
            )
            SELECT 
                B.time_of_day, 
                COALESCE(A.total_conversion_percentage, 0) AS total_conversion_percentage, 
                COALESCE(A.total_assigned_percentage, 0) AS total_assigned_percentage, 
                COALESCE(A.searched_data, 0) AS searched_data
            FROM B
            LEFT JOIN A ON B.time_of_day = A.time_of_day

            UNION ALL
            SELECT 
                'Overall' AS time_of_day,
                CASE
                    WHEN SUM(ls.searched) = 0 OR SUM(ls.confirmed) = 0 THEN 0 
                    ELSE ROUND((SUM(ls.confirmed) / SUM(ls.searched)) * 100.0, 1) 
                END AS total_conversion_percentage,
                CASE
                    WHEN SUM(ls.searched) = 0 OR SUM(ls.assigned) = 0 THEN 0 
                    ELSE ROUND((SUM(ls.assigned) / SUM(ls.searched)) * 100.0, 1) 
                END AS total_assigned_percentage,
                SUM(ls.searched) AS searched_data
            FROM {constant.LOGISTIC_SEARCH_PINCODE_TBL} ls
            where date between '{start_date}' and '{end_date}' and {where_condition} ;
        """
        
        df = self.db_utility.execute_query(query)
        return df
    

    def fetch_logistic_searched_data_date_range(self):
        query = f"""
            select max(date), min(date)
            from {constant.LOGISTIC_SEARCH_PINCODE_TBL}
        """
        df = self.db_utility.execute_query(query)
        return df
    

    @log_function_call(ondcLogger)
    def get_total_searches_per_state(self, start_date=None, end_date=None):
        table_name = constant.LOGISTIC_SEARCH_PINCODE_TBL
        date_filter = ""
        if start_date and end_date:
            date_filter = f"WHERE date BETWEEN '{start_date}' AND '{end_date}'"
        
        query = f"""
        SELECT DISTINCT state, SUM(searched) AS total_searches, sum(confirmed) as order_confirmed
        FROM {table_name}
        {date_filter} 
        AND time_of_day IN ('3am-6am', '6am-8am', '8am-10am', '10am-12pm', '12pm-3pm', 
                      '3pm-6pm', '6pm-9pm', '9pm-12am', '12am-3am') 
        GROUP BY state
        ORDER BY total_searches DESC
        """
        
        df= self.db_utility.execute_query(query)
        return df


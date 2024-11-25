

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
                    (
                        SELECT 
                            ls.time_of_day AS time_of_day, 
                            ls.pick_up_pincode, 
                            CASE
                                WHEN SUM(ls.searched) = 0 OR SUM(ls.confirmed) = 0 THEN 0 
                                ELSE ROUND((SUM(ls.confirmed) / SUM(ls.searched)) * 100.0, 1) 
                            END AS conversion_rate,
                            CASE
                                WHEN SUM(ls.searched) = 0 OR SUM(ls.assigned) = 0 THEN 0 
                                ELSE ROUND((SUM(ls.assigned) / SUM(ls.searched)) * 100.0, 1) 
                            END AS assigned_rate,
                            SUM(ls.searched) AS searched_data,
                            CASE 
                                WHEN EXTRACT(DOW FROM MIN(ls.date)) IN (6, 0) THEN 'weekend' 
                                ELSE 'weekday'
                            END AS is_weekend
                        FROM ec2_all.logistic_search_pincode ls
                        WHERE ls.date BETWEEN '{start_date}' AND '{end_date}' AND {where_condition}'
                        GROUP BY ls.time_of_day, ls.pick_up_pincode
                    )
                    UNION
                    (
                        SELECT 
                            'Overall' AS time_of_day,
                            ls.pick_up_pincode, 
                            CASE
                                WHEN SUM(ls.searched) = 0 OR SUM(ls.confirmed) = 0 THEN 0 
                                ELSE ROUND((SUM(ls.confirmed) / SUM(ls.searched)) * 100.0, 1) 
                            END AS conversion_rate,
                            CASE
                                WHEN SUM(ls.searched) = 0 OR SUM(ls.assigned) = 0 THEN 0 
                                ELSE ROUND((SUM(ls.assigned) / SUM(ls.searched)) * 100.0, 1) 
                            END AS assigned_rate,
                            SUM(ls.searched) AS searched_data,
                            CASE 
                                WHEN EXTRACT(DOW FROM MIN(ls.date)) IN (6, 0) THEN 'weekend' 
                                ELSE 'weekday'
                            END AS is_weekend
                        FROM ec2_all.logistic_search_pincode ls
                        WHERE ls.date BETWEEN '{start_date}' AND '{end_date}' AND {where_condition}
                        GROUP BY ls.pick_up_pincode
                    )
                    ORDER BY pick_up_pincode, time_of_day

                    """

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
    def fetch_overall_total_searches(self, start_date=None, end_date=None):
        table_name = constant.LOGISTIC_SEARCH_PINCODE_TBL
        
        query = f"""
                    with 
                        req_table as (
                            select * 
                        from 
                            {table_name}
                        WHERE 
                            date BETWEEN '{start_date}' and '{end_date}'
                            AND time_of_day IN (
                                    '3am-6am', '6am-8am', '8am-10am', '10am-12pm', 
                                '12pm-3pm', '3pm-6pm', '6pm-9pm', '9pm-12am', '12am-3am'
                            )
                        )
                        (SELECT DISTINCT 
                                state, 
                            district,
                                time_of_day,
                                SUM(searched) AS total_searches, 
                                SUM(confirmed) AS order_confirmed
                        FROM 
                            req_table
                        GROUP BY 
                            1,2, 3)             
                        UNION ALL
                        (SELECT 
                            state,
                            district,
                            'Overall' AS time_of_day, 
                            SUM(searched) AS total_searches, 
                            SUM(confirmed) AS order_confirmed
                            FROM 
                            req_table
                            GROUP BY 
                            1,2)
                            UNION ALL
                            
                            (SELECT DISTINCT 
                                state, 
                            'All' as district,
                                time_of_day,
                                SUM(searched) AS total_searches, 
                                SUM(confirmed) AS order_confirmed
                        FROM 
                            req_table
                        GROUP BY 
                            1, 3)             
                        UNION ALL
                        (SELECT 
                            state,
                                'All' as district,
                                'Overall' AS time_of_day, 
                            SUM(searched) AS total_searches, 
                                SUM(confirmed) AS order_confirmed
                            FROM 
                            req_table
                            GROUP BY 
                        1,3)
                            
                            order by 1,2,3;
        """
        df= self.db_utility.execute_query(query)
        return df
    
    def fetch_total_searches_per_state(self, start_date, end_date, state):
        table_name = constant.LOGISTIC_SEARCH_PINCODE_TBL

        query = f"""
                    (
                    SELECT 
                            state,
                            district,
                            time_of_day,
                            SUM(searched) AS total_searches, 
                            SUM(confirmed) AS order_confirmed
                    FROM 
                        {table_name}
                    WHERE 
                        date BETWEEN '{start_date}' AND '{end_date}' AND upper(state)=upper('{state}')
                        AND time_of_day IN (
                            '3am-6am', '6am-8am', '8am-10am', '10am-12pm', 
                            '12pm-3pm', '3pm-6pm', '6pm-9pm', '9pm-12am', '12am-3am'
                        )
                    GROUP BY 
                        1,2,3)

                UNION ALL

                    (SELECT 
                        state,
                        district,
                        'Overall' AS time_of_day, 
                        SUM(searched) AS total_searches, 
                        SUM(confirmed) AS order_confirmed
                    FROM 
                        {table_name}
                    WHERE 
                        date BETWEEN '{start_date}' AND '{end_date}'
                        AND upper(state)=upper('{state}')
                        AND time_of_day IN (
                            '3am-6am', '6am-8am', '8am-10am', '10am-12pm', 
                            '12pm-3pm', '3pm-6pm', '6pm-9pm', '9pm-12am', '12am-3am'
                        )
                    GROUP BY 
                        1,2

                    ORDER BY 
                        total_searches DESC);
        """
        df= self.db_utility.execute_query(query)
        return df


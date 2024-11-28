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
    def fetch_logistic_searched_data(self, start_date, end_date, city, day_type='All'):
        where_condition = " district in ('Bangalore', 'Bengaluru Rural', 'Bengaluru Urban') " \
            if city == 'Bangalore' else "state = 'DELHI'"
        
        day_type_condition = " and extract(dow from date) in (6,0) " if day_type == 'Weekends' else (
            " and extract(dow from date) in (1,2,3,4,5)" if day_type == 'Week days' else ''
        )
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
                        WHERE ls.date BETWEEN '{start_date}' AND '{end_date}' AND {where_condition}
                        {day_type_condition}
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
                        {day_type_condition}
                        GROUP BY ls.pick_up_pincode
                    )
                    ORDER BY pick_up_pincode, time_of_day

                    """

        df = self.db_utility.execute_query(query)

        return df
    
    @log_function_call(ondcLogger)
    def fetch_logistic_searched_top_card_data(self, start_date, end_date, city, day_type='All'):
        table_name = constant.LOGISTIC_SEARCH_PINCODE_TBL

        condition = " district in ('Bangalore', 'Bengaluru Rural', 'Bengaluru Urban') " \
            if city == 'Bangalore' else ('' if not city else " state = 'DELHI' ")    
        
        day_type_condition = " and extract(dow from date) in (6,0) " if day_type == 'Weekends' else (
            " and extract(dow from date) in (1,2,3,4,5)" if day_type == 'Week days' else ''
        )

        query = f"""WITH A AS (
                SELECT 
                	state, 
                    ls.time_of_day,
                    CASE
                        WHEN SUM(ls.searched) = 0 OR SUM(ls.confirmed) = 0 THEN 0 
                        ELSE ROUND((SUM(ls.confirmed) / SUM(ls.searched)) * 100.0, 1) 
                    END AS total_conversion_percentage,
                    CASE
                        WHEN SUM(ls.searched) = 0 OR SUM(ls.assigned) = 0 THEN 0 
                        ELSE ROUND((SUM(ls.assigned) / SUM(ls.searched)) * 100.0, 1) 
                    END AS total_assigned_percentage,
                    SUM(ls.confirmed) AS confirmed_data,
                    SUM(ls.assigned) AS assigned_data,
                    SUM(ls.searched) AS searched_data
                FROM ec2_all.logistic_search_pincode ls
                    where date between '{start_date}' and '{end_date}' {' and ' + condition if condition else ''}
                    {day_type_condition}
                GROUP BY 1,2
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
            A.state as state,
                B.time_of_day, 
                COALESCE(A.total_conversion_percentage, 0) AS total_conversion_percentage, 
                COALESCE(A.total_assigned_percentage, 0) AS total_assigned_percentage,
                COALESCE(A.confirmed_data, 0) AS confirmed_data,
                COALESCE(A.assigned_data, 0) AS assigned_data, 
                COALESCE(A.searched_data, 0) AS searched_data
                
            FROM B
            LEFT JOIN A ON B.time_of_day = A.time_of_day

            UNION ALL
            SELECT 
            	state,
                'Overall' AS time_of_day,
                CASE
                    WHEN SUM(ls.searched) = 0 OR SUM(ls.confirmed) = 0 THEN 0 
                    ELSE ROUND((SUM(ls.confirmed) / SUM(ls.searched)) * 100.0, 1) 
                END AS total_conversion_percentage,
                CASE
                    WHEN SUM(ls.searched) = 0 OR SUM(ls.assigned) = 0 THEN 0 
                    ELSE ROUND((SUM(ls.assigned) / SUM(ls.searched)) * 100.0, 1) 
                END AS total_assigned_percentage,
                SUM(ls.confirmed) AS confirmed_data,
                SUM(ls.assigned) AS assigned_data,
                SUM(ls.searched) AS searched_data
            FROM {table_name} ls
            where date between '{start_date}' and '{end_date}' {' and ' + condition if condition else ''}
            {day_type_condition}
            group by 1;
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
    def fetch_overall_total_searches(self, start_date=None, end_date=None, day_type='All'):
        table_name = constant.LOGISTIC_SEARCH_PINCODE_TBL
        day_type_condition = " and extract(dow from date) in (6,0) " if day_type == 'Weekends' else (
            " and extract(dow from date) in (1,2,3,4,5)" if day_type == 'Week days' else ''
        )
        
        query = f"""
                    with 
                        req_table as (
                            select * 
                        from 
                            {table_name}
                        WHERE 
                            date BETWEEN '{start_date}' and '{end_date}'
                            {day_type_condition}
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
                                SUM(confirmed) AS order_confirmed,
                                CASE
                                    WHEN SUM(searched) = 0 OR SUM(confirmed) = 0 THEN 0 
                                    ELSE ROUND((SUM(confirmed) / SUM(searched)) * 100.0, 1) 
                                END AS total_conversion_percentage,
                                CASE
                                    WHEN SUM(searched) = 0 OR SUM(assigned) = 0 THEN 0 
                                    ELSE ROUND((SUM(assigned) / SUM(searched)) * 100.0, 1) 
                                END AS total_assigned_percentage
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
                            SUM(confirmed) AS order_confirmed,
                            CASE
                                WHEN SUM(searched) = 0 OR SUM(confirmed) = 0 THEN 0 
                                ELSE ROUND((SUM(confirmed) / SUM(searched)) * 100.0, 1) 
                            END AS total_conversion_percentage,
                            CASE
                                WHEN SUM(searched) = 0 OR SUM(assigned) = 0 THEN 0 
                                ELSE ROUND((SUM(assigned) / SUM(searched)) * 100.0, 1) 
                            END AS total_assigned_percentage
                        FROM 
                            req_table
                        GROUP BY 1,2)
                        UNION ALL
                            
                            (SELECT DISTINCT 
                                state, 
                            'All' as district,
                                time_of_day,
                                SUM(searched) AS total_searches, 
                                SUM(confirmed) AS order_confirmed,
                                CASE
                                    WHEN SUM(searched) = 0 OR SUM(confirmed) = 0 THEN 0 
                                    ELSE ROUND((SUM(confirmed) / SUM(searched)) * 100.0, 1) 
                                END AS total_conversion_percentage,
                                CASE
                                    WHEN SUM(searched) = 0 OR SUM(assigned) = 0 THEN 0 
                                    ELSE ROUND((SUM(assigned) / SUM(searched)) * 100.0, 1) 
                                END AS total_assigned_percentage
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
                                SUM(confirmed) AS order_confirmed,
                                CASE
                                    WHEN SUM(searched) = 0 OR SUM(confirmed) = 0 THEN 0 
                                    ELSE ROUND((SUM(confirmed) / SUM(searched)) * 100.0, 1) 
                                END AS total_conversion_percentage,
                                CASE
                                    WHEN SUM(searched) = 0 OR SUM(assigned) = 0 THEN 0 
                                    ELSE ROUND((SUM(assigned) / SUM(searched)) * 100.0, 1) 
                                END AS total_assigned_percentage
                            FROM 
                                req_table
                            GROUP BY 
                        1,3)
                            
                            order by 1,2,3;
        """
        df= self.db_utility.execute_query(query)
        return df
    
    def fetch_total_searches_per_state(self, start_date, end_date, state, day_type='All'):
        table_name = constant.LOGISTIC_SEARCH_PINCODE_TBL
        day_type_condition = " and extract(dow from date) in (6,0) " if day_type == 'Weekends' else (
            " and extract(dow from date) in (1,2,3,4,5)" if day_type == 'Week days' else ''
        )

        query = f"""with req_table as (
                    
                    select * from 
                        {table_name}
                    WHERE 
                        date BETWEEN '{start_date}' AND '{end_date}' AND upper(state)=upper('{state}')
                        {day_type_condition}
                        AND time_of_day IN (
                            '3am-6am', '6am-8am', '8am-10am', '10am-12pm', 
                            '12pm-3pm', '3pm-6pm', '6pm-9pm', '9pm-12am', '12am-3am'
                        )
                    )
                    (
                    SELECT 
                            state,
                            district,
                            time_of_day,
                            SUM(searched) AS total_searches, 
                            SUM(confirmed) AS order_confirmed,
                            CASE
                                    WHEN SUM(searched) = 0 OR SUM(confirmed) = 0 THEN 0 
                                    ELSE ROUND((SUM(confirmed) / SUM(searched)) * 100.0, 1) 
                                END AS total_conversion_percentage,
                                CASE
                                    WHEN SUM(searched) = 0 OR SUM(assigned) = 0 THEN 0 
                                    ELSE ROUND((SUM(assigned) / SUM(searched)) * 100.0, 1) 
                                END AS total_assigned_percentage
                    FROM 
                        req_table
                    GROUP BY 
                        1,2,3)

                UNION ALL

                    (SELECT 
                        state,
                        district,
                        'Overall' AS time_of_day, 
                        SUM(searched) AS total_searches, 
                        SUM(confirmed) AS order_confirmed,
                        CASE
                            WHEN SUM(searched) = 0 OR SUM(confirmed) = 0 THEN 0 
                            ELSE ROUND((SUM(confirmed) / SUM(searched)) * 100.0, 1) 
                        END AS total_conversion_percentage,
                        CASE
                            WHEN SUM(searched) = 0 OR SUM(assigned) = 0 THEN 0 
                            ELSE ROUND((SUM(assigned) / SUM(searched)) * 100.0, 1) 
                        END AS total_assigned_percentage
                    FROM 
                        req_table
                    GROUP BY 
                        1,2

                    ORDER BY 
                        total_searches DESC);
        """
        df= self.db_utility.execute_query(query)
        return df

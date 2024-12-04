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

        table_name = constant.LOGISTIC_SEARCH_PINCODE_TBL
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
                        FROM {table_name} ls
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
                        FROM {table_name} ls
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

        condition = ""
        if city == "New Delhi":
            condition = " state = 'DELHI' "
        elif city == "Bangalore":
            condition = " district in ('Bangalore', 'Bengaluru Rural', 'Bengaluru Urban') " 
        
        day_type_condition = " and extract(dow from date) in (6,0) " if day_type == 'Weekends' else (
            " and extract(dow from date) in (1,2,3,4,5)" if day_type == 'Week days' else ''
        )

        query = f"""
                with A as (
                    (SELECT 
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
                    FROM {table_name} ls
                    where date between '{start_date}' and '{end_date}' {' and ' + condition if condition else ''}
                    {day_type_condition} 
                        GROUP BY 1,2
                    )
                    UNION ALL (
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
                    group by 1
                    )
                    
                ),
                B AS (
                    select 
                        dd.delivery_state as state, 
                        td.time_of_day as time_of_day
                    from {constant.DIM_DISTRICTS} dd right join  (
                        SELECT 
                            time_of_day
                        FROM (VALUES
                            ('Overall'),
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
                    ) as td 
                        on 1=1 
                        { "where dd.delivery_district in ('Bangalore', 'Bengaluru Rural', 'Bengaluru Urban') " if city =='Bangalore' else (
                            "where dd.delivery_state='DELHI' " if city=='New Delhi' else ""
                        )}
                    group by 1,2
                    
                ) 
                    
                select 
                    B.state as state, B.time_of_day as time_of_day,
                    COALESCE(A.total_conversion_percentage, 0) AS total_conversion_percentage,
                    COALESCE(A.total_assigned_percentage, 0) AS total_assigned_percentage, 
                    COALESCE(A.confirmed_data, 0) AS confirmed_data,
                    COALESCE(A.assigned_data, 0) AS assigned_data,
                    COALESCE(A.searched_data, 0) AS searched_data
                from 
                    B left join A on B.state=A.state and B.time_of_day = A.time_of_day
                    order by 1,2;
                        
                """

        df = self.db_utility.execute_query(query)
        return df
    
    @log_function_call(ondcLogger)
    def fetch_logistic_searched_data_date_range(self):
        query = f"""
            select max(date), min(date)
            from {constant.LOGISTIC_SEARCH_PINCODE_TBL}
        """
        df = self.db_utility.execute_query(query)
        return df

    @log_function_call(ondcLogger)
    def fetch_overall_total_searches(self, start_date=None, end_date=None, state=None, day_type='All'):
        table_name = constant.LOGISTIC_SEARCH_PINCODE_TBL
        day_type_condition = " and extract(dow from date) in (6,0) " if day_type == 'Weekends' else (
            " and extract(dow from date) in (1,2,3,4,5)" if day_type == 'Week days' else ''
        )

        query = f"""
            with
                req_table as (
                    SELECT 
                        state,
                        district,
                        time_of_day,
                        CASE
                            WHEN SUM(searched) = 0 OR SUM(confirmed) = 0 THEN 0 
                            ELSE ROUND((SUM(confirmed) / SUM(searched)) * 100.0, 1) 
                        END AS total_conversion_percentage,
                        CASE
                            WHEN SUM(searched) = 0 OR SUM(assigned) = 0 THEN 0 
                            ELSE ROUND((SUM(assigned) / SUM(searched)) * 100.0, 1) 
                        END AS total_assigned_percentage,
                        SUM(confirmed) AS confirmed_data,
                        SUM(assigned) AS assigned_data,
                        SUM(searched) AS searched_data
                    from 
                        {table_name} ls
                    WHERE 
                        date BETWEEN '{start_date}' and '{end_date}'
                        {day_type_condition} { f" and upper(state)=upper('{state}') " if state else ''}
                    GROUP BY 1, 2, 3
                ),
                A as (
                    -- District-level data for all time_of_day
                    SELECT 
                        state,
                        district,
                        time_of_day,
                        total_conversion_percentage,
                        total_assigned_percentage,
                        confirmed_data,
                        assigned_data,
                        searched_data
                    FROM req_table

                    UNION ALL

                    -- District-level data for Overall time_of_day
                    SELECT 
                        state,
                        district,
                        'Overall' AS time_of_day,
                        CASE
                            WHEN SUM(searched_data) = 0 OR SUM(confirmed_data) = 0 THEN 0 
                            ELSE ROUND((SUM(confirmed_data) / SUM(searched_data)) * 100.0, 1) 
                        END AS total_conversion_percentage,
                        CASE
                            WHEN SUM(searched_data) = 0 OR SUM(assigned_data) = 0 THEN 0 
                            ELSE ROUND((SUM(assigned_data) / SUM(searched_data)) * 100.0, 1) 
                        END AS total_assigned_percentage,
                        SUM(confirmed_data) AS confirmed_data,
                        SUM(assigned_data) AS assigned_data,
                        SUM(searched_data) AS searched_data
                    FROM req_table
                    GROUP BY 1, 2

                    UNION ALL

                    -- State-level data (district = 'All') for each time_of_day
                    SELECT 
                        state,
                        'All' as district,
                        time_of_day,
                        CASE
                            WHEN SUM(searched_data) = 0 OR SUM(confirmed_data) = 0 THEN 0 
                            ELSE ROUND((SUM(confirmed_data) / SUM(searched_data)) * 100.0, 1) 
                        END AS total_conversion_percentage,
                        CASE
                            WHEN SUM(searched_data) = 0 OR SUM(assigned_data) = 0 THEN 0 
                            ELSE ROUND((SUM(assigned_data) / SUM(searched_data)) * 100.0, 1) 
                        END AS total_assigned_percentage,
                        SUM(confirmed_data) AS confirmed_data,
                        SUM(assigned_data) AS assigned_data,
                        SUM(searched_data) AS searched_data
                    FROM req_table
                    GROUP BY 1, 3

                    UNION ALL

                    -- State-level data (district = 'All') for Overall time_of_day
                    SELECT 
                        state,
                        'All' as district,
                        'Overall' AS time_of_day,
                        CASE
                            WHEN SUM(searched_data) = 0 OR SUM(confirmed_data) = 0 THEN 0 
                            ELSE ROUND((SUM(confirmed_data) / SUM(searched_data)) * 100.0, 1) 
                        END AS total_conversion_percentage,
                        CASE
                            WHEN SUM(searched_data) = 0 OR SUM(assigned_data) = 0 THEN 0 
                            ELSE ROUND((SUM(assigned_data) / SUM(searched_data)) * 100.0, 1) 
                        END AS total_assigned_percentage,
                        SUM(confirmed_data) AS confirmed_data,
                        SUM(assigned_data) AS assigned_data,
                        SUM(searched_data) AS searched_data
                    FROM req_table
                    GROUP BY 1
                ),
                B AS (
                    select 
                        dd.state as state,
                        dd.district as district,
                        td.time_of_day as time_of_day
                    from 
                    (
                        select 
                            delivery_state as state,
                            delivery_district as district
                        from {constant.DIM_DISTRICTS}
                            {f" where upper(delivery_state)=upper('{state}') " if state else ''}
                            group by 1,2
                        Union all 
                        select 
                            delivery_state as state,
                            'All' as district
                        from {constant.DIM_DISTRICTS}
                            {f" where upper(delivery_state)=upper('{state}') " if state else ''}
                            group by 1 
                    ) dd 
                    right join (
                        SELECT 
                            time_of_day
                        FROM (VALUES
                            ('Overall'),
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
                    ) td 
                    on 1=1 
                    group by 1,2,3
                )
                select 
                    B.state as state, B.district as district, B.time_of_day as time_of_day,
                    COALESCE(A.total_conversion_percentage, 0) AS total_conversion_percentage,
                    COALESCE(A.total_assigned_percentage, 0) AS total_assigned_percentage, 
                    COALESCE(A.confirmed_data, 0) AS confirmed_data,
                    COALESCE(A.assigned_data, 0) AS assigned_data,
                    COALESCE(A.searched_data, 0) AS total_searches
                from 
                    B 
                left join A 
                    on B.state=A.state 
                    and B.district=A.district 
                    and B.time_of_day = A.time_of_day 
                order by 1, 2, 3;
        """
        df= self.db_utility.execute_query(query)
        return df
    
    @log_function_call(ondcLogger)
    def fetch_pan_india_search_distribution(self, start_date, end_date, day_type):
        table_name = constant.LOGISTIC_SEARCH_PINCODE_TBL

        day_type_condition = " and extract(dow from date) in (6,0) " if day_type == 'Weekends' else (
            " and extract(dow from date) in (1,2,3,4,5)" if day_type == 'Week days' else ''
        )

        query = f"""
                with A as (
                    select date, 
                        time_of_day, 
                        sum(searched) as searched_count 
                    from {table_name} 
	                where date BETWEEN '{start_date}' and '{end_date}'
                    {day_type_condition} 
	                group by 1,2),
                B as (
                    SELECT 
	                    time_of_day
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
                select 
                    A.date, 
                    B.time_of_day, 
                    COALESCE(A.searched_count, 0) as searched_count 
                from 
                    A right join B on A.time_of_day = B.time_of_day
            """
        
        df= self.db_utility.execute_query(query)
        return df

    @log_function_call(ondcLogger)
    def fetch_top_states_search_distribution(self, start_date, end_date, day_type, state):
        table_name = constant.LOGISTIC_SEARCH_PINCODE_TBL

        day_type_condition = " and extract(dow from date) in (6,0) " if day_type == 'Weekends' else (
            " and extract(dow from date) in (1,2,3,4,5)" if day_type == 'Week days' else ''
        )
        query = f"""
            select 
                state, 
                time_of_day,
                date,
                sum(searched) as searched
            FROM {table_name}
            WHERE 
                date BETWEEN '{start_date}' AND '{end_date}' 
                {day_type_condition}
                {f" and upper(state)=upper('{state}') " if state else ''}
                AND state IS NOT NULL
                AND state <> ''
            group by 1,2,3
            UNION all
            select 
                state, 
                'Overall' as time_of_day,
                date,
                sum(searched) as searched
            FROM {table_name}
            WHERE
                date BETWEEN '{start_date}' AND '{end_date}' 
                {day_type_condition}
                {f" and upper(state)=upper('{state}') " if state else ''}
                AND state IS NOT NULL
                AND state <> ''
            group by 1,2,3
        """
        df= self.db_utility.execute_query(query)
        return df

    @log_function_call(ondcLogger)
    def fetch_top_districts_search_distribution(self, start_date, end_date, day_type, state):
        table_name = constant.LOGISTIC_SEARCH_PINCODE_TBL

        day_type_condition = " and extract(dow from date) in (6,0) " if day_type == 'Weekends' else (
            " and extract(dow from date) in (1,2,3,4,5)" if day_type == 'Week days' else ''
        )

        query = f"""
            select 
                district, 
                time_of_day,
                date,
                sum(searched) as searched
            FROM {table_name}
            WHERE 
                date BETWEEN '{start_date}' AND '{end_date}' 
                {day_type_condition}
                {f" and upper(state)=upper('{state}') " if state else ''}
                AND district IS NOT NULL
                AND district <> ''
            group by 1,2,3
            UNION all
            select 
                district, 
                'Overall' as time_of_day,
                date,
                sum(searched) as searched
            FROM {table_name}
            WHERE
                date BETWEEN '{start_date}' AND '{end_date}' 
                {day_type_condition}
                {f" and upper(state)=upper('{state}') " if state else ''}
                AND district IS NOT NULL
                AND district <> ''
            group by 1,2,3
        """
        
        df= self.db_utility.execute_query(query)
        return df


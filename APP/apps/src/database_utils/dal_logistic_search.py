

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
    def fetch_logistic_searched_data(self, city):
        where_condition = " district in ('Bangalore', 'Bengaluru Rural', 'Bengaluru Urban') " \
            if city == 'Bangalore' else "state = 'DELHI'"
        
        query = f"""
            
            (SELECT 
                    ls.time_of_day as time_of_day, 
                    ls.pick_up_pincode, 
                    case
                        when sum(ls.searched) = 0 or sum(ls.confirmed) = 0 then 0 
                        else round((sum(ls.confirmed)/sum(ls.searched))*100.0, 2) 
                    end as total_conversion_percentage,
                    
                    sum(ls.searched) as searched_data
                from {constant.LOGISTIC_SEARCH_PINCODE_TBL} ls
                    where {where_condition}
                group by ls.time_of_day, ls.pick_up_pincode )

                    Union
                (SELECT 
                    'Overall' as time_of_day,
                    ls.pick_up_pincode, 
                    case
                        when sum(ls.searched) = 0 or sum(ls.confirmed) = 0 then 0 
                        else round((sum(ls.confirmed)/sum(ls.searched))*100.0, 2) 
                    end as total_conversion_percentage,
                    
                    sum(ls.searched) as searched_data
                from {constant.LOGISTIC_SEARCH_PINCODE_TBL} ls
                    where {where_condition} group by ls.pick_up_pincode  )
                    order by pick_up_pincode, time_of_day"""
        df = self.db_utility.execute_query(query)
        return df
    
    @log_function_call(ondcLogger)
    def fetch_logistic_searched_top_card_data(self, city):
        where_condition = " district in ('Bangalore', 'Bengaluru Rural', 'Bengaluru Urban') " \
            if city == 'Bangalore' else " state = 'DELHI' "
        
        query = f"""
            (SELECT 
                ls.time_of_day as time_of_day,
                case
                    when sum(ls.searched) = 0 or sum(ls.confirmed) = 0 then 0 
                    else round((sum(ls.confirmed)/sum(ls.searched))*100.0, 2) 
                end as total_conversion_percentage,
                case
                    when sum(ls.searched) = 0 or sum(ls.assigned) = 0 then 0 
                    else round((sum(ls.assigned)/sum(ls.searched))*100.0, 2) 
                end as total_assigned_percentage,
                sum(ls.searched) as searched_data
            from {constant.LOGISTIC_SEARCH_PINCODE_TBL} ls
                where {where_condition}
            group by ls.time_of_day )

                Union
            (SELECT 
                'Overall' as time_of_day,
                case
                    when sum(ls.searched) = 0 or sum(ls.confirmed) = 0 then 0 
                    else round((sum(ls.confirmed)/sum(ls.searched))*100.0, 2) 
                end as total_conversion_percentage,
                case
                    when sum(ls.searched) = 0 or sum(ls.assigned) = 0 then 0 
                    else round((sum(ls.assigned)/sum(ls.searched))*100.0, 2) 
                end as total_assigned_percentage,
                sum(ls.searched) as searched_data
            from {constant.LOGISTIC_SEARCH_PINCODE_TBL} ls
                where {where_condition} )
                order by time_of_day
            
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
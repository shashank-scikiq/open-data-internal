from apps.src.database_utils.database_utility import DatabaseUtility
from apps.utils import constant
from apps.src.database_utils.generic_queries import max_date_retail_overall, fetch_district_list_query 

class RetailDataAccessLayer(DatabaseUtility):
    def fetch_district_level_order_summary(self, *args, **kwargs):
        table_name = constant.MONTHLY_DISTRICT_TABLE

        params = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))

        query = f"""
            select 
                delivery_state_code,
                delivery_state,
                delivery_district,
                SUM(total_orders_delivered) AS total_orders_in_district,
                sum(total_items) AS total_ordered_items_in_district
            from 
                {table_name}
            where domain = 'Retail'
                    and ((order_year*100) + order_month) between 
                        {((params['start_year']) * 100) + params['start_month']} and
                        {((params['end_year']) * 100) + params['end_month']}
             group by 1,2,3 """
        df = self.execute_query(query)
        return df
    
    def fetch_district_level_order_summary_with_seller_state_info(self, *args, **kwargs):
        table_name = constant.MONTHLY_DISTRICT_TABLE

        params = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))

        query = f"""
            select 
                delivery_state_code,
                delivery_state,
                delivery_district,
                seller_state_code,
                seller_state,
                seller_district,
                SUM(total_orders_delivered) AS total_orders_in_district,
                sum(total_items) AS total_ordered_items_in_district
            from 
                {table_name}
            where domain = 'Retail'
                    and ((order_year*100) + order_month) between 
                        {((params['start_year']) * 100) + params['start_month']} and
                        {((params['end_year']) * 100) + params['end_month']}
             group by 1,2,3,4,5,6 """

        df = self.execute_query(query)
        return df

    def fetch_state_level_sellers(self, *args, **kwargs):
        aggregate_value = "'AGG'"
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)

        table_name = constant.ACTIVE_TOTAL_SELLER_TBL
        
        params = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))

        query = f"""
            SELECT
                seller_state_code,
                seller_state,
                max(total_sellers) as total_sellers
            FROM
                {table_name}
            WHERE
                ((year_value*100) + month_value) = (({params['end_year']} * 100) + {params['end_month']})
                and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregate_value})
                and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregate_value})
                and upper(seller_state) <> {aggregate_value}
                and seller_district = {aggregate_value}
                and seller_state <> {aggregate_value}
            group by 1,2
            """
        df = self.execute_query(query)
        return df

    def fetch_district_level_sellers(self, *args, **kwargs):
        aggregate_value = "'AGG'"
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)

        table_name = constant.ACTIVE_TOTAL_SELLER_TBL
        
        params = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))

        query = f"""
            SELECT
                seller_state_code,
                seller_state,
                seller_district,
                max(total_sellers) as total_sellers
            FROM
                {table_name}
            WHERE
                ((year_value*100) + month_value) = (({params['end_year']} * 100) + {params['end_month']})
                and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregate_value})
                and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregate_value})
                and seller_state <> {aggregate_value}
            group by 1,2,3
            """
        df = self.execute_query(query)
        return df
    
    def fetch_interdistrict_going_orders(self, *args, **kwargs):
        district_name = kwargs.get('district', None)

        table_name = constant.MONTHLY_DISTRICT_TABLE
        
        params = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))

        query = f"""
            select 
                seller_district,
                delivery_district,
                SUM(total_orders_delivered) AS order_demand
            from 
                {table_name}
            where 
                ((order_year*100)+order_month) between 
                {((params['start_year']) * 100) + params['start_month']} and
                {((params['end_year']) * 100) + params['end_month']}
                and upper(seller_district)=upper('{district_name}')
                and not upper(delivery_district) in ('', 'AGG', 'MISSING')
         group by 1,2 order by 3 desc"""

        df = self.execute_query(query)
        return df
    
    def fetch_interdistrict_coming_orders(self, *args, **kwargs):
        district_name = kwargs.get('district', None)

        table_name = constant.MONTHLY_DISTRICT_TABLE
        
        params = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))

        query = f"""
            select 
                seller_district,
                delivery_district,
                SUM(total_orders_delivered) AS order_demand
            from 
                {table_name}
            where 
                ((order_year*100)+order_month) between 
                {((params['start_year']) * 100) + params['start_month']} and
                {((params['end_year']) * 100) + params['end_month']}
                and upper(delivery_district)=upper('{district_name}')
                and not upper(seller_district) in ('', 'AGG', 'MISSING')
             group by 1,2 order by 3 desc"""

        df = self.execute_query(query)
        return df

    def fetch_interstate_going_orders(self, *args, **kwargs):
        state = kwargs.get('state', None)

        table_name = constant.MONTHLY_DISTRICT_TABLE
        
        params = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))

        query = f"""
            select 
                seller_state,
                delivery_state,
                SUM(total_orders_delivered) AS order_demand
            from 
                {table_name}
            where 
                ((order_year*100)+order_month) between 
                {((params['start_year']) * 100) + params['start_month']} and
                {((params['end_year']) * 100) + params['end_month']}
                and upper(seller_state)=upper('{state}')
                and not upper(delivery_state) in ('', 'AGG', 'MISSING')
            group by 1,2 order by 3 desc"""
        
        df = self.execute_query(query)
        return df

    def fetch_interstate_coming_orders(self, *args, **kwargs):
        state = kwargs.get('state', None)

        table_name = constant.MONTHLY_DISTRICT_TABLE
        
        params = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))

        query = f"""
            select 
                seller_state,
                delivery_state,
                SUM(total_orders_delivered) AS order_demand
            from 
                {table_name}
            where 
                ((order_year*100)+order_month) between 
                {((params['start_year']) * 100) + params['start_month']} and
                {((params['end_year']) * 100) + params['end_month']}
                and upper(delivery_state)=upper('{state}')
                and not upper(seller_state) in ('', 'AGG', 'MISSING')
         group by 1,2 order by 3 desc"""

        df = self.execute_query(query)
        return df
    
    def fetch_month_wise_orders_at_district_level(self, *args, **kwargs):
        state = kwargs.get('state', None)

        table_name = constant.MONTHLY_DISTRICT_TABLE
        

        parameters = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))

        query = f"""
            SELECT 
                order_month,
                order_year,
                delivery_state,
                delivery_district,
                SUM(total_orders_delivered) AS total_orders_delivered
            from 
                {table_name}
            where
                ((order_year*100) + order_month) between 
                    (({parameters['start_year']} * 100) + {parameters['start_month']}) 
                    and 
                    (({parameters['end_year']} * 100) + {parameters['end_month']})
                and domain = 'Retail'
                {f"and upper(delivery_state) = upper('{state}')" if state else ''}
            group by 1,2,3,4
        """
        df = self.execute_query(query)
        return df
    
    def fetch_month_wise_orders_at_state_level(self, *args, **kwargs):
        state = kwargs.get('state', None)

        table_name = constant.MONTHLY_DISTRICT_TABLE
        

        parameters = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))

        query = f"""
            SELECT 
                order_month,
                order_year,
                delivery_state,
                SUM(total_orders_delivered) AS total_orders_delivered
            from 
                {table_name}
            where
                ((order_year*100) + order_month) between 
                    (({parameters['start_year']} * 100) + {parameters['start_month']}) 
                    and 
                    (({parameters['end_year']} * 100) + {parameters['end_month']})
                and domain = 'Retail'
                {f"and upper(delivery_state) = upper('{state}')" if state else ''}
            group by 1,2,3
        """
        df = self.execute_query(query)
        return df
    
    def fetch_month_wise_orders_at_global_level(self, *args, **kwargs):
        state = kwargs.get('state', None)

        table_name = constant.MONTHLY_DISTRICT_TABLE

        parameters = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))

        query = f"""
            SELECT 
                order_month,
                order_year,
                SUM(total_orders_delivered) AS total_orders_delivered
            from 
                {table_name}
            where
                ((order_year*100) + order_month) between 
                    (({parameters['start_year']} * 100) + {parameters['start_month']}) 
                    and 
                    (({parameters['end_year']} * 100) + {parameters['end_month']})
                and domain = 'Retail'
                {f"and upper(delivery_state) = upper('{state}')" if state else ''}
            group by 1,2
        """
        df = self.execute_query(query)
        return df
    
    def fetch_month_wise_sellers_at_district_level(self, *args, **kwargs):
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)
        seller_type = kwargs.get('seller_type', 'Total')
        state = kwargs.get('state', None)
        aggregated_value = "'AGG'"
        params = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))
        
        table_name = constant.ACTIVE_TOTAL_SELLER_TBL

        query = f"""
            SELECT 
                month_value as order_month,
                year_value as order_year,
                seller_state as state,
                seller_district as district,
                max(total_sellers) as sellers_count
            FROM 
                {table_name}
            WHERE
                ((year_value*100) + month_value) between
                    (({params['start_year']} * 100) + {params['start_month']})
                    and
                    (({params['end_year']} * 100) + {params['end_month']})
                and seller_district <> {aggregated_value}
                and upper(seller_state) {f" = upper('{state}'" if state else f" <> upper({aggregated_value}"})
                and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregated_value})
                and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregated_value})
            group by 1, 2,3,4
        """
        df = self.execute_query(query)
        return df
    
    def fetch_month_wise_sellers_at_state_level(self, *args, **kwargs):
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)
        seller_type = kwargs.get('seller_type', 'Total')
        state = kwargs.get('state', None)
        aggregated_value = "'AGG'"
        params = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))
        
        table_name = constant.ACTIVE_TOTAL_SELLER_TBL

        query = f"""
            SELECT 
                month_value as order_month,
                year_value as order_year,
                seller_state as state,
                max(total_sellers) as sellers_count
            FROM 
                {table_name}
            WHERE
                ((year_value*100) + month_value) between
                    (({params['start_year']} * 100) + {params['start_month']})
                    and
                    (({params['end_year']} * 100) + {params['end_month']})
                and seller_district = {aggregated_value}
                and upper(seller_state) {f" = upper('{state}'" if state else f" <> upper({aggregated_value}"})
                and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregated_value})
                and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregated_value})
            group by 1, 2,3
        """
        df = self.execute_query(query)
        return df
    
    def fetch_month_wise_sellers_at_global_level(self, *args, **kwargs):
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)
        seller_type = kwargs.get('seller_type', 'Total')
        aggregated_value = "'AGG'"
        params = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))
        
        table_name = constant.ACTIVE_TOTAL_SELLER_TBL

        query = f"""
            SELECT 
                month_value as order_month,
                year_value as order_year,
                max(total_sellers) as total_orders_delivered
            FROM 
                {table_name}
            WHERE
                ((year_value*100) + month_value) between
                    (({params['start_year']} * 100) + {params['start_month']})
                    and
                    (({params['end_year']} * 100) + {params['end_month']})
                and seller_district = {aggregated_value}
                and  upper(seller_state) = {aggregated_value}
                and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregated_value})
                and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregated_value})
            group by 1, 2
            order by 1,2
        """
        df = self.execute_query(query)
        return df

    def fetch_month_wise_hyperlocal_orders_at_district_level(self, *args, **kwargs):
        state = kwargs.get('state', None)
        table_name = constant.MONTHLY_DISTRICT_TABLE
        
        parameters = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))

        query = f"""
            SELECT 
                order_month,
                order_year,
                delivery_state,
                delivery_district,
                SUM(total_orders_delivered) AS total_orders_delivered,
                SUM(intradistrict_orders) AS intradistrict_orders
            from 
                {table_name}
            where
                ((order_year*100) + order_month) between 
                    (({parameters['start_year']} * 100) + {parameters['start_month']}) 
                    and 
                    (({parameters['end_year']} * 100) + {parameters['end_month']})
                and domain = 'Retail'
                {f"and upper(delivery_state) = upper('{state}')" if state else ''}
            group by 1,2,3,4
        """

        df = self.execute_query(query)
        return df
    
    def fetch_month_wise_hyperlocal_orders_at_state_level(self, *args, **kwargs):
        state = kwargs.get('state', None)

        table_name = constant.MONTHLY_DISTRICT_TABLE

        parameters = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))

        query = f"""
            SELECT 
                order_month,
                order_year,
                delivery_state,
                SUM(total_orders_delivered) AS total_orders_delivered,
                SUM(intrastate_orders) AS intrastate_orders_total
            from 
                {table_name}
            where
                ((order_year*100) + order_month) between 
                    (({parameters['start_year']} * 100) + {parameters['start_month']}) 
                    and 
                    (({parameters['end_year']} * 100) + {parameters['end_month']})
                and domain = 'Retail'
                {f"and upper(delivery_state) = upper('{state}')" if state else ''}
            group by 1,2,3
        """
        df = self.execute_query(query)
        return df
    
    def fetch_date_range(self):
        df = self.execute_query(max_date_retail_overall)
        return df
    
    def fetch_state_district_list(self):
        df = self.execute_query(fetch_district_list_query)
        return df

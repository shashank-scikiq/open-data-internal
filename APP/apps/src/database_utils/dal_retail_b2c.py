from apps.src.database_utils.database_utility import DatabaseUtility
from apps.utils import constant

class B2CDataAccessLayer(DatabaseUtility):
    def fetch_district_level_order_summary(self, *args, **kwargs):
        aggregate_value = "'AGG'"
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)

        table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE \
            if category or sub_category else constant.MONTHLY_DISTRICT_TABLE

        
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
            where sub_domain = 'B2C'
                    and ((order_year*100) + order_month) between 
                        {((params['start_year']) * 100) + params['start_month']} and
                        {((params['end_year']) * 100) + params['end_month']}
            """
        
        if category or sub_category:
            query += f"""
                and delivery_state <> 'AGG'
                and delivery_district <> 'AGG'
                and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregate_value})
                and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregate_value})
            """
        
        query += " group by 1,2,3 "
        df = self.execute_query(query)
        return df
    
    def fetch_district_level_order_summary_with_seller_state_info(self, *args, **kwargs):
        aggregate_value = "'AGG'"
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)

        table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE \
            if category or sub_category else constant.MONTHLY_DISTRICT_TABLE

        
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
            where sub_domain = 'B2C'
                    and ((order_year*100) + order_month) between 
                        {((params['start_year']) * 100) + params['start_month']} and
                        {((params['end_year']) * 100) + params['end_month']}
            """
        
        if category or sub_category:
            query += f"""
                and delivery_state <> 'AGG'
                and delivery_district <> 'AGG'
                and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregate_value})
                and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregate_value})
            """
        
        query += " group by 1,2,3,4,5,6 "

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
                max(active_sellers) as active_sellers,
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
                max(active_sellers) as active_sellers,
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
        aggregate_value = "'AGG'"
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)
        district_name = kwargs.get('district', None)

        table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE \
            if category or sub_category else constant.MONTHLY_DISTRICT_TABLE
        
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
            """
        
        if category or sub_category:
            query += f"""
                and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregate_value})
                and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregate_value})
            """
        
        query += " group by 1,2 order by 3 desc"

        df = self.execute_query(query)
        return df
    
    def fetch_interdistrict_coming_orders(self, *args, **kwargs):
        aggregate_value = "'AGG'"
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)
        district_name = kwargs.get('district', None)

        table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE \
            if category or sub_category else constant.MONTHLY_DISTRICT_TABLE
        
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
            """
        
        if category or sub_category:
            query += f"""
                and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregate_value})
                and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregate_value})
            """
        
        query += " group by 1,2 order by 3 desc"

        df = self.execute_query(query)
        return df

    def fetch_interstate_going_orders(self, *args, **kwargs):
        aggregate_value = "'AGG'"
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)
        state = kwargs.get('state', None)

        table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE \
            if category or sub_category else constant.MONTHLY_DISTRICT_TABLE
        
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
            """
        
        if category or sub_category:
            query += f"""
                and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregate_value})
                and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregate_value})
            """
        
        query += " group by 1,2 order by 3 desc"
        df = self.execute_query(query)
        return df

    def fetch_interstate_coming_orders(self, *args, **kwargs):
        aggregate_value = "'AGG'"
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)
        state = kwargs.get('state', None)

        table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE \
            if category or sub_category else constant.MONTHLY_DISTRICT_TABLE
        
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
            """
        
        if category or sub_category:
            query += f"""
                and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregate_value})
                and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregate_value})
            """
        
        query += " group by 1,2 order by 3 desc"

        df = self.execute_query(query)
        return df

    def fetch_categories(self, *args, **kwargs):
        query = f'''
                select 
                    category  as category,
                    sub_category 
                from {constant.DIM_CATEGORIES}
                group by 1,2
        '''
        df = self.execute_query(query)
        return df
    
    def fetch_month_wise_orders_at_district_level(self, *args, **kwargs):
        aggregate_value = "'AGG'"
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)
        state = kwargs.get('state', None)

        table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE \
            if category or sub_category else constant.MONTHLY_DISTRICT_TABLE
        

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
                and sub_domain = 'B2C'
        """

        if category or sub_category:
            query += f"""
                and upper(delivery_state) {f" = upper('{state}'" if state else f" <> upper({aggregate_value}"})
                and delivery_district <> {aggregate_value}
                and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregate_value})
                and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregate_value})            
            """
        else:
            query += f"""
                {f"and upper(delivery_state) = upper('{state}')" if state else ''}
            """
        
        query += """
            group by 1,2,3,4
        """
        df = self.execute_query(query)
        return df
    
    def fetch_month_wise_orders_at_state_level(self, *args, **kwargs):
        aggregate_value = "'AGG'"
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)
        state = kwargs.get('state', None)

        table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE \
            if category or sub_category else constant.MONTHLY_DISTRICT_TABLE
        

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
                and sub_domain = 'B2C'
        """

        if category or sub_category:
            query += f"""
                and upper(delivery_state) {f" = upper('{state}'" if state else f" <> upper({aggregate_value}"})
                and delivery_district = {aggregate_value}
                and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregate_value})
                and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregate_value})
            """
        else:
            query += f"""
                {f"and upper(delivery_state) = upper('{state}')" if state else ''}
            """
        
        query += """
            group by 1,2,3
        """
        df = self.execute_query(query)
        return df
    
    def fetch_month_wise_orders_at_global_level(self, *args, **kwargs):
        aggregate_value = "'AGG'"
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)
        state = kwargs.get('state', None)

        table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE \
            if category or sub_category else constant.MONTHLY_DISTRICT_TABLE
        

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
                and sub_domain = 'B2C'
        """

        if category or sub_category:
            query += f"""
                and upper(delivery_state) = {aggregate_value}
                and delivery_district = {aggregate_value}
                and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregate_value})
                and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregate_value})
            """
        else:
            query += f"""
                {f"and upper(delivery_state) = upper('{state}')" if state else ''}
            """
        
        query += """
            group by 1,2
        """
        df = self.execute_query(query)
        return df
    
    def fetch_category_penetration_orders(self, *args, **kwargs):
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)
        aggregated_value = "'AGG'"
        params = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))
        
        table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE
        
        query = f'''
                select 
                    category, 
                    case 
                        when sub_category = {aggregated_value} then 'ALL' 
                        else sub_category 
                    end as sub_category, 
                    max(total_orders_delivered) as order_demand
                from 
                    {table_name}
                where ((order_year*100)+order_month) =  (({params['end_year']}*100)+{params['end_month']})
                    and upper(category) { " = upper('"+ category +"') " if category else ' <> ' + aggregated_value}
                    { (" and upper(sub_category) = upper('" + sub_category + "') ") if sub_category else ' '}
                    and upper(seller_state) = {aggregated_value} 
                    and not category in ('Undefined', '')  
                    and seller_state <> ''
                group by 1,2
                order by category
                '''
        df = self.execute_query(query)
        return df
    
    def fetch_month_wise_sellers_at_district_level(self, *args, **kwargs):
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)
        seller_type = kwargs.get('seller_type', 'Total')
        state = kwargs.get('state', None)
        seller_column = 'total_sellers' if seller_type == 'Total' else 'active_sellers'
        aggregated_value = "'AGG'"
        params = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))
        
        table_name = constant.ACTIVE_TOTAL_SELLER_TBL

        query = f"""
            SELECT 
                month_value as order_month,
                year_value as order_year,
                seller_state as state,
                seller_district as district,
                max({seller_column}) as sellers_count
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
        seller_column = 'total_sellers' if seller_type == 'Total' else 'active_sellers'
        aggregated_value = "'AGG'"
        params = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))
        
        table_name = constant.ACTIVE_TOTAL_SELLER_TBL

        query = f"""
            SELECT 
                month_value as order_month,
                year_value as order_year,
                seller_state as state,
                max({seller_column}) as sellers_count
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
        seller_column = 'total_sellers' if seller_type == 'Total' else 'active_sellers'
        aggregated_value = "'AGG'"
        params = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))
        
        table_name = constant.ACTIVE_TOTAL_SELLER_TBL

        query = f"""
            SELECT 
                month_value as order_month,
                year_value as order_year,
                max({seller_column}) as total_orders_delivered
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

    def fetch_category_penetration_sellers(self, *args, **kwargs):
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)
        seller_type = kwargs.get('seller_type', 'Total')
        seller_column = 'total_sellers' if seller_type == 'Total' else 'active_sellers'
        aggregated_value = "'AGG'"
        params = self.get_query_month_parameters(kwargs.get('start_date'), kwargs.get('end_date'))
        
        table_name = constant.ACTIVE_TOTAL_SELLER_TBL
        
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
            where ((year_value*100)+month_value) =  (({params['end_year']}*100)+{params['end_month']})
                and upper(category) { " = upper('"+ category +"') " if category else ' <> ' + aggregated_value}
                { (" and upper(sub_category) = upper('" + sub_category + "') ") if sub_category else ' '}
                and upper(seller_state) = {aggregated_value} 
                and category <>'Undefined' 
                and seller_state <> ''
            group by 1,2
            order by category
        '''

        df = self.execute_query(query)
        return df

    def fetch_month_wise_hyperlocal_orders_at_district_level(self, *args, **kwargs):
        aggregate_value = "'AGG'"
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)
        state = kwargs.get('state', None)

        table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE \
            if category or sub_category else constant.MONTHLY_DISTRICT_TABLE
        

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
                and sub_domain = 'B2C'
        """

        if category or sub_category:
            query += f"""
                and upper(delivery_state) {f" = upper('{state}'" if state else f" <> upper({aggregate_value}"})
                and delivery_district <> {aggregate_value}
                and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregate_value})
                and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregate_value})            
            """
        else:
            query += f"""
                {f"and upper(delivery_state) = upper('{state}')" if state else ''}
            """
        
        query += """
            group by 1,2,3,4
        """

        df = self.execute_query(query)
        return df
    
    def fetch_month_wise_hyperlocal_orders_at_state_level(self, *args, **kwargs):
        aggregate_value = "'AGG'"
        category = kwargs.get('category', None)
        sub_category = kwargs.get('sub_category', None)
        state = kwargs.get('state', None)

        table_name = constant.SUB_CAT_MONTHLY_DISTRICT_TABLE \
            if category or sub_category else constant.MONTHLY_DISTRICT_TABLE
        

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
                and sub_domain = 'B2C'
        """

        if category or sub_category:
            query += f"""
                and upper(delivery_state) {f" = upper('{state}'" if state else f" <> upper({aggregate_value}"})
                and delivery_district = {aggregate_value}
                and upper(category) = upper({f"'{category}'" if bool(category) and (category != 'None') else aggregate_value})
                and upper(sub_category) = upper({f"'{sub_category}'" if bool(sub_category) and (sub_category != 'None') else aggregate_value})
            """
        else:
            query += f"""
                {f"and upper(delivery_state) = upper('{state}')" if state else ''}
            """
        
        query += """
            group by 1,2,3
        """
        df = self.execute_query(query)
        return df

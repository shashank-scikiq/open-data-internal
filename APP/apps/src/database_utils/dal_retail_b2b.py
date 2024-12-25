from apps.src.database_utils.database_utility import DatabaseUtility
from apps.utils import constant


class B2BDataAccessLayer(DatabaseUtility):
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
            where sub_domain = 'B2B'
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
            where sub_domain = 'B2C'
                    and ((order_year*100) + order_month) between 
                        {((params['start_year']) * 100) + params['start_month']} and
                        {((params['end_year']) * 100) + params['end_month']}
             group by 1,2,3,4,5,6
            """

        df = self.execute_query(query)
        return df

    
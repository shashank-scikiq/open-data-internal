from decimal import getcontext

from apps.logging_conf import log_function_call, ondcLogger

from apps.utils import constant

getcontext().prec = 4

class DataAccessLayer:
    def __init__(self, db_utility):
        self.db_utility = db_utility
        self.comprehensive_data_df = None
        self.preload_penetration_data = None
        self.numeric_columns = ['total_orders_delivered', 'total_items', 'intradistrict_orders', 'intrastate_orders']
        self.sunburst_numeric_col = 'total_orders_delivered'

    def get_table_name(self, category, sub_category, domain=None):

        try:
            selected_view = constant.DISTRICT_TABLE

            if sub_category and sub_category != 'None':
                selected_view = constant.SUB_CATEGORY_TABLE
            elif category and category != 'None':
                selected_view = constant.CATEGORY_TABLE

            return selected_view

        except Exception as e:
            print(f"Error: {e}")
            if domain:
                return constant.DISTRICT_TABLE

            return constant.DISTRICT_TABLE

    @log_function_call(ondcLogger)
    def fetch_top_states_orders(self, start_date, end_date, category=None,
                                sub_category=None, domain_name=None, state=None):
        try:
            selected_view = self.get_table_name(category, sub_category)

            parameters = [start_date, end_date]

            query = f'''
                WITH TopStates AS (
                    SELECT 
                        COALESCE(delivery_state, 'MISSING') as delivery_state,
                        sum(total_orders_delivered) AS total_orders_delivered
                    FROM 
                        {selected_view}
                    WHERE 
                        order_date BETWEEN %s AND %s
                        and delivery_state != 'MISSING'
            '''

            if category and category != 'None':
                query += constant.category_sub_query
                parameters.append(category)

            if sub_category and sub_category != 'None':
                query += constant.sub_category_sub_query
                parameters.append(sub_category)

            if state and state != 'None':
                query += constant.delivery_state_sub_query
                parameters.append(state)

            query += '''
                    GROUP BY 
                        delivery_state
                    ORDER BY 
                        total_orders_delivered DESC
                    LIMIT 3
                ),
                FinalResult AS (
                    SELECT 
                        om.order_date as order_date,
                        COALESCE(om.delivery_state, 'MISSING') as delivery_state,
                        SUM(om.total_orders_delivered) AS total_orders_delivered
                    FROM 
                        {0} om
                    INNER JOIN 
                        TopStates ts ON COALESCE(om.delivery_state, 'MISSING') = upper(ts.delivery_state)
                    WHERE 
                        om.order_date BETWEEN %s AND %s
            '''.format(selected_view)

            parameters.extend([start_date, end_date])

            if category and category != 'None':
                query += " AND om.category = %s"
                parameters.append(category)

            if sub_category and sub_category != 'None':
                query += constant.tdr_sub_category_sub_query
                parameters.append(sub_category)

            if state and state != 'None':
                query += constant.tdr_delivery_state_sub_query
                parameters.append(state)

            query += '''
                    GROUP BY 
                        om.order_date, om.delivery_state
                    ORDER BY 
                        om.order_date, total_orders_delivered desc
                )
                SELECT * FROM FinalResult 
            '''
            df = self.db_utility.execute_query(query, parameters)

            return df
        except Exception as e:
            ondcLogger.error(str(e))
            raise



    @log_function_call(ondcLogger)
    def fetch_states_orders(self, start_date, end_date, category=None,
                            sub_category=None, domain_name=None, state=None):

        selected_view = self.get_table_name(category, sub_category)

        parameters = [start_date, end_date]

        query = f"""
            SELECT 
                delivery_state,
                sum(total_orders_delivered) AS total_orders_delivered
            FROM 
                {selected_view}
            WHERE 
                order_date BETWEEN %s AND %s
                and delivery_state is not null
                and delivery_state <> ''
        """

        if category and category != 'None':
            query += constant.category_sub_query
            parameters.append(category)
        if sub_category and sub_category != 'None':
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
    def fetch_cumulative_orders(self, start_date, end_date, category=None,
                                sub_category=None, domain_name=None, state=None):

        selected_view = self.get_table_name(category, sub_category)

        parameters = [start_date, end_date]

        query = f"""
            SELECT order_date as order_date,
                sum(total_orders_delivered) AS total_orders_delivered
            FROM 
                {selected_view}
            WHERE 
                order_date BETWEEN %s AND %s
        """

        if category and category != 'None':
            query += constant.category_sub_query
            parameters.append(category)
        if sub_category and sub_category != 'None':
            query += constant.sub_category_sub_query
            parameters.append(sub_category)
        if domain_name:
            query += constant.domain_sub_query
            parameters.append(domain_name)
        if state:
            query += constant.delivery_state_sub_query
            parameters.append(state)

        query += """
                GROUP BY order_date 
                ORDER BY 
                    order_date
        """

        df = self.db_utility.execute_query(query, parameters)

        return df

    @log_function_call(ondcLogger)
    def fetch_cumulative_orders_rv(self, start_date, end_date, category=None,
                                   sub_category=None, domain_name=None, state=None):

        selected_view = constant.RV_DISTRICT_TABLE

        parameters = [start_date, end_date]

        query = f"""
            SELECT order_date as order_date,
                sum(total_orders_delivered) AS total_orders_delivered
            FROM 
                {selected_view}
            WHERE 
                order_date BETWEEN %s AND %s
        """

        query += """
                GROUP BY order_date 
                ORDER BY 
                    order_date
        """

        df = self.db_utility.execute_query(query, parameters)

        return df

    @log_function_call(ondcLogger)
    def fetch_cummulative_sellers(self, start_date, end_date, category=None,
                                  sub_category=None, domain_name=None, state=None):

        table_name = constant.SELLER_TABLE

        query = f"""
                    SELECT 
                        order_date,
                        COUNT(DISTINCT trim(lower(provider_key))) AS total_orders_delivered
                    FROM 
                        {table_name}
                    WHERE
                        order_date BETWEEN %s AND %s
                """

        parameters = [start_date, end_date]

        if category and category != 'None':
            query += constant.category_sub_query
            parameters.append(category)

        if sub_category:
            query += constant.sub_category_sub_query
            parameters.append(sub_category)

        if domain_name:
            query += constant.domain_sub_query
            parameters.append(domain_name)

        if state:
            query += constant.delivery_state_sub_query
            parameters.append(state)

        query += " GROUP BY 1"

        df = self.db_utility.execute_query(query, parameters)

        return df

    @log_function_call(ondcLogger)
    def fetch_top_states_hyperlocal_orders(self, start_date, end_date, category=None, sub_category=None,
                                           domain_name=None, state=None):

        selected_view = self.get_table_name(category, sub_category)

        parameters = [start_date, end_date]

        base_query = f'''
                    WITH TopStates AS (
                        SELECT 
                            COALESCE(delivery_state, 'MISSING') as delivery_state,
                            sum(total_orders_delivered) AS total_orders_delivered,
                            SUM(intrastate_orders) AS intrastate_orders_total,
                            ROUND(SUM(intrastate_orders::numeric) / 
                            NULLIF(SUM(total_orders_delivered::numeric), 0) * 100, 2) AS intrastate_orders_percentage
                        FROM {selected_view}
                        WHERE 
                            order_date BETWEEN %s and %s
                            and delivery_state != 'MISSING'
                    '''

        if domain_name:
            base_query += constant.domain_sub_query
            parameters.append(domain_name)

        if category and category != 'None':
            base_query += constant.category_sub_query
            parameters.append(category)
            if sub_category:
                base_query += constant.sub_category_sub_query
                parameters.append(sub_category)

        if state:
            base_query += constant.delivery_state_sub_query
            parameters.append(state)

        base_query += f'''
                    GROUP BY 
                        delivery_state
                    ORDER BY 
                        intrastate_orders_percentage DESC
                        LIMIT 3
                )
                SELECT 
                    om.order_date as order_date,
                    COALESCE(om.delivery_state, 'MISSING')  as delivery_state,
                    SUM(om.total_orders_delivered) AS total_orders_delivered,
                    ROUND(SUM(om.intrastate_orders::numeric) / 
                    NULLIF(SUM(om.total_orders_delivered::numeric), 0) * 100, 2) AS intrastate_orders_percentage
                FROM {selected_view} om
                INNER JOIN 
                    TopStates ts ON COALESCE(om.delivery_state, 'MISSING')  = ts.delivery_state
                WHERE 
                    om.order_date BETWEEN %s and %s
        '''

        parameters.append(start_date)
        parameters.append(end_date)

        if domain_name:
            base_query += constant.tdr_domain_sub_query
            parameters.append(domain_name)

        if category and category != 'None':
            base_query += constant.tdr_category_sub_query
            parameters.append(category)
            if sub_category:
                base_query += constant.tdr_sub_category_sub_query
                parameters.append(sub_category)

        if state:
            base_query += constant.tdr_delivery_state_sub_query
            parameters.append(state)

        base_query += ('\nGROUP BY om.order_date, om.delivery_state '
                       'ORDER BY om.order_date, intrastate_orders_percentage DESC')

        df = self.db_utility.execute_query(base_query, parameters)

        return df

    def fetch_top_district_hyperlocal_orders(self, start_date, end_date, category=None, sub_category=None,
                                             domain_name=None, state=None):

        selected_view = self.get_table_name(category, sub_category)

        query = f"""
            WITH TopDistricts AS (
                SELECT 
                    delivery_district,
                    sum(total_orders_delivered) AS total_order_demand,
                    SUM(intradistrict_orders) AS intradistrict_orders,
                    ROUND((SUM(intradistrict_orders::numeric) / 
                    NULLIF(SUM(total_orders_delivered::numeric), 0)) * 100, 2) AS intradistrict_percentage
                FROM 
                    {selected_view}
                WHERE 
                    order_date BETWEEN %s AND %s
                    AND delivery_district <> '' and upper(delivery_district) <> 'UNDEFINED'
                    and delivery_district is not null

        """

        parameters = [start_date, end_date]

        if category and category != 'None':
            query += constant.category_sub_query
            parameters.append(category)
        if sub_category and sub_category != 'None':
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
                    delivery_district
                ORDER BY 
                    intradistrict_percentage DESC
                LIMIT 3
            ),
            FinalResult AS (
                SELECT 
                    om.order_date as order_date,
                    om.delivery_district as delivery_district,
                    SUM(om.total_orders_delivered) AS total_orders_delivered,
                    SUM(om.intradistrict_orders) AS intradistrict_orders,
                    ROUND((SUM(om.intradistrict_orders::numeric) / 
                    NULLIF(SUM(om.total_orders_delivered::numeric), 0)) * 100, 2) AS intrastate_orders_percentage
                FROM 
        """

        query += f"{selected_view} om"

        query += """
                INNER JOIN 
                    TopDistricts td ON om.delivery_district = td.delivery_district
                WHERE 
                    om.order_date BETWEEN %s AND %s
        """

        parameters.extend([start_date, end_date])

        if category and category != 'None':
            query += constant.tdr_category_sub_query
            parameters.append(category)
        if sub_category and sub_category != 'None':
            query += constant.tdr_sub_category_sub_query
            parameters.append(sub_category)
        if domain_name:
            query += constant.tdr_domain_sub_query
            parameters.append(domain_name)
        if state:
            query += constant.tdr_delivery_state_sub_query
            parameters.append(state)

        query += """
                GROUP BY 
                    om.order_date, om.delivery_district
                ORDER BY 
                    om.order_date, intrastate_orders_percentage DESC
            )
            SELECT * FROM FinalResult;
        """

        df = self.db_utility.execute_query(query, parameters)

        return df

    @log_function_call(ondcLogger)
    def fetch_top5_seller_states(self, start_date, end_date, category=None, sub_category=None, domain=None,
                                 state=None):

        table_name = self.get_table_name(category, sub_category)

        query = f"""
            SELECT 
                sub.delivery_state,
                COALESCE(NULLIF(TRIM(sub.seller_state), ''), 'Missing') AS seller_state,
                sub.order_demand,
                ROUND(sub.flow_percentage,2) as flow_percentage
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
                    WHERE swdlo.order_date BETWEEN %s AND %s
                      AND swdlo.delivery_state <> ''
        """

        parameters = [start_date, end_date]

        if category and category != 'None':
            query += constant.swdlo_cat_sub_query
            parameters.append(category)
        if sub_category and sub_category != 'None':
            query += constant.swdlo_sub_cat_sub_query
            parameters.append(sub_category)
        if domain:
            query += constant.swdlo_domain_sub_query
            parameters.append(domain)

        query += """
                    GROUP BY swdlo.delivery_state
                ) total ON om.delivery_state = total.delivery_state
                WHERE 
                 om.order_date BETWEEN %s AND %s
        """

        parameters.extend([start_date, end_date])

        if category and category != 'None':
            query += constant.tdr_category_sub_query
            parameters.append(category)
        if sub_category and sub_category != 'None':
            query += constant.tdr_sub_category_sub_query
            parameters.append(sub_category)
        if domain:
            query += constant.tdr_domain_sub_query
            parameters.append(domain)
        if state:
            query += constant.tdr_delivery_state_sub_query
            parameters.append(state)

        query += """
                GROUP BY 
                    om.delivery_state, om.seller_state, total.total_orders
            ) sub
            WHERE sub.rn <= 5
            ORDER BY sub.delivery_state, sub.flow_percentage DESC;
        """

        df = self.db_utility.execute_query(query, parameters)
        return df

    @log_function_call(ondcLogger)
    def fetch_top5_seller_districts(self, start_date, end_date, category=None, sub_category=None, domain=None,
                                    state=None, district=None):

        table_name = self.get_table_name(category, sub_category)

        query = f"""
            SELECT 
                sub.delivery_district,
                COALESCE(NULLIF(TRIM(sub.seller_district), ''), 'Missing') AS seller_district,
                sub.order_demand,
                ROUND(sub.flow_percentage, 2) AS flow_percentage
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
                    WHERE swdlo.order_date BETWEEN %s AND %s
                      AND swdlo.delivery_district <> ''
        """

        parameters = [start_date, end_date]

        if category and category != 'None':
            query += constant.swdlo_cat_sub_query
            parameters.append(category)
        if sub_category and sub_category != 'None':
            query += constant.swdlo_sub_cat_sub_query
            parameters.append(sub_category)
        if domain:
            query += constant.swdlo_domain_sub_query
            parameters.append(domain)
        if state:
            query += constant.swdlo_delivery_st_sq
            parameters.append(state)

        query += """
                    GROUP BY swdlo.delivery_district
                ) total ON upper(om.delivery_district) = upper(total.delivery_district)
                WHERE om.order_date BETWEEN %s AND %s
        """

        parameters.extend([start_date, end_date])

        if category and category != 'None':
            query += constant.tdr_category_sub_query
            parameters.append(category)
        if sub_category and sub_category != 'None':
            query += constant.tdr_sub_category_sub_query
            parameters.append(sub_category)
        if domain:
            query += constant.tdr_domain_sub_query
            parameters.append(domain)
        if state:
            query += constant.tdr_delivery_state_sub_query
            parameters.append(state)
        if district:
            query += " AND upper(om.delivery_district) = upper(%s)"
            parameters.append(district)

        query += """
                GROUP BY 
                    om.delivery_district, om.seller_district, total.total_orders
            ) sub
            WHERE sub.rn <= 5
            ORDER BY sub.delivery_district, sub.flow_percentage DESC;
        """

        df = self.db_utility.execute_query(query, parameters)
        return df

    @log_function_call(ondcLogger)
    def fetch_cumulative_orders_statedata(self, start_date, end_date,
                                          category=None, sub_category=None,
                                          domain=None, state=None):

        table_name = self.get_table_name(category, sub_category)

        query = f'''
            SELECT 
                delivery_state_code AS delivery_state_code,
                delivery_state AS delivery_state,
                delivery_district AS delivery_district,
                sum(total_orders_delivered) AS total_orders_delivered,
                SUM(total_items) AS total_items,
                ROUND((sum(total_orders_delivered::numeric)/ 
                SUM(NULLIF(total_items::numeric, 0))), 2) AS avg_items_per_order,
                SUM(intradistrict_orders) AS intradistrict_orders,
                AVG(intradistrict_orders_percentage) AS intradistrict_percentage,
                SUM(intrastate_orders) AS intrastate_orders,
                AVG(intrastate_orders_percentage) AS intrastate_percentage
            FROM {table_name}
            WHERE
                order_date BETWEEN %s AND %s
        '''

        parameters = [start_date, end_date]

        if domain:
            query += constant.domain_sub_query
            parameters.append(domain)

        if category and category != 'None':
            query += constant.category_sub_query
            parameters.append(category)

        if sub_category:
            query += constant.sub_category_sub_query
            parameters.append(sub_category)

        if state:
            query += constant.delivery_state_sub_query
            parameters.append(state)

        query += ('GROUP BY delivery_state_code, delivery_state, delivery_district ORDER BY delivery_state_code, '
                  'total_orders_delivered DESC')

        aggregated_df = self.db_utility.execute_query(query, parameters)

        return aggregated_df

    @log_function_call(ondcLogger)
    def fetch_cumulative_orders_statewise(self, start_date, end_date, category=None, sub_category=None, domain=None,
                                          state=None):
        table_name = self.get_table_name(category, sub_category)

        query = f"""
            SELECT 
                delivery_state_code AS delivery_state_code,
                delivery_state AS delivery_state,
                sum(total_orders_delivered) AS total_orders,
                SUM(total_items) AS total_items_delivered,
                ROUND((SUM(total_items::numeric)/SUM(NULLIF(total_orders_delivered::numeric,0))),2) 
                AS avg_items_per_order,
                SUM(intradistrict_orders) AS intradistrict_orders,
                ROUND(100*SUM(intradistrict_orders)/(SUM(NULLIF(total_orders_delivered,0))),2) 
                AS intradistrict_percentage,
                SUM(intrastate_orders) AS intrastate_orders,
                ROUND(100*(SUM(intrastate_orders)/SUM(NULLIF(total_orders_delivered,0))),2) AS intrastate_percentage
            FROM {table_name}
            WHERE
                order_date BETWEEN %s AND %s
        """

        parameters = [start_date, end_date]

        if domain:
            query += constant.domain_sub_query
            parameters.append(domain)

        if category and category != 'None':
            query += constant.category_sub_query
            parameters.append(category)

        if sub_category:
            query += constant.sub_category_sub_query
            parameters.append(sub_category)

        if state:
            query += constant.delivery_state_sub_query
            parameters.append(state)

        query += ' GROUP BY 1, 2 ORDER BY 2, 4 DESC'

        aggregated_df = self.db_utility.execute_query(query, parameters)

        return aggregated_df

    @log_function_call(ondcLogger)
    def build_district_ranking_query(self, table_name, category, sub_category):
        query = f"""
            WITH DistrictRanking AS (
                SELECT
                    swdlo.delivery_state AS delivery_state_code,
                    swdlo.delivery_state AS delivery_state,
                    swdlo.delivery_district AS delivery_district,
                    SUM(swdlo.total_orders_delivered) AS total_orders_in_district,
                    ROW_NUMBER() OVER (PARTITION BY swdlo.delivery_state 
                    ORDER BY SUM(swdlo.total_orders_delivered) DESC) AS rank_in_state
                FROM
                    {table_name} swdlo
                WHERE
                    swdlo.order_date BETWEEN %(start_date)s AND %(end_date)s
                    AND swdlo.delivery_state <> ''
        """

        if category and category != 'None':
            query += constant.swdlo_category_ranking_sub_query

        if sub_category:
            query += constant.swdlo_sub_category_ranking_sub_query

        query += """
                GROUP BY
                    swdlo.delivery_state,
                    swdlo.delivery_state_code,
                    swdlo.delivery_district
            )
        """
        return query

    def build_subcategory_ranking_query(self, table_name, sub_category, category):
        query = f"""
            SubCategoryRanking AS (
                SELECT
                    scp.delivery_state AS delivery_state_code,
                    scp.delivery_state AS delivery_state,
                    scp.sub_category,
                    SUM(scp.total_orders_delivered) AS total_orders_in_district,
                    ROW_NUMBER() OVER (PARTITION BY scp.delivery_state 
                    ORDER BY SUM(scp.total_orders_delivered) DESC) AS rank_in_state
                FROM
                    {table_name} scp
                WHERE
                    scp.order_date BETWEEN %(start_date)s AND %(end_date)s
                    AND scp.delivery_state <> ''
                    AND scp.sub_category <> 'ALL'
        """
        if category and category != 'None':
            query += constant.sub_category_ranking_sub_query

        if sub_category:
            query += constant.category_ranking_sub_query

        query += """
                GROUP BY
                    scp.delivery_state,
                    scp.delivery_state_code,
                    scp.sub_category
            )
        """
        return query

    def build_active_sellers_query(self, category, sub_category):
        query = f"""
            ActiveSellers AS (
                SELECT
                    ds.seller_state AS seller_state_code,
                    ds.seller_state AS seller_state,
                    COUNT(DISTINCT trim(lower(ds.provider_key))) AS total_active_sellers
                FROM
                    {constant.SELLER_TABLE} ds
                WHERE
                    ds.order_date BETWEEN %(start_date)s AND %(end_date)s
                    AND ds.seller_state <> ''
        """
        if category and category != 'None':
            query += constant.seller_category_ranking_sub_query

        if sub_category:
            query += constant.seller_sub_category_ranking_sub_query

        query += """
                GROUP BY
                    ds.seller_state,
                    ds.seller_state_code
            )
        """
        return query

    def build_aggregated_data_query(self, table_name, category, sub_category):
        query = f"""
            AggregatedData AS (
                SELECT
                    swdlo.delivery_state_code AS delivery_state_code,
                    swdlo.delivery_state AS delivery_state,
                    COUNT(DISTINCT swdlo.delivery_district) AS total_districts,
                    SUM(swdlo.total_orders_delivered) AS delivered_orders,
                    SUM(swdlo.total_items) AS total_items,
                    ROUND(COALESCE(SUM(swdlo.total_items::numeric) / 
                    NULLIF(SUM(swdlo.total_orders_delivered::numeric), 0), 0), 2) AS avg_items_per_order
                FROM
                    {table_name} swdlo
                WHERE
                    swdlo.order_date BETWEEN %(start_date)s AND %(end_date)s
                    AND swdlo.delivery_state <> ''
        """
        if category and category != 'None':
            query += constant.swdlo_category_ranking_sub_query
        if sub_category:
            query += constant.swdlo_sub_category_ranking_sub_query

        query += """
                GROUP BY
                    swdlo.delivery_state,
                    swdlo.delivery_state_code
            )
        """
        return query

    def build_state_ranking_query(self, table_name, category, sub_category):
        query = f"""
            StateRanking AS (
                SELECT
                    swdlo.delivery_state AS delivery_state,
                    swdlo.delivery_state_code AS delivery_state_code,
                    SUM(swdlo.total_orders_delivered) AS total_orders_in_state,
                    ROW_NUMBER() OVER (ORDER BY SUM(swdlo.total_orders_delivered) DESC) AS rank_in_state
                FROM
                    {table_name} swdlo
                WHERE
                    swdlo.order_date BETWEEN %(start_date)s AND %(end_date)s
                    AND swdlo.delivery_state <> ''
        """
        if category and category != 'None':
            query += constant.swdlo_category_ranking_sub_query

        if sub_category:
            query += constant.swdlo_sub_category_ranking_sub_query

        query += """
                GROUP BY
                    swdlo.delivery_state,
                    swdlo.delivery_state_code
            )
        """
        return query

    def build_subcategory_ranking_total_query(self, sub_category, category):
        query = f"""
            SubCategoryRankingTotal AS (
                SELECT
                    scp.sub_category,
                    SUM(scp.total_orders_delivered) AS total_orders_in_district,
                    ROW_NUMBER() OVER (ORDER BY SUM(scp.total_orders_delivered) DESC) AS rank_in_state
                FROM
                    {constant.SUB_CATEGORY_PENETRATION_TABLE} scp
                WHERE
                    scp.order_date BETWEEN %(start_date)s AND %(end_date)s
                    AND scp.sub_category <> 'ALL'
        """
        if category and category != 'None':
            query += constant.sub_category_ranking_sub_query

        if sub_category:
            query += constant.category_ranking_sub_query

        query += """
                GROUP BY
                    scp.sub_category
            )
        """
        return query

    def build_active_sellers_total_query(self, category, sub_category):
        query = f"""
            ActiveSellersTotal AS (
                SELECT
                    'TT' AS seller_state_code,
                    'TOTAL' AS seller_state,
                    COUNT(DISTINCT trim(lower(ds.provider_key))) AS total_active_sellers
                FROM
                    {constant.SELLER_TABLE} ds
                WHERE
                    ds.order_date BETWEEN %(start_date)s AND %(end_date)s
        """
        if category and category != 'None':
            query += constant.seller_category_ranking_sub_query

        if sub_category:
            query += constant.seller_sub_category_ranking_sub_query

        query += """
            )
        """
        return query

    def build_aggregated_data_total_query(self, table_name, category, sub_category):
        query = f"""
            AggregatedDataTotal AS (
                SELECT
                    'TT' AS delivery_state_code,
                    'TOTAL' AS delivery_state,
                    COUNT(DISTINCT swdlo.delivery_district) AS total_districts,
                    SUM(swdlo.total_orders_delivered) AS delivered_orders,
                    SUM(swdlo.total_items) AS total_items,
                    ROUND(COALESCE(SUM(swdlo.total_items::numeric) / 
                    NULLIF(SUM(swdlo.total_orders_delivered::numeric), 0), 0), 2) AS avg_items_per_order
                FROM
                    {table_name} swdlo
                WHERE
                    swdlo.order_date BETWEEN %(start_date)s AND %(end_date)s
        """
        if category and category != 'None':
            query += constant.swdlo_category_ranking_sub_query

        if sub_category:
            query += constant.swdlo_sub_category_ranking_sub_query

        query += """
            )
        """
        return query


    def fetch_total_orders(self, start_date, end_date, category=None,
                           sub_category=None, domain=None, state=None):
        table_name = constant.DISTRICT_TABLE
        if category and not sub_category:
            table_name = constant.CATEGORY_TABLE
        elif category and sub_category:
            table_name = constant.SUB_CATEGORY_TABLE

        parameters = {
            'start_date': start_date,
            'end_date': end_date,
        }

        query = f"""
            WITH DistrictRanking AS (
                SELECT
                    swdlo.delivery_state AS delivery_state_code,
                    swdlo.delivery_state AS delivery_state,
                    swdlo.delivery_district AS delivery_district,
                    SUM(swdlo.total_orders_delivered) AS total_orders_in_district,
                    ROW_NUMBER() OVER (PARTITION BY swdlo.delivery_state ORDER BY SUM(swdlo.total_orders_delivered) DESC) AS rank_in_state
                FROM
                    {table_name} swdlo
                WHERE
                    swdlo.order_date BETWEEN %(start_date)s AND %(end_date)s
                    AND swdlo.delivery_state <> ''
        """

        if category and category != 'None':
            query += constant.category_ranking_sub_query
            parameters['category'] = category

        if sub_category:
            query += constant.swdlo_sub_category_ranking_sub_query
            parameters['sub_category'] = sub_category

        query += """
                GROUP BY
                    swdlo.delivery_state,
                    swdlo.delivery_state_code,
                    swdlo.delivery_district
            ),
            
        """
        if category and category != 'None':
            query += constant.category_ranking_sub_query

        if sub_category:
            query += constant.sub_category_ranking_sub_query

        query += f"""
                
            ActiveSellers AS (
                SELECT
                    ds.seller_state AS seller_state_code,
                    ds.seller_state AS seller_state,
                    COUNT(DISTINCT trim(lower(ds.provider_key))) AS total_active_sellers
                FROM
                    {constant.SELLER_TABLE} ds
                WHERE
                    ds.order_date BETWEEN %(start_date)s AND %(end_date)s
        """
        if category and category != 'None':
            query += constant.seller_category_ranking_sub_query

        if sub_category:
            query += constant.seller_sub_category_ranking_sub_query

        query += f"""
                GROUP BY
                    ds.seller_state,
                    ds.seller_state_code
            ),
            AggregatedData AS (
                SELECT
                    swdlo.delivery_state_code AS delivery_state_code,
                    swdlo.delivery_state AS delivery_state,
                    COUNT(DISTINCT swdlo.delivery_district) AS total_districts,
                    SUM(swdlo.total_orders_delivered) AS delivered_orders,
                    SUM(swdlo.total_items) AS total_items,
                    ROUND(COALESCE(SUM(swdlo.total_items::numeric) / NULLIF(SUM(swdlo.total_orders_delivered::numeric), 0), 0), 2) AS avg_items_per_order
                FROM
                    {table_name} swdlo
                WHERE
                    swdlo.order_date BETWEEN %(start_date)s AND %(end_date)s
                    AND swdlo.delivery_state <> ''
        """
        if category and category != 'None':
            query += constant.swdlo_category_ranking_sub_query

        if sub_category:
            query += constant.swdlo_sub_category_ranking_sub_query

        query += f"""
                GROUP BY
                    swdlo.delivery_state,
                    swdlo.delivery_state_code
            ),
            StateRanking AS (
                SELECT
                    swdlo.delivery_state AS delivery_state,
                    swdlo.delivery_state_code AS delivery_state_code,
                    SUM(swdlo.total_orders_delivered) AS total_orders_in_state,
                    ROW_NUMBER() OVER (ORDER BY SUM(swdlo.total_orders_delivered) DESC) AS rank_in_state
                FROM
                    {table_name} swdlo
                WHERE
                    swdlo.order_date BETWEEN %(start_date)s AND %(end_date)s
                    AND swdlo.delivery_state <> ''
        """
        if category and category != 'None':
            query += constant.swdlo_category_ranking_sub_query

        if sub_category:
            query += constant.swdlo_sub_category_ranking_sub_query

        query += """
                GROUP BY
                    swdlo.delivery_state,
                    swdlo.delivery_state_code
            ),

        """

        query += f"""
                
            ActiveSellersTotal AS (
                SELECT
                    'TT' AS seller_state_code,
                    'TOTAL' AS seller_state,
                    COUNT(DISTINCT trim(lower(ds.provider_key))) AS total_active_sellers
                FROM
                    {constant.SELLER_TABLE} ds
                WHERE
                    ds.order_date BETWEEN %(start_date)s AND %(end_date)s
        """
        if category and category != 'None':
            query += constant.seller_category_ranking_sub_query

        if sub_category:
            query += constant.seller_sub_category_ranking_sub_query

        query += f"""
            ),
            AggregatedDataTotal AS (
                SELECT
                    'TT' AS delivery_state_code,
                    'TOTAL' AS delivery_state,
                    COUNT(DISTINCT CASE WHEN swdlo.delivery_district <> '' THEN 
                    CONCAT(swdlo.delivery_state, '_', swdlo.delivery_district) END) AS total_districts,
                    SUM(swdlo.total_orders_delivered) AS delivered_orders,
                    SUM(swdlo.total_items) AS total_items,
                    ROUND(COALESCE(SUM(swdlo.total_items::numeric) / NULLIF(SUM(swdlo.total_orders_delivered::numeric), 0), 0), 2) AS avg_items_per_order
                FROM
                    {table_name} swdlo
                WHERE
                    swdlo.order_date BETWEEN %(start_date)s AND %(end_date)s
        """
        if category and category != 'None':
            query += constant.swdlo_category_ranking_sub_query

        if sub_category:
            query += constant.swdlo_sub_category_ranking_sub_query

        query += """
            )
            SELECT
                AD.delivery_state_code,
                AD.delivery_state,
                AD.total_districts,
                AD.delivered_orders,
                AD.avg_items_per_order,
                AD.total_items,
                COALESCE(
                    CASE
                        WHEN ASel.total_active_sellers < 3 THEN 0
                        ELSE ASel.total_active_sellers
                    END, 0) AS total_active_sellers,
                DR.delivery_district AS most_ordering_district
            FROM
                AggregatedData AD
            LEFT JOIN
                ActiveSellers ASel ON AD.delivery_state = ASel.seller_state
            LEFT JOIN
                (SELECT * FROM DistrictRanking WHERE rank_in_state = 1) DR ON AD.delivery_state = DR.delivery_state
            UNION ALL
            SELECT
                'TT' AS delivery_state_code,
                'TOTAL' AS delivery_state,
                ADT.total_districts,
                ADT.delivered_orders,
                ADT.avg_items_per_order,
                ADT.total_items,
                COALESCE(
                    CASE
                        WHEN ASelt.total_active_sellers < 3 THEN 0
                        ELSE ASelt.total_active_sellers
                    END, 0) AS total_active_sellers,
                SRnk.delivery_state AS most_ordering_district
            FROM
                AggregatedDataTotal ADT
            LEFT JOIN
                ActiveSellersTotal ASelt ON 1=1
            LEFT JOIN
                StateRanking SRnk ON SRnk.rank_in_state = 1
        """

        orders_count = self.db_utility.execute_query(query, parameters)
        return orders_count


    def fetch_total_orders_with_category(self, start_date, end_date, category=None,
                           sub_category=None, domain=None, state=None):
        table_name = constant.DISTRICT_TABLE
        if category and not sub_category:
            table_name = constant.CATEGORY_TABLE
        elif category and sub_category:
            table_name = constant.SUB_CATEGORY_TABLE

        parameters = {
            'start_date': start_date,
            'end_date': end_date,
        }

        query = f"""
            WITH DistrictRanking AS (
                SELECT
                    swdlo.delivery_state AS delivery_state_code,
                    swdlo.delivery_state AS delivery_state,
                    swdlo.delivery_district AS delivery_district,
                    SUM(swdlo.total_orders_delivered) AS total_orders_in_district,
                    ROW_NUMBER() OVER (PARTITION BY swdlo.delivery_state ORDER BY SUM(swdlo.total_orders_delivered) DESC) AS rank_in_state
                FROM
                    {table_name} swdlo
                WHERE
                    swdlo.order_date BETWEEN %(start_date)s AND %(end_date)s
                    AND swdlo.delivery_state <> ''
        """

        if category and category != 'None':
            query += constant.category_ranking_sub_query
            parameters['category'] = category

        if sub_category:
            query += constant.swdlo_sub_category_ranking_sub_query
            parameters['sub_category'] = sub_category

        query += f"""
                GROUP BY
                    swdlo.delivery_state,
                    swdlo.delivery_state_code,
                    swdlo.delivery_district
            ),
            SubCategoryRanking AS (
                SELECT
                    scp.delivery_state AS delivery_state_code,
                    scp.delivery_state AS delivery_state,
                    scp.sub_category,
                    SUM(scp.total_orders_delivered) AS total_orders_in_district,
                    ROW_NUMBER() OVER (PARTITION BY scp.delivery_state ORDER BY SUM(scp.total_orders_delivered) DESC) AS rank_in_state
                FROM
                    {constant.SUB_CATEGORY_PENETRATION_TABLE} scp
                WHERE
                    scp.order_date BETWEEN %(start_date)s AND %(end_date)s
                    AND scp.delivery_state <> ''
                    AND scp.sub_category <> 'ALL'
        """
        if category and category != 'None':
            query += constant.category_ranking_sub_query

        if sub_category:
            query += constant.sub_category_ranking_sub_query

        query += f"""
                GROUP BY
                    scp.delivery_state,
                    scp.delivery_state_code,
                    scp.sub_category
            ),
            ActiveSellers AS (
                SELECT
                    ds.seller_state AS seller_state_code,
                    ds.seller_state AS seller_state,
                    COUNT(DISTINCT trim(lower(ds.provider_key))) AS total_active_sellers
                FROM
                    {constant.SELLER_TABLE} ds
                WHERE
                    ds.order_date BETWEEN %(start_date)s AND %(end_date)s
        """
        if category and category != 'None':
            query += constant.seller_category_ranking_sub_query

        if sub_category:
            query += constant.seller_sub_category_ranking_sub_query

        query += f"""
                GROUP BY
                    ds.seller_state,
                    ds.seller_state_code
            ),
            AggregatedData AS (
                SELECT
                    swdlo.delivery_state_code AS delivery_state_code,
                    swdlo.delivery_state AS delivery_state,
                    COUNT(DISTINCT swdlo.delivery_district) AS total_districts,
                    SUM(swdlo.total_orders_delivered) AS delivered_orders,
                    SUM(swdlo.total_items) AS total_items,
                    ROUND(COALESCE(SUM(swdlo.total_items::numeric) / NULLIF(SUM(swdlo.total_orders_delivered::numeric), 0), 0), 2) AS avg_items_per_order
                FROM
                    {table_name} swdlo
                WHERE
                    swdlo.order_date BETWEEN %(start_date)s AND %(end_date)s
                    AND swdlo.delivery_state <> ''
        """
        if category and category != 'None':
            query += constant.swdlo_category_ranking_sub_query

        if sub_category:
            query += constant.swdlo_sub_category_ranking_sub_query

        query += f"""
                GROUP BY
                    swdlo.delivery_state,
                    swdlo.delivery_state_code
            ),
            StateRanking AS (
                SELECT
                    swdlo.delivery_state AS delivery_state,
                    swdlo.delivery_state_code AS delivery_state_code,
                    SUM(swdlo.total_orders_delivered) AS total_orders_in_state,
                    ROW_NUMBER() OVER (ORDER BY SUM(swdlo.total_orders_delivered) DESC) AS rank_in_state
                FROM
                    {table_name} swdlo
                WHERE
                    swdlo.order_date BETWEEN %(start_date)s AND %(end_date)s
                    AND swdlo.delivery_state <> ''
        """
        if category and category != 'None':
            query += constant.swdlo_category_ranking_sub_query

        if sub_category:
            query += constant.swdlo_sub_category_ranking_sub_query

        query += f"""
                GROUP BY
                    swdlo.delivery_state,
                    swdlo.delivery_state_code
            ),
            SubCategoryRankingTotal AS (
                SELECT
                    scp.sub_category,
                    SUM(scp.total_orders_delivered) AS total_orders_in_district,
                    ROW_NUMBER() OVER (ORDER BY SUM(scp.total_orders_delivered) DESC) AS rank_in_state
                FROM
                    {constant.SUB_CATEGORY_PENETRATION_TABLE} scp
                WHERE
                    scp.order_date BETWEEN %(start_date)s AND %(end_date)s
                    AND scp.sub_category <> 'ALL'
        """
        if category and category != 'None':
            query += constant.category_ranking_sub_query

        if sub_category:
            query += constant.sub_category_ranking_sub_query

        query += f"""
                GROUP BY
                    scp.sub_category
            ),
            ActiveSellersTotal AS (
                SELECT
                    'TT' AS seller_state_code,
                    'TOTAL' AS seller_state,
                    COUNT(DISTINCT trim(lower(ds.provider_key))) AS total_active_sellers
                FROM
                    {constant.SELLER_TABLE} ds
                WHERE
                    ds.order_date BETWEEN %(start_date)s AND %(end_date)s
        """
        if category and category != 'None':
            query += constant.seller_category_ranking_sub_query

        if sub_category:
            query += constant.seller_sub_category_ranking_sub_query

        query += f"""
            ),
            AggregatedDataTotal AS (
                SELECT
                    'TT' AS delivery_state_code,
                    'TOTAL' AS delivery_state,
                    COUNT(DISTINCT CASE WHEN swdlo.delivery_district <> '' THEN 
                    CONCAT(swdlo.delivery_state, '_', swdlo.delivery_district) END) AS total_districts,
                    SUM(swdlo.total_orders_delivered) AS delivered_orders,
                    SUM(swdlo.total_items) AS total_items,
                    ROUND(COALESCE(SUM(swdlo.total_items::numeric) / NULLIF(SUM(swdlo.total_orders_delivered::numeric), 0), 0), 2) AS avg_items_per_order
                FROM
                    {table_name} swdlo
                WHERE
                    swdlo.order_date BETWEEN %(start_date)s AND %(end_date)s
        """
        if category and category != 'None':
            query += constant.swdlo_category_ranking_sub_query

        if sub_category:
            query += constant.swdlo_sub_category_ranking_sub_query

        query += """
            )
            SELECT
                AD.delivery_state_code,
                AD.delivery_state,
                AD.total_districts,
                AD.delivered_orders,
                AD.avg_items_per_order,
                AD.total_items,
                COALESCE(
                    CASE
                        WHEN ASel.total_active_sellers < 3 THEN 0
                        ELSE ASel.total_active_sellers
                    END, 0) AS total_active_sellers,
                DR.delivery_district AS most_ordering_district,
                SR.sub_category
            FROM
                AggregatedData AD
            LEFT JOIN
                ActiveSellers ASel ON AD.delivery_state = ASel.seller_state
            LEFT JOIN
                (SELECT * FROM DistrictRanking WHERE rank_in_state = 1) DR ON AD.delivery_state = DR.delivery_state
            LEFT JOIN
                (SELECT * FROM SubCategoryRanking WHERE rank_in_state = 1) SR ON AD.delivery_state = SR.delivery_state
            UNION ALL
            SELECT
                'TT' AS delivery_state_code,
                'TOTAL' AS delivery_state,
                ADT.total_districts,
                ADT.delivered_orders,
                ADT.avg_items_per_order,
                ADT.total_items,
                COALESCE(
                    CASE
                        WHEN ASelt.total_active_sellers < 3 THEN 0
                        ELSE ASelt.total_active_sellers
                    END, 0) AS total_active_sellers,
                SRnk.delivery_state AS most_ordering_district,
                SRt.sub_category AS sub_category
            FROM
                AggregatedDataTotal ADT
            LEFT JOIN
                ActiveSellersTotal ASelt ON 1=1
            LEFT JOIN
                SubCategoryRankingTotal SRt ON SRt.rank_in_state = 1
            LEFT JOIN
                StateRanking SRnk ON SRnk.rank_in_state = 1
        """

        orders_count = self.db_utility.execute_query(query, parameters)
        return orders_count

    @log_function_call(ondcLogger)
    def fetch_total_orders_prev(self, start_date, end_date, category=None,
                                sub_category=None, domain=None, state=None):

        parameters = {
            'start_date': start_date,
            'end_date': end_date,
        }
        table_name = self.get_table_name(category, sub_category)

        query = f"""
            WITH 
            ActiveSellers AS (
                SELECT
                    ds.seller_state AS seller_state_code,
                    ds.seller_state AS seller_state,
                    COUNT(DISTINCT ds.provider_key) AS total_active_sellers
                FROM
                    {constant.SELLER_TABLE} ds
                WHERE
                    ds.order_date BETWEEN %(start_date)s AND %(end_date)s
                    AND ds.seller_state <> ''
        """
        if category and category != 'None':
            parameters['category'] = category
            query += constant.seller_category_ranking_sub_query

        if sub_category and sub_category != 'None':
            parameters['sub_category'] = sub_category
            query += constant.seller_sub_category_ranking_sub_query

        query += f""" GROUP BY ds.seller_state, ds.seller_state_code ), AggregatedData AS ( SELECT 
        swdlo.delivery_state_code AS delivery_state_code, swdlo.delivery_state AS delivery_state, COUNT(DISTINCT 
        swdlo.delivery_district) AS total_districts, SUM(swdlo.total_orders_delivered) AS delivered_orders, 
        SUM(swdlo.total_items) AS total_items, ROUND(COALESCE(SUM(swdlo.total_items::numeric) / NULLIF(SUM(
        swdlo.total_orders_delivered::numeric), 0), 0), 2) AS avg_items_per_order FROM {table_name} swdlo
                WHERE
                    swdlo.order_date BETWEEN %(start_date)s AND %(end_date)s
                    AND swdlo.delivery_state <> ''
        """
        if category and category != 'None':
            query += constant.swdlo_category_ranking_sub_query

        if sub_category:
            query += constant.swdlo_sub_category_ranking_sub_query

        query += f"""
                GROUP BY
                    swdlo.delivery_state,
                    swdlo.delivery_state_code
            ),
            ActiveSellersTotal AS (
                SELECT
                    'TT' AS seller_state_code,
                    'TOTAL' AS seller_state,
                    COUNT(DISTINCT trim(lower(ds.provider_key))) AS total_active_sellers
                FROM
                    {constant.SELLER_TABLE} ds
                WHERE
                    ds.order_date BETWEEN %(start_date)s AND %(end_date)s
        """
        if category and category != 'None':
            query += constant.seller_category_ranking_sub_query

        if sub_category:
            query += constant.seller_sub_category_ranking_sub_query

        query += f""" ), AggregatedDataTotal AS ( SELECT 'TT' AS delivery_state_code, 'TOTAL' AS delivery_state, 
        COUNT(DISTINCT swdlo.delivery_district) AS total_districts, SUM(swdlo.total_orders_delivered) AS 
        delivered_orders, SUM(swdlo.total_items) AS total_items, ROUND(COALESCE(SUM(swdlo.total_items::numeric) / 
        NULLIF(SUM(swdlo.total_orders_delivered::numeric), 0), 0), 2) AS avg_items_per_order FROM {table_name} swdlo
                WHERE
                    swdlo.order_date BETWEEN %(start_date)s AND %(end_date)s
        """
        if category and category != 'None':
            query += constant.swdlo_category_ranking_sub_query

        if sub_category:
            query += constant.swdlo_sub_category_ranking_sub_query

        query += """
            )
            SELECT
                AD.delivery_state_code,
                AD.delivery_state,
                AD.total_districts,
                AD.delivered_orders,
                AD.avg_items_per_order,
                AD.total_items,
                COALESCE(
                    CASE
                        WHEN ASel.total_active_sellers < 3 THEN 0
                        ELSE ASel.total_active_sellers
                    END, 0) AS total_active_sellers
            FROM
                AggregatedData AD
            LEFT JOIN
                ActiveSellers ASel ON AD.delivery_state = ASel.seller_state
            UNION ALL
            SELECT
                'TT' AS delivery_state_code,
                'TOTAL' AS delivery_state,
                ADT.total_districts,
                ADT.delivered_orders,
                ADT.avg_items_per_order,
                ADT.total_items,
                COALESCE(
                    CASE
                        WHEN ASelt.total_active_sellers < 3 THEN 0
                        ELSE ASelt.total_active_sellers
                    END, 0) AS total_active_sellers
            FROM
                AggregatedDataTotal ADT
            JOIN
                ActiveSellersTotal ASelt ON 1=1
        """

        orders_count = self.db_utility.execute_query(query, parameters)
        return orders_count

    @log_function_call(ondcLogger)
    def fetch_total_orders_rv(self, start_date, end_date, category=None,
                              sub_category=None, domain=None, state=None):
        table_name = constant.RV_DISTRICT_TABLE

        query = f"""
                       select 
                       sum(total_orders_delivered) as total_orders_delivered,
                       sum(total_items) as total_items
                    FROM 
                        {table_name}
                    WHERE
                        order_date BETWEEN %s AND %s 
                """

        parameters = [start_date, end_date]

        orders_count = self.db_utility.execute_query(query, parameters, return_type='sql')
        total_orders = 0
        total_items = 0
        try:
            if orders_count and len(orders_count) > 0 and orders_count[0]:
                total_orders = orders_count[0][0] if orders_count[0][0] is not None else 0
                total_items = orders_count[0][1] if orders_count[0][1] is not None else 0
        except (IndexError, TypeError):
            pass
        return total_orders, total_items

    @log_function_call(ondcLogger)
    def fetch_district_count(self, start_date, end_date, category=None,
                             sub_category=None, domain=None, state=None):

        table_name = self.get_table_name(category, sub_category)

        query = f"""
                   select 
                   count(distinct delivery_district) as delivery_district_count
                FROM 
                    {table_name}
                WHERE
                    order_date BETWEEN %s AND %s 
            """

        parameters = [start_date, end_date]

        if category and category != 'None':
            query += constant.category_sub_query
            parameters.append(category)

        if sub_category:
            query += constant.sub_category_sub_query
            parameters.append(sub_category)

        if domain:
            query += constant.domain_sub_query
            parameters.append(domain)

        if state:
            query += constant.delivery_state_sub_query
            parameters.append(state)

        districts_count = self.db_utility.execute_query(query, parameters, return_type='sql')
        dist_count = 0
        try:
            if districts_count and districts_count[0]:
                dist_count = districts_count[0][0]
        except Exception as e:
            print(f"Error: {e}")

        return dist_count

    @log_function_call(ondcLogger)
    def fetch_max_subcategory_overall(self, start_date, end_date, category=None,
                                      sub_category=None, domain=None, state=None):

        table_name = constant.SUB_CATEGORY_PENETRATION_TABLE

        query = f"""
                   select coalesce(sub_category, 'Missing') as sub_category, 
                   sum(total_orders_delivered) as total_orders_delivered
                FROM 
                    {table_name}
                WHERE
                    order_date BETWEEN %s AND %s 
                    and sub_category <> 'ALL' 
                    and sub_category <> ''
            """

        parameters = [start_date, end_date]

        if category and category != 'None':
            query += constant.category_sub_query
            parameters.append(category)

        if sub_category:
            query += constant.sub_category_sub_query
            parameters.append(sub_category)

        if domain:
            query += constant.domain_sub_query
            parameters.append(domain)

        if state:
            query += constant.delivery_state_sub_query
            parameters.append(state)

        query += " GROUP BY 1"
        query += " order by total_orders_delivered desc limit 1"

        max_subcategory_data = self.db_utility.execute_query(query, parameters, return_type='sql')
        max_subcategory = constant.NO_DATA_MSG
        try:
            if max_subcategory_data and max_subcategory_data[0]:
                max_subcategory = max_subcategory_data[0][0]
        except Exception as e:
            print(f"Error: {e}")

        return max_subcategory

    @log_function_call(ondcLogger)
    def fetch_top_district_orders(self, start_date, end_date, category=None,
                                  sub_category=None, domain=None, state=None):

        selected_view = self.get_table_name(category, sub_category)

        query_template = """
            WITH DateRange AS (
                SELECT generate_series(%s::date, %s::date, '1 day') AS date
            ),
            TopDistricts AS (
                SELECT 
                    delivery_district,
                    SUM(total_orders_delivered) AS total_order_demand
                FROM {view}
                WHERE order_date::date BETWEEN %s::date AND %s::date
                AND delivery_district <> '' AND delivery_district IS NOT NULL
                AND delivery_state IS NOT NULL AND delivery_state <> ''
                {conditions}
                GROUP BY delivery_district
                ORDER BY total_order_demand DESC
                LIMIT 3
            ),
            FinalResult AS (
                SELECT
                    dr.date::date AS order_date,
                    td.delivery_district AS delivery_district,
                    COALESCE(SUM(foslm.total_orders_delivered), 0) AS total_orders_delivered
                FROM DateRange dr
                LEFT JOIN TopDistricts td ON TRUE
                LEFT JOIN {view} foslm ON foslm.delivery_district = td.delivery_district 
                AND foslm.order_date::date = dr.date
                WHERE td.delivery_district <> '' AND upper(td.delivery_district) <> upper('undefined') 
                AND td.delivery_district IS NOT NULL
                {final_conditions}
                GROUP BY 1, 2
                ORDER BY 1, 3 DESC
            )
            SELECT * FROM FinalResult;
            """

        conditions = []
        final_conditions = []
        parameters = [start_date, end_date, start_date, end_date]

        if category and category != 'None':
            conditions.append(constant.category_sub_query)
            parameters += [category]

        if sub_category and sub_category != 'None':
            conditions.append(constant.sub_category_sub_query)
            parameters += [sub_category]

        if domain:
            conditions.append(constant.domain_sub_query)
            parameters += [domain]

        if state:
            conditions.append(constant.delivery_state_sub_query)
            parameters += [state]

        if category and category != 'None':
            final_conditions.append("AND foslm.category = %s")
            parameters += [category]

        if sub_category and sub_category != 'None':
            final_conditions.append("AND foslm.sub_category = %s")
            parameters += [sub_category]

        if domain:
            final_conditions.append("AND foslm.domain = %s")
            parameters += [domain]

        if state:
            final_conditions.append("AND upper(foslm.delivery_state) = upper(%s)")
            parameters += [state]

        conditions_str = ' '.join(conditions)
        final_conditions_str = ' '.join(final_conditions)

        query = query_template.format(view=selected_view, conditions=conditions_str,
                                      final_conditions=final_conditions_str)

        df = self.db_utility.execute_query(query, parameters)

        return df

    @log_function_call(ondcLogger)
    def fetch_max_state_orders(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                               state=None):

        selected_view = self.get_table_name(category, sub_category)

        params = [start_date, end_date]

        query = f"""
            SELECT 
                'State' AS record_type,
                delivery_state as location,
                order_date,
                order_demand
            FROM 
                (
                    SELECT
                        delivery_state,
                        order_date,
                        SUM(total_orders_delivered) AS order_demand,
                        RANK() OVER (PARTITION BY delivery_state ORDER BY SUM(total_orders_delivered) DESC) AS rank
                    FROM
                        {selected_view}
                    WHERE 
                        order_date BETWEEN %s AND %s
                        and delivery_state <> ''
        """

        if state:
            query += constant.delivery_state_sub_query
            params.append(state)

        if category and category != 'None':
            query += constant.category_sub_query
            params.append(category)

        if sub_category and sub_category != 'None':
            query += constant.sub_category_sub_query
            params.append(sub_category)

        if domain_name:
            query += constant.domain_sub_query
            params.append(domain_name)

        query += """
                    GROUP BY
                        delivery_state, order_date
                    ORDER BY
                        delivery_state, rank, order_date
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

        selected_view = self.get_table_name(category, sub_category)

        params = [start_date, end_date]

        query = f"""
            SELECT 
                'District' AS record_type,
                delivery_district as location,
                order_date,
                order_count
            FROM 
                (
                    SELECT
                        delivery_district,
                        order_date,
                        SUM(total_orders_delivered) AS order_count,
                        RANK() OVER (PARTITION BY delivery_district ORDER BY SUM(total_orders_delivered)  DESC) AS rank
                    FROM
                        {selected_view}
                    WHERE 
                        order_date BETWEEN %s AND %s
                        and delivery_district <> '' and upper(delivery_district) <> upper('Undefined')
        """

        if state:
            query += constant.delivery_state_sub_query
            params.append(state)

        if category and category != 'None':
            query += constant.category_sub_query
            params.append(category)

        if sub_category and sub_category != 'None':
            query += constant.sub_category_sub_query
            params.append(sub_category)

        if domain_name:
            query += constant.domain_sub_query
            params.append(domain_name)

        query += """
                    GROUP BY
                        delivery_district, order_date
                    ORDER BY
                        delivery_district, rank, order_date
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
    def fetch_category_penetration_orders(self, start_date, end_date, category=None, sub_category=None, domain=None,
                                          state=None):
        selected_view = constant.SUB_CATEGORY_PENETRATION_TABLE

        parameters = [start_date, end_date]

        query = f'''
            SELECT 
                COALESCE(category, 'Missing') AS category,
                COALESCE(sub_category, 'Missing') AS sub_category,
                SUM(total_orders_delivered) AS order_demand  
            FROM 
                {selected_view} 
            WHERE 
                order_date BETWEEN %s AND %s
        '''

        if category and category != 'None':
            query += constant.category_sub_query
            parameters.append(category)
        if sub_category and sub_category != 'None':
            query += constant.sub_category_sub_query
            parameters.append(sub_category)
        if domain:
            query += constant.domain_sub_query
            parameters.append(domain)
        if state:
            query += constant.delivery_state_sub_query
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
    def fetch_category_penetration_sellers(self, start_date, end_date, category=None, sub_category=None, domain=None,
                                           state=None):

        query_sub_cat = f'''
                SELECT 
                    CASE 
                        WHEN category IS NULL OR category = '' THEN 'Missing'
                        ELSE category 
                    END AS category,
                    CASE 
                        WHEN sub_category IS NULL OR sub_category = '' THEN 'Missing'
                        ELSE sub_category 
                    END AS sub_category,
                    COUNT(distinct trim(lower(provider_key))) AS active_sellers_count  
                FROM 
                    {constant.SELLER_TABLE}
                WHERE 
                     order_date between %s and %s
            '''

        parameters = [start_date, end_date]

        if category:
            query_sub_cat += constant.category_sub_query
            parameters.append(category)
        if sub_category:
            query_sub_cat += constant.sub_category_sub_query
            parameters.append(sub_category)
        if domain:
            query_sub_cat += constant.domain_sub_query
            parameters.append(domain)
        if state:
            query_sub_cat += constant.seller_state_sub_query
            parameters.append(state)

        query_sub_cat += '''
                GROUP BY 
                    1,2
            '''

        query_all = f'''
                    SELECT 
                        CASE 
                            WHEN category IS NULL OR category = '' THEN 'Missing'
                            ELSE category 
                        END AS category,
                        'ALL' AS sub_category,
                        COUNT(distinct provider_key) AS active_sellers_count  
                    FROM 
                        {constant.SELLER_TABLE}
                    WHERE 
                         order_date between %s and %s
                '''

        parameters.append(start_date)
        parameters.append(end_date)

        if category:
            query_all += constant.category_sub_query
            parameters.append(category)
        if sub_category:
            query_all += constant.sub_category_sub_query
            parameters.append(sub_category)
        if domain:
            query_all += constant.domain_sub_query
            parameters.append(domain)
        if state:
            query_all += constant.seller_state_sub_query
            parameters.append(state)

        query_all += '''
                    GROUP BY 
                        1,2
                    ORDER BY 
                        active_sellers_count DESC

                '''

        query = f''' {query_sub_cat}
                            UNION 
                        {query_all}'''

        df = self.db_utility.execute_query(query, parameters)
        return df

    @log_function_call(ondcLogger)
    def fetch_active_sellers(self, start_date, end_date, category=None,
                             sub_category=None, domain=None, state=None):
        table_name = constant.SELLER_TABLE

        query = f"""
            SELECT 
                seller_state AS seller_state,
                seller_state_code AS seller_state_code,
                COUNT(DISTINCT provider_key) AS active_sellers_count
            FROM 
                {table_name}
            WHERE
                order_date BETWEEN %s AND %s
        """

        parameters = [start_date, end_date]

        if category and category != 'None':
            query += constant.category_sub_query
            parameters.append(category)

        if sub_category:
            query += constant.sub_category_sub_query
            parameters.append(sub_category)

        if domain:
            query += constant.domain_sub_query
            parameters.append(domain)

        if state:
            query += constant.seller_state_sub_query
            parameters.append(state)

        query += " GROUP BY 1, 2"

        df = self.db_utility.execute_query(query, parameters)

        return df

    @log_function_call(ondcLogger)
    def fetch_most_orders_delivered_to(self, start_date, end_date, category=None,
                                       sub_category=None, domain=None, state=None):
        table_name = self.get_table_name(category, sub_category)

        parameters = [start_date, end_date]
        where_conditions = " AND swdlo.delivery_state IS NOT NULL AND swdlo.delivery_state <> ''"

        if category and category != 'None':
            where_conditions += constant.swdlo_cat_sub_query
            parameters.append(category)
        if sub_category:
            where_conditions += constant.swdlo_sub_cat_sub_query
            parameters.append(sub_category)
        if domain:
            where_conditions += constant.swdlo_domain_sub_query
            parameters.append(domain)
        if state:
            where_conditions += constant.swdlo_delivery_st_sq
            parameters.append(state)

        if not state:
            query = f"""
                    SELECT
                        swdlo.delivery_state,
                        SUM(swdlo.total_orders_delivered) AS total_orders_in_state
                    FROM
                        {table_name} swdlo
                    WHERE
                        swdlo.order_date BETWEEN %s AND %s
                        {where_conditions}
                    GROUP BY
                        swdlo.delivery_state
                    ORDER BY
                        total_orders_in_state DESC
                    LIMIT 1;
                """
        else:
            query = f"""
                    WITH StateDistricts AS (
                        SELECT
                            swdlo.delivery_district,
                            SUM(swdlo.total_orders_delivered) AS total_orders_in_district
                        FROM
                            {table_name} swdlo
                        WHERE
                            swdlo.order_date BETWEEN %s AND %s
                            {where_conditions}
                        GROUP BY
                            swdlo.delivery_district
                        ORDER BY
                            total_orders_in_district DESC
                        LIMIT 1
                    )
                    SELECT
                        delivery_district AS top_district,
                        total_orders_in_district
                    FROM
                        StateDistricts;
                """

        most_delivering_areas = self.db_utility.execute_query(query, parameters, return_type='sql')

        value = constant.NO_DATA_MSG

        try:
            if most_delivering_areas and most_delivering_areas[0]:
                value = most_delivering_areas[0][0]
        except Exception as e:
            print(f"Error: {e}")

        return value

    @log_function_call(ondcLogger)
    def fetch_total_sellers(self, start_date, end_date, category=None,
                            sub_category=None, domain=None, state=None):
        table_name = constant.SELLER_TABLE

        query = f"""
                SELECT 
                    COUNT(DISTINCT provider_key) AS active_sellers_count
                FROM 
                    {table_name}
                WHERE
                    order_date BETWEEN %s AND %s
            """

        parameters = [start_date, end_date]

        if category and category != 'None':
            query += constant.category_sub_query
            parameters.append(category)

        if sub_category:
            query += constant.sub_category_sub_query
            parameters.append(sub_category)

        if domain:
            query += constant.domain_sub_query
            parameters.append(domain)

        if state:
            query += constant.seller_state_sub_query
            parameters.append(state)

        total_sellers = self.db_utility.execute_query(query, parameters, return_type='sql')
        sellers_count = 0

        try:
            if total_sellers and isinstance(total_sellers, list) and total_sellers[0]:
                sellers_count = total_sellers[0][0]
        except Exception as e:
            print(f"Error: {e}")

        return sellers_count

    @log_function_call(ondcLogger)
    def fetch_active_sellers_statedata(self, start_date, end_date,
                                       category=None, sub_category=None,
                                       domain=None, state=None):
        table_name = constant.SELLER_TABLE

        query = f"""
            SELECT 
                seller_state AS seller_state,
                seller_state_code AS seller_state_code,
                seller_district AS seller_district,
                COUNT(DISTINCT provider_key) AS active_sellers_count
            FROM 
                {table_name}
            WHERE
                order_date BETWEEN %s AND %s
        """

        parameters = [start_date, end_date]

        if category and category != 'None':
            query += constant.category_sub_query
            parameters.append(category)

        if sub_category:
            query += constant.sub_category_sub_query
            parameters.append(sub_category)

        if domain:
            query += constant.domain_sub_query
            parameters.append(domain)

        if state:
            query += constant.seller_state_sub_query
            parameters.append(state)

        query += " GROUP BY seller_district, seller_state, seller_state_code"

        df = self.db_utility.execute_query(query, parameters)

        return df

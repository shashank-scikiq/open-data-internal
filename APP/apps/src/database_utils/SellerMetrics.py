__author__ = "Shashank Katyayan"

import asyncio
import logging
from apps.src.database_utils.ClsBaseMetrics import Metric
from apps.utils import constant
import os
from datetime import datetime

from apps.utils import constant
import time
from datetime import datetime
from django.db.models import Q, F, Count, Case, When, Value, IntegerField
from apps.logistics_all.logistics_all_app.models import DistrictWiseMonthlyAggregate, MonthlyProvider, ProviderMonthlyAggregation
import pandas as pd
from datetime import datetime, timedelta
from django.db.models import Q, Count, Case, When, IntegerField, Sum
from django.db.models import Q, Count, Case, When, IntegerField, Value

import pandas as pd
import time
import calendar
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SellerMetric(Metric):

    def __init__(self, db_utility):
        self.db_utility = db_utility

    def run(self, start_date, end_date, **kwargs):
        self.top_card_delta(start_date, end_date, **kwargs)
    

    def get_month_conditions(start_date, end_date):
        start_month = start_date.month
        end_month = end_date.month
        start_year = start_date.year
        end_year = end_date.year

        # List of month fields
        month_fields = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

        conditions = Q()
        if start_year == end_year:
            month_conditions = [Q(**{f"{month_fields[m - 1]}__gt": 0}) for m in range(start_month, end_month + 1)]
            conditions &= Q(order_year=start_year) & Q(*month_conditions, _connector=Q.OR)
        else:
            # Conditions for the first year
            first_year_months = [Q(**{f"{month_fields[m - 1]}__gt": 0}) for m in range(start_month, 13)]
            conditions &= Q(order_year=start_year) & Q(*first_year_months, _connector=Q.OR)

            # Conditions for the full years in between
            if end_year > start_year + 1:
                middle_years = Q(order_year__gt=start_year, order_year__lt=end_year)
                conditions |= middle_years

            # Conditions for the last year
            last_year_months = [Q(**{f"{month_fields[m - 1]}__gt": 0}) for m in range(1, end_month + 1)]
            conditions |= Q(order_year=end_year) & Q(*last_year_months, _connector=Q.OR)

        return conditions


    def top_card_delta(self, start_date, end_date, domain_name=None, state=None):
        try:
            start_time = time.time()

            # Convert start_date and end_date to datetime objects
            stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
            edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

            # Function to subtract one month
            def subtract_one_month(date):
                year = date.year
                month = date.month - 1
                if month == 0:
                    month = 12
                    year -= 1
                return date.replace(year=year, month=month, day=1)

            # Calculate the previous period
            prev_start_date = subtract_one_month(stdate_obj)
            prev_end_date = subtract_one_month(edate_obj)

            # Conditions for current and previous periods
            current_conditions = self.get_month_conditions(stdate_obj, edate_obj)
            prev_conditions = self.get_month_conditions(prev_start_date, prev_end_date)

            if state:
                current_conditions &= Q(seller_state__iexact=state)
                prev_conditions &= Q(seller_state__iexact=state)

            current_condition_queryset = ProviderMonthlyAggregation.objects.filter(current_conditions)
            previous_condition_queryset = ProviderMonthlyAggregation.objects.filter(prev_conditions)


            # Active Sellers for current period
            active_sellers_current = (
                current_condition_queryset
                .values('seller_state', 'seller_state_code')
                .annotate(
                    total_active_sellers=Count('provider_key_id', distinct=True)
                )
            )

            # Active Sellers for previous period
            active_sellers_previous = (
                previous_condition_queryset
                .values('seller_state', 'seller_state_code')
                .annotate(
                    total_active_sellers=Count('provider_key_id', distinct=True)
                )
            )

            # Mapping previous data
            prev_data_map = {item['seller_state']: item['total_active_sellers'] for item in active_sellers_previous}

            def calculate_delta(current_value, previous_value):
                if previous_value is None or previous_value == 0:
                    return float('inf') if current_value != 0 else 0
                return (current_value - previous_value) / previous_value * 100

            # Combine current and previous period data for delta calculation
            aggregated_data = []
            for current in active_sellers_current:
                state = current['seller_state']
                previous_active_sellers = prev_data_map.get(state, 0)
                current['delta_active_sellers'] = calculate_delta(current['total_active_sellers'], previous_active_sellers)
                aggregated_data.append(current)

            # Total aggregation for current and previous periods
            total_current = (
                current_condition_queryset
                .aggregate(total_active_sellers=Count('provider_key_id', distinct=True))
            )

            total_previous = (
                previous_condition_queryset
                .aggregate(total_active_sellers=Count('provider_key_id', distinct=True))
            )

            # Provide default values of 0 if None
            total_current_active_sellers = total_current['total_active_sellers'] or 0
            total_previous_active_sellers = total_previous['total_active_sellers'] or 0

            total_data = {
                'seller_state_code': 'TT',
                'seller_state': 'TOTAL',
                'total_active_sellers': total_current_active_sellers,
                'delta_active_sellers': calculate_delta(total_current_active_sellers, total_previous_active_sellers)
            }
            aggregated_data.append(total_data)

            df = pd.DataFrame(aggregated_data)

            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Query execution time: {execution_time} seconds")

            return df

        except Exception as e:
            raise e


    def map_state_data(self, start_date, end_date, domain_name, **kwargs):
        start_time = time.time()

        # Convert start_date and end_date to datetime objects
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')
        # Conditions for current and previous periods
        current_conditions = self.get_month_conditions(stdate_obj, edate_obj)

        # if state:
        #     current_conditions &= Q(seller_state__iexact=state)
        #     prev_conditions &= Q(seller_state__iexact=state)

        # if domain_name:
        #     current_conditions &= Q(domain_name=domain_name)

        aggregated_data = (
            ProviderMonthlyAggregation.objects
            .filter(current_conditions)
            .values('seller_state', 'seller_state_code', 'seller_district')
            .annotate(
                total_active_sellers=Count('provider_key', distinct=True)
            )
        )

        df = pd.DataFrame(list(aggregated_data))

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"*************************Query execution time: {execution_time} seconds")

        return df

    def map_statewise_data(self, start_date, end_date, domain_name, **kwargs):
        start_time = time.time()

        # Convert start_date and end_date to datetime objects
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')


        # Conditions for current and previous periods
        current_conditions = self.get_month_conditions(stdate_obj, edate_obj)

        # if state:
        #     current_conditions &= Q(seller_state__iexact=state)
        #     prev_conditions &= Q(seller_state__iexact=state)

        if domain_name:
            current_conditions &= Q(domain_name=domain_name)

        aggregated_data = (
            ProviderMonthlyAggregation.objects
            .filter(current_conditions)
            .values('seller_state', 'seller_state_code')
            .annotate(
                total_active_sellers=Count('provider_key', distinct=True)
            )
        )

        df = pd.DataFrame(list(aggregated_data))

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"*************************Query execution time: {execution_time} seconds")

        return df


    def top_cumulative_chart(self, start_date, end_date, category=None,
                             sub_category=None, domain_name=None, state=None, group_by_seller_state=False,
                             group_by_seller_district=False):

        start_time = time.time()
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        end_month = edate_obj.month
        start_year = stdate_obj.year
        end_year = edate_obj.year

        month_names = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

        conditions = Q()

        # Create conditions for each relevant month
        if start_year == end_year:
            month_conditions = [Q(**{f"{month_names[m - 1]}": 1}) for m in range(start_month, end_month + 1)]
            conditions &= Q(order_year=start_year) & Q(*month_conditions, _connector=Q.OR)
        else:
            # Conditions for the first year
            first_year_months = [Q(**{f"{month_names[m - 1]}": 1}) for m in range(start_month, 13)]
            conditions &= Q(order_year=start_year) & Q(*first_year_months, _connector=Q.OR)

            # Conditions for the full years in between
            if end_year > start_year + 1:
                middle_years = Q(order_year__gt=start_year, order_year__lt=end_year)
                conditions |= middle_years

            # Conditions for the last year
            last_year_months = [Q(**{f"{month_names[m - 1]}": 1}) for m in range(1, end_month + 1)]
            conditions |= Q(order_year=end_year) & Q(*last_year_months, _connector=Q.OR)

        if state:
            conditions &= Q(seller_state=state)

        aggregated_data = (
            ProviderMonthlyAggregation.objects
            .filter(conditions)
            .annotate(
                order_month=Case(
                    *[When(**{month_names[i - 1]: 1}, then=Value(i)) for i in range(1, 13)],
                    output_field=IntegerField()
                )
            )
            .values('order_year', 'order_month')
            .annotate(total_orders_delivered=Count('provider_key', distinct=True))
            .order_by('order_year', 'order_month')
        )

        df = pd.DataFrame(list(aggregated_data))

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"*************************Query execution time: {execution_time} seconds")

        return df

    # from datetime import datetime
    # from django.db.models import Q, F, Count, Case, When, Value, IntegerField
    # import pandas as pd
    #
    # from datetime import datetime
    # from django.db.models import Q, F, Count, Case, When, Value, IntegerField
    # import pandas as pd

    # from datetime import datetime
    # from django.db.models import Q, F, Count, Case, When, Value, IntegerField
    # import pandas as pd

    from datetime import datetime
    from django.db.models import Q, F, Count, Case, When, Value, IntegerField
    import pandas as pd
    import time

    def top_states_chart(self, start_date, end_date, category=None, sub_category=None, domain_name=None, state=None):
        start_time = time.time()
        base_table = os.getenv('MONTHLY_PROVIDERS_TBL')
        if domain_name == 'Logistics':
            base_table = os.getenv('LOGISTICS_MONTHLY_PROVIDERS_TBL')

        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        end_month = edate_obj.month
        start_year = stdate_obj.year
        end_year = edate_obj.year

        # Define the month names in the table
        month_names = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

        conditions = Q()

        # Create conditions for each relevant month
        if start_year == end_year:
            month_conditions = [Q(**{f"{month_names[m - 1]}__gt": 0}) for m in range(start_month, end_month + 1)]
            conditions &= Q(order_year=start_year) & Q(*month_conditions, _connector=Q.OR)
        else:
            # Conditions for the first year
            first_year_months = [Q(**{f"{month_names[m - 1]}__gt": 0}) for m in range(start_month, 13)]
            conditions &= Q(order_year=start_year) & Q(*first_year_months, _connector=Q.OR)

            # Conditions for the full years in between
            if end_year > start_year + 1:
                middle_years = Q(order_year__gt=start_year, order_year__lt=end_year)
                conditions |= middle_years

            # Conditions for the last year
            last_year_months = [Q(**{f"{month_names[m - 1]}__gt": 0}) for m in range(1, end_month + 1)]
            conditions |= Q(order_year=end_year) & Q(*last_year_months, _connector=Q.OR)

        if state:
            conditions &= Q(seller_state__iexact=state)

        # Query for StateSellerCounts
        state_seller_counts = (
            ProviderMonthlyAggregation.objects
            .filter(conditions)
            .exclude(seller_state='')
            .annotate(
                annotated_state=Case(
                    When(seller_state='', then=Value('MISSING')),
                    default=F('seller_state')
                ),
                active_sellers_count=Count('provider_key', distinct=True)
            )
            .values('annotated_state')
            .annotate(active_sellers_count=Count('provider_key', distinct=True))
            .order_by('-active_sellers_count')
        )

        # Limit to top 3 states
        ranked_states = state_seller_counts[:3]

        # Convert to DataFrame for easier manipulation
        ranked_states_df = pd.DataFrame(list(ranked_states))

        # If there are no results, return an empty DataFrame
        if ranked_states_df.empty:
            return pd.DataFrame(columns=['order_year', 'order_month', 'state', 'active_sellers_count', 'state_rank'])

        # Create the rank column
        ranked_states_df['state_rank'] = ranked_states_df['active_sellers_count'].rank(method='dense',
                                                                                       ascending=False).astype(int)

        # Convert the DataFrame back to a list of dictionaries
        ranked_states_list = ranked_states_df.to_dict(orient='records')

        final_conditions = conditions & Q(seller_state__in=[state['annotated_state'] for state in ranked_states_list])

        # Main query to get the final aggregated data
        aggregated_data = (
            ProviderMonthlyAggregation.objects
            .filter(final_conditions)
            .annotate(
                order_month=Case(
                    *[When(**{f"{month_names[i - 1]}__gt": 0}, then=Value(i)) for i in range(1, 13)],
                    output_field=IntegerField()
                ),
                annotated_state=Case(
                    When(seller_state='', then=Value('MISSING')),
                    default=F('seller_state')
                )
            )
            .values('order_year', 'order_month', 'annotated_state')
            .annotate(active_sellers_count=Count('provider_key', distinct=True))
            .order_by('order_year', 'order_month')
        )

        aggregated_data_df = pd.DataFrame(list(aggregated_data))

        # Add the state_rank column to the final DataFrame
        final_df = aggregated_data_df.merge(ranked_states_df, how='left', left_on='annotated_state',
                                            right_on='annotated_state')

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"*************************Query execution time: {execution_time} seconds")

        return final_df[['order_year', 'order_month', 'annotated_state', 'active_sellers_count', 'state_rank']]

    def top_states_chart11(self, start_date, end_date, category=None, sub_category=None,
                                          domain_name=None, state=None):
        base_table = os.getenv('MONTHLY_PROVIDERS_TBL')
        if domain_name == 'Logistics':
            base_table = os.getenv('LOGISTICS_MONTHLY_PROVIDERS_TBL')

        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        end_month = edate_obj.month
        start_year = stdate_obj.year
        end_year = edate_obj.year

        parameters = {
            'start_month': start_month,
            'start_year': start_year,
            'end_month': end_month,
            'end_year': end_year
        }

        query = f'''
            WITH StateSellerCounts AS (
                SELECT 
                    COALESCE(seller_state, 'MISSING') AS seller_state,
                    COUNT(DISTINCT TRIM(LOWER(provider_key))) AS active_sellers_count
                FROM 
                    {base_table}
                WHERE
                    (order_year > %(start_year)s OR (order_year = %(start_year)s AND order_month >= %(start_month)s))
                    AND (order_year < %(end_year)s OR (order_year = %(end_year)s AND order_month <= %(end_month)s))
                    AND seller_state <> ''
        '''

        # if domain_name:
        #     query += " AND domain_name = %(domain_name)s"
        #     parameters['domain_name'] = domain_name

        if state:
            query += " AND COALESCE(UPPER(seller_state), 'MISSING') = UPPER(%(state)s)"
            parameters['state'] = state.upper()

        query += f'''
                GROUP BY 
                    seller_state
            ),
            RankedStates AS (
                SELECT
                    seller_state,
                    active_sellers_count,
                    RANK() OVER (ORDER BY active_sellers_count DESC) AS state_rank
                FROM
                    StateSellerCounts
                WHERE active_sellers_count > 0  -- Add any necessary masking logic here
                LIMIT 3
            )
            SELECT 
                om.order_month AS order_month,
                om.order_year AS order_year,
                COALESCE(om.seller_state, 'MISSING') AS state,
                COUNT(DISTINCT TRIM(LOWER(om.provider_key))) AS active_sellers_count,
                rs.state_rank
            FROM 
                {base_table} om
            INNER JOIN 
                RankedStates rs ON COALESCE(om.seller_state, 'MISSING') = rs.seller_state
            WHERE
                (om.order_year > %(start_year)s OR (om.order_year = %(start_year)s AND om.order_month >= %(start_month)s))
                AND (om.order_year < %(end_year)s OR (om.order_year = %(end_year)s AND om.order_month <= %(end_month)s))
        '''

        # if domain_name:
        #     query += " AND om.domain_name = %(domain_name)s"
        #     parameters['domain_name'] = domain_name

        if state:
            query += " AND COALESCE(UPPER(om.seller_state), 'MISSING') = UPPER(%(state)s)"
            parameters['state'] = state.upper()

        query += '''
            GROUP BY 
                om.order_month, om.order_year, om.seller_state, rs.state_rank
            ORDER BY 
                rs.state_rank, om.order_year, om.order_month
        '''

        df = self.db_utility.execute_query(query, parameters)
        return df


    def top_district_chart(self, start_date, end_date, category=None, sub_category=None,
                                            domain_name=None, state=None):
        table_name = constant.MONTHLY_PROVIDERS
        if domain_name == 'Logistics':
            table_name = constant.LOGISTICS_MONTHLY_PROVIDERS
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        end_month = edate_obj.month
        start_year = stdate_obj.year
        end_year = edate_obj.year

        parameters = {
            'start_month': start_month,
            'start_year': start_year,
            'end_month': end_month,
            'end_year': end_year
        }

        query = f"""
            WITH TopDistricts AS (
                SELECT 
                    seller_district,
                    COUNT(DISTINCT TRIM(LOWER(provider_key))) AS active_sellers_count
                FROM 
                    {table_name}
                WHERE
                    (order_year > %(start_year)s OR (order_year = %(start_year)s AND order_month >= %(start_month)s))
                    AND (order_year < %(end_year)s OR (order_year = %(end_year)s AND order_month <= %(end_month)s))
                    AND seller_district <> 'Undefined'
                    AND seller_district IS NOT NULL
        """

        # if domain:
        #     query += " AND domain = %(domain)s"
        #     parameters['domain'] = domain

        if state:
            query += " AND COALESCE(UPPER(seller_state), 'MISSING') = UPPER(%(state)s)"
            parameters['state'] = state.upper()

        query += f"""
                GROUP BY 
                    seller_district
                HAVING COUNT(DISTINCT TRIM(LOWER(provider_key))) > 0  -- Add any necessary masking logic here
                ORDER BY 
                    active_sellers_count DESC
                LIMIT 3
            ),
            FinalResult AS (
                SELECT 
                    om.order_month AS order_month,
                    om.order_year AS order_year,
                    om.seller_district AS seller_district,
                    COUNT(DISTINCT TRIM(LOWER(om.provider_key))) AS active_sellers_count
                FROM 
                    {table_name} om
                INNER JOIN 
                    TopDistricts td ON om.seller_district = td.seller_district
                WHERE
                    (om.order_year > %(start_year)s OR (om.order_year = %(start_year)s AND om.order_month >= %(start_month)s))
                    AND (om.order_year < %(end_year)s OR (om.order_year = %(end_year)s AND om.order_month <= %(end_month)s))
        """

        # if domain:
        #     query += " AND om.domain = %(domain)s"
        #     parameters['domain'] = domain

        if state:
            query += " AND COALESCE(UPPER(om.seller_state), 'MISSING') = UPPER(%(state)s)"
            parameters['state'] = state.upper()

        query += """
                GROUP BY 
                    om.order_month, om.order_year, om.seller_district
                ORDER BY 
                    om.order_year, om.order_month, COUNT(DISTINCT TRIM(LOWER(provider_key))) DESC
            )
            SELECT * FROM FinalResult;
        """


        df = self.db_utility.execute_query(query, parameters)

        return df


    def state_tree_chart(self, start_date, end_date, **kwargs):
        """Matching the functions"""
        pass

    def district_tree_chart(self, start_date, end_date, **kwargs):
        """Matching the functions"""
        pass



















    # def top_cumulative_chartss(self, start_date, end_date, category=None, sub_category=None, domain_name=None, state=None,
    #                          group_by_seller_state=False, group_by_seller_district=False):
    #
    #     start_time = time.time()
    #     month_names = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    #     # Convert start_date and end_date to datetime objects
    #     stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
    #     edate_obj = datetime.strptime(end_date, '%Y-%m-%d')
    #
    #     # Extract month and year
    #     start_month = stdate_obj.month
    #     start_year = stdate_obj.year
    #     end_month = edate_obj.month
    #     end_year = edate_obj.year
    #
    #     # Construct the initial filter
    #     filters = Q()
    #
    #     # Construct conditions based on the month and year ranges
    #     if start_year == end_year:
    #         filters &= Q(order_year=start_year) & Q(
    #             **{f"{month_names[m - 1]}": True for m in range(start_month, end_month + 1)})
    #     else:
    #         filters &= (
    #                 (Q(order_year=start_year) & Q(**{f"{month_names[m - 1]}": True for m in range(start_month, 13)})) |
    #                 (Q(order_year=end_year) & Q(**{f"{month_names[m - 1]}": True for m in range(1, end_month + 1)}))
    #         )
    #
    #         if end_year > start_year + 1:
    #             filters |= Q(order_year__gt=start_year, order_year__lt=end_year)
    #
    #     if state:
    #         filters &= Q(seller_state=state)
    #
    #     # Perform the query
    #     result = (
    #         ProviderMonthlyAggregation.objects
    #         .filter(filters)
    #         .annotate(
    #             order_month=F('order_month'),
    #             order_year=F('order_year'),
    #             month_present=Case(
    #                 When(order_month__in=[start_month, end_month], then=True),
    #                 default=False,
    #                 output_field=BooleanField()
    #             )
    #         )
    #         .values('order_year', 'order_month')
    #         .annotate(total_orders_delivered=Count('provider_key', distinct=True))
    #         .order_by('order_year', 'order_month')
    #     )
    #
    #     # Convert the result to a DataFrame
    #     df = pd.DataFrame(list(result))
    #
    #     end_time = time.time()
    #     execution_time = end_time - start_time
    #     print(f"###################Query execution time: {execution_time} seconds")
    #     return df
    #
    # def top_cumulative_chart_diff(self, start_date, end_date, category=None,
    #                                      sub_category=None, domain_name=None, state=None, group_by_seller_state=False,
    #                        group_by_seller_district=False):
    #
    #     start_time = time.time()
    #     table_name = constant.MONTHLY_PROVIDERS
    #     stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
    #     edate_obj = datetime.strptime(end_date, '%Y-%m-%d')
    #
    #     # Extract month and year
    #     start_month = stdate_obj.month
    #     end_month = edate_obj.month
    #     start_year = stdate_obj.year
    #     end_year = edate_obj.year
    #
    #     month_names = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    #
    #     conditions = []
    #
    #     # Create conditions for each relevant month
    #     if start_year == end_year:
    #         month_conditions = [f"{month_names[m - 1]} = 1" for m in range(start_month, end_month + 1)]
    #         conditions.append(f"(order_year = {start_year} AND ({' OR '.join(month_conditions)}))")
    #     else:
    #         # Conditions for the first year
    #         first_year_months = [f"{month_names[m - 1]} = 1" for m in range(start_month, 13)]
    #         conditions.append(f"(order_year = {start_year} AND ({' OR '.join(first_year_months)}))")
    #
    #         # Conditions for the full years in between
    #         if end_year > start_year + 1:
    #             middle_years = f"(order_year > {start_year} AND order_year < {end_year})"
    #             conditions.append(middle_years)
    #
    #         # Conditions for the last year
    #         last_year_months = [f"{month_names[m - 1]} = 1" for m in range(1, end_month + 1)]
    #         conditions.append(f"(order_year = {end_year} AND ({' OR '.join(last_year_months)}))")
    #
    #     final_query = f"""
    #     SELECT
    #         order_year,
    #         order_month,
    #         COUNT(DISTINCT provider_key) AS total_orders_delivered
    #     FROM (
    #         SELECT
    #             provider_key,
    #             seller_district,
    #             seller_state,
    #             order_year,
    #             unnest(array[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]) as order_month,
    #             unnest(array[jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec]) as month_present
    #         FROM
    #             provider_monthly_aggregation
    #         WHERE
    #             {" OR ".join(conditions)}
    #     ) AS monthly_data
    #     WHERE
    #         month_present = 1
    #     """
    #
    #     if state:
    #         final_query += f" AND seller_state = '{state}'"
    #
    #     final_query += """
    #     GROUP BY order_year, order_month
    #     ORDER BY order_year, order_month
    #     """
    #     df = self.db_utility.execute_query(final_query)
    #
    #     end_time = time.time()
    #     execution_time = end_time - start_time
    #     print(f"*************************Query execution time: {execution_time} seconds")
    #
    #     return pd.DataFrame(df, columns=['order_year', 'order_month', 'total_orders_delivered'])
    # def top_cumulative_chart44(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
    #                          state=None):
    #     start_time = time.time()
    #
    #     # Convert start_date and end_date to datetime objects
    #     stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
    #     edate_obj = datetime.strptime(end_date, '%Y-%m-%d')
    #
    #     # Extract month and year
    #     start_month = stdate_obj.month
    #     start_year = stdate_obj.year
    #     end_month = edate_obj.month
    #     end_year = edate_obj.year
    #
    #     # Construct the initial filter
    #     filters = (
    #             (Q(order_year__gt=start_year) | (Q(order_year=start_year) & Q(order_month__gte=start_month))) &
    #             (Q(order_year__lt=end_year) | (Q(order_year=end_year) & Q(order_month__lte=end_month)))
    #     )
    #
    #     if state:
    #         filters &= Q(delivery_state=state)
    #
    #     # if domain_name:
    #     #     filters &= Q(domain_name=domain_name)
    #
    #     # Perform the query
    #     result = (
    #         MonthlyProvider.objects
    #         .filter(filters)
    #         .values('order_month', 'order_year')
    #         .annotate(total_orders_delivered=Count('provider_key', distinct=True))
    #         .order_by('order_year', 'order_month')
    #     )
    #
    #     # Convert the result to a DataFrame
    #     df = pd.DataFrame(list(result))
    #
    #     end_time = time.time()
    #     execution_time = end_time - start_time
    #     print(f"*************************Query execution time: {execution_time} seconds")
    #     return df
    # def top_cumulative_chart99(self, start_date, end_date, category=None,
    #                                      sub_category=None, domain_name=None, state=None):
    #
    #     start_time = time.time()
    #     table_name = constant.MONTHLY_PROVIDERS
    #     stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
    #     edate_obj = datetime.strptime(end_date, '%Y-%m-%d')
    #
    #     # Extract month and year
    #     start_month = stdate_obj.month
    #     end_month = edate_obj.month
    #     start_year = stdate_obj.year
    #     end_year = edate_obj.year
    #
    #     parameters = {
    #         'start_month': start_month,
    #         'start_year': start_year,
    #         'end_month': end_month,
    #         'end_year': end_year
    #     }
    #
    #     query = f"""
    #         SELECT
    #             order_month,
    #             order_year,
    #             COUNT(DISTINCT TRIM(LOWER(provider_key))) AS total_orders_delivered
    #         FROM
    #             {table_name}
    #         WHERE
    #             (order_year > %(start_year)s OR (order_year = %(start_year)s AND order_month >= %(start_month)s))
    #             AND (order_year < %(end_year)s OR (order_year = %(end_year)s AND order_month <= %(end_month)s))
    #     """
    #
    #     # if domain_name:
    #     #     query += " AND domain_name = %(domain_name)s"
    #     #     parameters['domain_name'] = domain_name
    #
    #     if state:
    #         query += " AND delivery_state = %(state)s"
    #         parameters['state'] = state
    #
    #     query += " GROUP BY order_month, order_year ORDER BY order_year, order_month"
    #
    #     df = self.db_utility.execute_query(query, parameters)
    #
    #     end_time = time.time()
    #     execution_time = end_time - start_time
    #     print(f"*************************Query execution time: {execution_time} seconds")
    #     return df


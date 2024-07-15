__author__ = "Shashank Katyayan"

import asyncio
import logging
import os
from datetime import datetime
from apps.src.database_utils.ClsBaseMetrics import Metric
from apps.utils import constant
import time
from datetime import datetime
from django.db.models import Sum, Count, Q, F
from apps.logistics_all.logistics_all_app.models import DistrictWiseMonthlyAggregate, MonthlyProvider, ProviderMonthlyAggregation
import pandas as pd
from datetime import datetime, timedelta
from django.db.models import Q, Count, Sum, Case, When, Value, IntegerField, CharField
import pandas as pd
import time
import calendar
from datetime import datetime
from django.db.models import Sum, F, Q, Window
from django.db.models.functions import Coalesce, Trim
from django.db.models import Value as V, CharField
from datetime import datetime
from django.db.models import Sum, F, Q, Window
from django.db.models.functions import Coalesce, Trim, RowNumber
from django.db.models import Value as V


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrderMetric(Metric):

    def __init__(self, db_utility):
        self.db_utility = db_utility

    def run(self, start_date, end_date, **kwargs):
        self.top_card_delta(start_date, end_date, **kwargs)

    # import time
    # from datetime import datetime
    # from django.db.models import Sum, Count, Q
    # from .models import DistrictWiseMonthlyAggregate
    # import pandas as pd

    def top_card_delta(self, start_date, end_date, domain_name=None, state=None):
        def calculate_delta(current_value, previous_value):
            if previous_value is None or previous_value == 0:
                return float('inf') if current_value != 0 else 0
            return (current_value - previous_value) / previous_value * 100

        try:
            start_time = time.time()

            # Convert start_date and end_date to datetime objects
            stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
            edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

            # Extract month and year
            start_month = stdate_obj.month
            start_year = stdate_obj.year
            end_month = edate_obj.month
            end_year = edate_obj.year

            # Construct the initial filter for current period
            current_filters = (
                    (Q(order_year__gt=start_year) | (Q(order_year=start_year) & Q(order_month__gte=start_month))) &
                    (Q(order_year__lt=end_year) | (Q(order_year=end_year) & Q(order_month__lte=end_month)))
            )

            if state:
                current_filters &= Q(delivery_state=state)

            if domain_name:
                current_filters &= Q(domain_name=domain_name)

            # Calculate previous period (assuming the previous period is the same duration before the start date)
            previous_start_date = stdate_obj - (edate_obj - stdate_obj)
            previous_end_date = stdate_obj

            previous_start_month = previous_start_date.month
            previous_start_year = previous_start_date.year
            previous_end_month = previous_end_date.month
            previous_end_year = previous_end_date.year

            previous_filters = (
                    (Q(order_year__gt=previous_start_year) | (
                                Q(order_year=previous_start_year) & Q(order_month__gte=previous_start_month))) &
                    (Q(order_year__lt=previous_end_year) | (
                                Q(order_year=previous_end_year) & Q(order_month__lte=previous_end_month)))
            )

            if state:
                previous_filters &= Q(delivery_state=state)

            if domain_name:
                previous_filters &= Q(domain_name=domain_name)

            # Aggregated data for the current period
            current_data = (
                DistrictWiseMonthlyAggregate.objects
                .filter(current_filters & Q(delivery_state__isnull=False) & ~Q(delivery_state=''))
                .values('delivery_state', 'delivery_state_code')
                .annotate(
                    total_districts=Count('delivery_district', distinct=True),
                    delivered_orders=Sum('total_orders_delivered')
                )
            )

            # Aggregated data for the previous period
            previous_data = (
                DistrictWiseMonthlyAggregate.objects
                .filter(previous_filters & Q(delivery_state__isnull=False) & ~Q(delivery_state=''))
                .values('delivery_state', 'delivery_state_code')
                .annotate(
                    total_districts=Count('delivery_district', distinct=True),
                    delivered_orders=Sum('total_orders_delivered')
                )
            )

            # Calculate the deltas
            current_data_dict = {item['delivery_state']: item for item in current_data}
            previous_data_dict = {item['delivery_state']: item for item in previous_data}

            delta_data = []
            for state in current_data_dict.keys():
                current = current_data_dict.get(state, {'total_districts': 0, 'delivered_orders': 0})
                previous = previous_data_dict.get(state, {'total_districts': 0, 'delivered_orders': 0})

                delta_data.append({
                    'delivery_state': state,
                    'delivery_state_code': current.get('delivery_state_code'),
                    'total_districts': current.get('total_districts', 0),
                    'delivered_orders': current.get('delivered_orders', 0),
                    'delta_districts': calculate_delta(current.get('total_districts', 0), previous.get('total_districts', 0)),
                    'delta_delivered_orders': calculate_delta(current.get('delivered_orders', 0), previous.get('delivered_orders', 0)),
                    'most_ordering_district': 'N/A'  # Placeholder, will be updated later
                })

            # Calculate most ordering district
            most_ordering_districts = (
                DistrictWiseMonthlyAggregate.objects
                .filter(current_filters & Q(delivery_state__isnull=False) & ~Q(delivery_state=''))
                .values('delivery_state', 'delivery_district')
                .annotate(total_orders=Sum('total_orders_delivered'))
                .order_by('delivery_state', '-total_orders')
            )

            # Combine the results for most ordering district
            most_ordering_district_map = {}
            for record in most_ordering_districts:
                state = record['delivery_state']
                if state not in most_ordering_district_map:
                    most_ordering_district_map[state] = record['delivery_district']

            # Update the most_ordering_district in delta_data
            for data in delta_data:
                data['most_ordering_district'] = most_ordering_district_map.get(data['delivery_state'], 'N/A')

            # Total Aggregation for current period
            current_data_total = (
                DistrictWiseMonthlyAggregate.objects
                .filter(current_filters)
                .aggregate(
                    total_districts=Count('delivery_district', distinct=True),
                    delivered_orders=Sum('total_orders_delivered')
                )
            )

            # Total Aggregation for previous period
            previous_data_total = (
                DistrictWiseMonthlyAggregate.objects
                .filter(previous_filters)
                .aggregate(
                    total_districts=Count('delivery_state', distinct=True),
                    delivered_orders=Sum('total_orders_delivered')
                )
            )

            # Calculate the most ordering state for the total aggregation
            most_ordering_state = (
                DistrictWiseMonthlyAggregate.objects
                .filter(current_filters & Q(delivery_state__isnull=False) & ~Q(delivery_state=''))
                .values('delivery_state')
                .annotate(total_orders=Sum('total_orders_delivered'))
                .order_by('-total_orders')
                .first()
            )

            most_ordering_state_name = most_ordering_state['delivery_state'] if most_ordering_state else 'N/A'


            # Calculate delta for total aggregation and include most ordering state in most_ordering_district
            delta_data.append({
                'delivery_state_code': 'TT',
                'delivery_state': 'TOTAL',
                'total_districts': current_data_total['total_districts'],
                'delivered_orders': current_data_total['delivered_orders'],
                'delta_districts': calculate_delta(current_data_total.get('total_districts',0), previous_data_total.get('total_districts',0)),
                'delta_delivered_orders': calculate_delta(current_data_total.get('delivered_orders',0), previous_data_total.get('delivered_orders',0)),
                'most_ordering_district': most_ordering_state_name  # Using state name for total aggregation
            })

            df = pd.DataFrame(delta_data)

            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Query execution time: {execution_time} seconds")

            return df

        except Exception as e:
            raise

    def top_card_delta_without_delta(self, start_date, end_date, domain_name=None, state=None):
        try:
            start_time = time.time()

            # Convert start_date and end_date to datetime objects
            stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
            edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

            # Extract month and year
            start_month = stdate_obj.month
            start_year = stdate_obj.year
            end_month = edate_obj.month
            end_year = edate_obj.year

            # Construct the initial filter
            filters = (
                    (Q(order_year__gt=start_year) | (Q(order_year=start_year) & Q(order_month__gte=start_month))) &
                    (Q(order_year__lt=end_year) | (Q(order_year=end_year) & Q(order_month__lte=end_month)))
            )

            if state:
                filters &= Q(delivery_state=state)

            if domain_name:
                filters &= Q(domain_name=domain_name)

            # AggregatedData
            aggregated_data = (
                DistrictWiseMonthlyAggregate.objects
                .filter(filters & Q(delivery_state__isnull=False) & ~Q(delivery_state=''))
                .values('delivery_state', 'delivery_state_code')
                .annotate(
                    total_districts=Count('delivery_district', distinct=True),
                    delivered_orders=Sum('total_orders_delivered')
                )
            )

            # Calculate most ordering district
            most_ordering_districts = (
                DistrictWiseMonthlyAggregate.objects
                .filter(filters & Q(delivery_state__isnull=False) & ~Q(delivery_state=''))
                .values('delivery_state', 'delivery_district')
                .annotate(total_orders=Sum('total_orders_delivered'))
                .order_by('delivery_state', '-total_orders')
            )

            # Combine the results for most ordering district
            most_ordering_district_map = {}
            for record in most_ordering_districts:
                state = record['delivery_state']
                if state not in most_ordering_district_map:
                    most_ordering_district_map[state] = record['delivery_district']

            # Update the most_ordering_district in aggregated_data
            for data in aggregated_data:
                data['most_ordering_district'] = most_ordering_district_map.get(data['delivery_state'], 'N/A')

            # AggregatedDataTotal
            aggregated_data_total = (
                DistrictWiseMonthlyAggregate.objects
                .filter(filters)
                .aggregate(
                    total_districts=Count('delivery_state', distinct=True),
                    delivered_orders=Sum('total_orders_delivered')
                )
            )

            # Calculate most ordering state
            most_ordering_state = (
                DistrictWiseMonthlyAggregate.objects
                .filter(filters & Q(delivery_state__isnull=False) & ~Q(delivery_state=''))
                .values('delivery_state')
                .annotate(total_orders=Sum('total_orders_delivered'))
                .order_by('-total_orders')
                .first()
            )

            most_ordering_state_name = most_ordering_state['delivery_state'] if most_ordering_state else 'N/A'

            # Merging the data
            aggregated_data = list(aggregated_data)

            aggregated_data.append({
                'delivery_state_code': 'TT',
                'delivery_state': 'TOTAL',
                'total_districts': aggregated_data_total['total_districts'],
                'delivered_orders': aggregated_data_total['delivered_orders'],
                'most_ordering_district': most_ordering_state_name  # Using state name for total aggregation
            })

            df = pd.DataFrame(aggregated_data)

            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Query execution time: {execution_time} seconds")

            return df

        except Exception as e:
            raise

    def map_state_data(self, start_date, end_date,
                                                  category=None, sub_category=None,
                                                  domain_name=None, state=None):
        # Convert string to datetime object
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        start_year = stdate_obj.year
        end_month = edate_obj.month
        end_year = edate_obj.year

        # Define conditions for filtering based on date range
        date_conditions = (
                Q(order_year__gt=start_year) |
                (Q(order_year=start_year) & Q(order_month__gte=start_month)) &
                (Q(order_year__lt=end_year) |
                 (Q(order_year=end_year) & Q(order_month__lte=end_month)))
        )

        # Additional filters
        if domain_name:
            date_conditions &= Q(domain_name=domain_name)

        if state:
            date_conditions &= Q(delivery_state__iexact=state)

        # Perform the query using Django's ORM
        aggregated_data = (
            DistrictWiseMonthlyAggregate.objects
            .filter(date_conditions)
            .values('delivery_state_code', 'delivery_state', 'delivery_district')
            .annotate(
                total_orders_delivered=Sum('total_orders_delivered'),
                intradistrict_orders=Sum('intradistrict_orders'),
                intrastate_orders=Sum('intrastate_orders')
            )
            .order_by('delivery_state_code', '-total_orders_delivered')
        )

        # Convert the queryset to a DataFrame
        aggregated_df = pd.DataFrame(list(aggregated_data))

        return aggregated_df

    def map_statewise_data(self, start_date, end_date,
                       category=None, sub_category=None,
                       domain_name=None, state=None):
        # Convert string to datetime object
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        start_year = stdate_obj.year
        end_month = edate_obj.month
        end_year = edate_obj.year

        # Define conditions for filtering based on date range
        date_conditions = (
                Q(order_year__gt=start_year) |
                (Q(order_year=start_year) & Q(order_month__gte=start_month)) &
                (Q(order_year__lt=end_year) |
                 (Q(order_year=end_year) & Q(order_month__lte=end_month)))
        )

        # Additional filters
        if domain_name:
            date_conditions &= Q(domain_name=domain_name)

        if state:
            date_conditions &= Q(delivery_state__iexact=state)

        # Perform the query using Django's ORM
        aggregated_data = (
            DistrictWiseMonthlyAggregate.objects
            .filter(date_conditions)
            .values('delivery_state_code', 'delivery_state')
            .annotate(
                total_orders_delivered=Sum('total_orders_delivered'),
                intrastate_orders=Sum('intrastate_orders'),
                intradistrict_orders=Sum('intradistrict_orders')
            )
            .order_by('delivery_state_code', '-total_orders_delivered')
        )

        # Convert the queryset to a DataFrame
        aggregated_df = pd.DataFrame(list(aggregated_data))

        return aggregated_df


    # @log_function_call(ondcLogger)
    def top_district_chart(self, start_date, end_date, category=None,
                           sub_category=None, domain_name=None, state=None):

        start_time = time.time()

        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        start_month = stdate_obj.month
        start_year = stdate_obj.year
        end_month = edate_obj.month
        end_year = edate_obj.year

        # Filter the data within the date range
        filters = (Q(order_year__gt=start_year) |
                   (Q(order_year=start_year) & Q(order_month__gte=start_month)))
        filters &= (Q(order_year__lt=end_year) |
                    (Q(order_year=end_year) & Q(order_month__lte=end_month)))
        filters &= ~Q(delivery_district='') & Q(delivery_district__isnull=False)
        filters &= ~Q(delivery_state='') & Q(delivery_state__isnull=False)

        if domain_name:
            filters &= Q(domain_name=domain_name)

        if state:
            filters &= Q(delivery_state__iexact=state)

        # Aggregate and get top 3 districts by total_orders_delivered
        top_districts = (DistrictWiseMonthlyAggregate.objects
                         .filter(filters)
                         .values('delivery_district')
                         .annotate(total_order_demand=Sum('total_orders_delivered'))
                         .order_by('-total_order_demand')[:3])

        top_district_names = [d['delivery_district'] for d in top_districts]

        # Final result with order_month, order_year, delivery_district, total_orders_delivered
        final_filters = filters & Q(delivery_district__in=top_district_names)

        final_result = (DistrictWiseMonthlyAggregate.objects
                        .filter(final_filters)
                        .values('order_month', 'order_year', 'delivery_district')
                        .annotate(total_orders_delivered=Sum('total_orders_delivered'))
                        .order_by('order_year', 'order_month', 'total_orders_delivered'))

        df = pd.DataFrame(list(final_result))

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Query execution time: {execution_time} seconds")

        return df

    def top_states_chart(self, start_date, end_date, category=None,
                           sub_category=None, domain_name=None, state=None):

        start_time = time.time()

        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        start_month = stdate_obj.month
        start_year = stdate_obj.year
        end_month = edate_obj.month
        end_year = edate_obj.year

        # Filter the data within the date range
        filters = (Q(order_year__gt=start_year) |
                   (Q(order_year=start_year) & Q(order_month__gte=start_month)))
        filters &= (Q(order_year__lt=end_year) |
                    (Q(order_year=end_year) & Q(order_month__lte=end_month)))
        filters &= ~Q(delivery_district='') & Q(delivery_district__isnull=False)
        filters &= ~Q(delivery_state='') & Q(delivery_state__isnull=False)

        if domain_name:
            filters &= Q(domain_name=domain_name)

        if state:
            filters &= Q(delivery_state__iexact=state)

        # Aggregate and get top 3 districts by total_orders_delivered
        top_states = (DistrictWiseMonthlyAggregate.objects
                         .filter(filters)
                         .values('delivery_state')
                         .annotate(total_order_demand=Sum('total_orders_delivered'))
                         .order_by('-total_order_demand')[:3])

        top_state_names = [d['delivery_state'] for d in top_states]

        # Final result with order_month, order_year, delivery_district, total_orders_delivered
        final_filters = filters & Q(delivery_state__in=top_state_names)

        final_result = (DistrictWiseMonthlyAggregate.objects
                        .filter(final_filters)
                        .values('order_month', 'order_year', 'delivery_state')
                        .annotate(total_orders_delivered=Sum('total_orders_delivered'))
                        .order_by('order_year', 'order_month', 'total_orders_delivered'))

        df = pd.DataFrame(list(final_result))

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"*************************Query execution time: {execution_time} seconds")

        return df


    def top_cumulative_chart(self, start_date, end_date, category=None,
                             sub_category=None, domain_name=None, state=None):
        try:
            start_time = time.time()

            stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
            edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

            start_month = stdate_obj.month
            start_year = stdate_obj.year
            end_month = edate_obj.month
            end_year = edate_obj.year

            # Construct the initial filter
            filters = (Q(order_year__gt=start_year) |
                       (Q(order_year=start_year) & Q(order_month__gte=start_month))) & \
                      (Q(order_year__lt=end_year) |
                       (Q(order_year=end_year) & Q(order_month__lte=end_month)))

            if domain_name:
                filters &= Q(domain_name=domain_name)

            if state:
                filters &= Q(delivery_state=state)

            # Get the cumulative data
            cumulative_data = (DistrictWiseMonthlyAggregate.objects
                               .filter(filters)
                               .values('order_month', 'order_year')
                               .annotate(total_orders_delivered=Sum('total_orders_delivered'))
                               .order_by('order_year', 'order_month'))

            df = pd.DataFrame(list(cumulative_data))

            end_time = time.time()
            execution_time = end_time - start_time
            print(f"*************************Query execution time: {execution_time} seconds")

            return df

        except Exception as e:
            raise

    # from datetime import datetime
    # from django.db.models import Q, Sum, F, Window
    # from django.db.models.functions import Coalesce, Trim
    # import pandas as pd

    def state_tree_chart(self, start_month, start_year, end_month, end_year, category=None, sub_category=None,
                         domain_name=None, state=None):
        stdate_obj = datetime(year=start_year, month=start_month, day=1)
        edate_obj = datetime(year=end_year, month=end_month, day=1)

        # Define base filters
        filters = (
                (Q(order_year__gt=start_year) | (Q(order_year=start_year) & Q(order_month__gte=start_month))) &
                (Q(order_year__lt=end_year) | (Q(order_year=end_year) & Q(order_month__lte=end_month)))
        )
        filters &= ~Q(delivery_state='') & Q(delivery_state__isnull=False)

        if domain_name:
            filters &= Q(domain_name=domain_name)

        if state:
            filters &= Q(delivery_state__iexact=state)

        # Subquery to calculate total orders per delivery state within the specified month and year range
        total_orders_subquery = DistrictWiseMonthlyAggregate.objects.filter(
            order_year__gte=start_year,
            order_month__gte=start_month,
            order_year__lte=end_year,
            order_month__lte=end_month,
            delivery_state__isnull=False,
        ).values('delivery_state').annotate(
            total_orders=Sum('total_orders_delivered')
        )

        # Main query to get top 5 seller states per delivery state
        main_query = DistrictWiseMonthlyAggregate.objects.filter(
            filters,
            delivery_state__isnull=False,
        ).annotate(
            seller_state_cleaned=Coalesce(Trim(F('seller_state')), 'Missing')
        ).values(
            'delivery_state', 'seller_state_cleaned'
        ).annotate(
            order_demand=Sum('total_orders_delivered'),
            flow_percentage=(Sum('intrastate_orders') * 100.0) / Subquery(total_orders_subquery.values('total_orders'))
        ).annotate(
            rn=Window(
                expression=RowNumber(),
                partition_by=F('delivery_state'),
                order_by=F('flow_percentage').desc()
            )
        ).filter(
            rn__lte=5  # Fetch top 5 seller states per delivery state
        ).order_by(
            'delivery_state', '-flow_percentage'
        )

        # Convert queryset to list of dictionaries
        data = list(main_query)

        # Optionally, convert to DataFrame if needed
        df = pd.DataFrame(data)

        return df

    def district_tree_chart(self, start_date, end_date, category=None, sub_category=None, domain=None,
                                            state=None, district=None):
        # Convert string to datetime object
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        start_year = stdate_obj.year
        end_month = edate_obj.month
        end_year = edate_obj.year

        # Define base filters
        filters = (
                (Q(order_year__gt=start_year) | (Q(order_year=start_year) & Q(order_month__gte=start_month))) &
                (Q(order_year__lt=end_year) | (Q(order_year=end_year) & Q(order_month__lte=end_month)))
        )

        if state:
            filters &= Q(delivery_state__iexact=state)
        if district:
            filters &= Q(delivery_district__iexact=district)

        # Subquery to calculate total orders per delivery district
        total_orders_subquery = DistrictWiseMonthlyAggregate.objects.filter(
            filters
        ).values('delivery_district').annotate(
            total_orders=Sum('total_orders_delivered')
        )

        # Main query to get top 5 seller districts per delivery district
        main_query = DistrictWiseMonthlyAggregate.objects.filter(
            filters
        ).annotate(
            seller_district_cleaned=Coalesce(Trim(F('seller_district')), V('Missing')),
            total_orders=Sum('total_orders_delivered'),
            order_demand=Sum('total_orders_delivered'),
            flow_percentage=(Sum('total_orders_delivered') * 100.0) / F('total_orders')
        ).values(
            'delivery_district', 'seller_district_cleaned'
        ).annotate(
            rn=Window(
                expression=RowNumber(),
                partition_by=F('delivery_district'),
                order_by=F('order_demand').desc()
            )
        ).filter(
            rn__lte=5
        ).order_by('delivery_district', '-flow_percentage')

        df = pd.DataFrame(list(main_query))
        return df


def aggregate_orders(start_date, end_date, domain_name=None, state=None):
        try:
            start_time = time.time()

            # Convert start_date and end_date to datetime objects
            stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
            edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

            # Extract month and year
            start_month = stdate_obj.month
            start_year = stdate_obj.year
            end_month = edate_obj.month
            end_year = edate_obj.year

            # Construct the initial filter
            filters = (
                              Q(order_year__gt=start_year) |
                              (Q(order_year=start_year) & Q(order_month__gte=start_month))
                      ) & (
                              Q(order_year__lt=end_year) |
                              (Q(order_year=end_year) & Q(order_month__lte=end_month))
                      )

            if domain_name:
                filters &= Q(domain_name=domain_name)

            if state:
                filters &= Q(delivery_state=state)

            # Perform the aggregation
            cumulative_data = (
                DistrictWiseMonthlyAggregate.objects
                .filter(filters)
                .values('order_month', 'order_year')
                .annotate(total_orders_delivered=Sum('total_orders_delivered'))
                .order_by('order_year', 'order_month')
            )

            # Convert the result to a Pandas DataFrame
            df = pd.DataFrame(list(cumulative_data))

            end_time = time.time()
            execution_time = end_time - start_time
            print(f"*************************Query execution time: {execution_time} seconds")

            return df

        except Exception as e:
            raise


from django.shortcuts import render
from django.http import HttpResponse

from django.http import JsonResponse
from rest_framework.views import APIView
from django.db import connection
import pandas as pd
import numpy as np
from decimal import Decimal
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from django.http import HttpRequest
from apps.src.chart_data.supply_chart import fetch_downloadable_data_b2b

from apps.src.database_utils.database_utility import DatabaseUtility
from apps.src.database_utils.data_access_layer import DataAccessLayer
from apps.src.database_utils.data_service_layer import DataService
from apps.src.database_utils.generic_queries import max_date_retail_b2b
import logging

from apps.logging_conf import log_function_call, exceptionAPI, ondcLogger

load_dotenv()

from apps.utils import constant
from django.core.cache import cache


templatePath = 'apps/retail_b2b/web/html/'

db_utility = DatabaseUtility()
data_access_layer = DataAccessLayer(db_utility)
data_service = DataService(data_access_layer)



def fetch_max_min_data():
    db_util = DatabaseUtility(alias='default')
    df = db_util.execute_query(max_date_retail_b2b, return_type='df')
    max_date_data = df['max_date'].iloc[0]
    min_date_data = df['min_date'].iloc[0]

    return min_date_data, max_date_data

try:
    min_date, max_date = fetch_max_min_data()
except Exception as e:
    min_date = ''
    max_date = ''



def fetch_state_list():
    query = f''' select distinct "Statecode" as delivery_state_code_current from {constant.PINCODE_TABLE}'''
    db_util = DatabaseUtility(alias='default')
    df = db_util.execute_query(query, return_type='df')
    return df


class B2BBaseDataAPI(APIView):
    """
    This class handles the base data API.
    """

    def extract_common_params(self, request):
        start_date = request.query_params.get('start_date', None)
        if start_date is None:
            start_date = request.query_params.get('startDate', None)

        end_date = request.query_params.get('end_date', None)
        if end_date is None:
            end_date = request.query_params.get('endDate')

        domain_name = request.query_params.get('domainName', None)
        if domain_name == 'None' or domain_name == 'undefined':
            domain_name = None

        state = request.query_params.get('state', None)
        if state == 'None' or state == 'undefined':
            state = None

        return {
            "start_date": start_date,
            "end_date": end_date,
            "domain_name": domain_name,
            "state": state,
        }

    def get_formatted_data(self, df):

        json_str = df.to_json(orient='records')

        return json_str

    @log_function_call(ondcLogger)
    def calculate_delta_percentage(self, current_value, previous_value):
        if previous_value == 0:
            return str(0)

        return round(((float(current_value) - float(previous_value)) / float(previous_value)) * 100, 2)

    @log_function_call(ondcLogger)
    def map_state_data_format(self, map_state_df: pd.DataFrame):
        map_state_df['delivery_district'] = map_state_df['delivery_district'].fillna('Unknown').str.upper()
        map_state_df['delivery_state_code'] = map_state_df['delivery_state_code'].fillna('Unknown')
        map_state_df['total_orders_delivered'] = map_state_df['total_orders_delivered'].astype(float)
        map_state_df['total_items'] = map_state_df['total_items'].astype(float)
        result = {}

        for state_code in map_state_df['delivery_state_code'].unique():
            state_df = map_state_df[map_state_df['delivery_state_code'] == state_code]
            state_data = result.setdefault(state_code, {'districts': {}, 'total': {}})

            for district in state_df['delivery_district'].unique():
                district_df = state_df[state_df['delivery_district'] == district]

                total_orders_delivered = district_df['total_orders_delivered'].sum()

                total_items = district_df['total_items'].sum()
                avg_items_per_order = total_items / total_orders_delivered if total_orders_delivered else 0

                district_data = {
                    'order_demand': int(total_orders_delivered),
                    'avg_items_per_order': round(avg_items_per_order, 2),
                }

                state_data['districts'][district] = district_data

            state_data['total'] = {
                'order_demand': int(state_df['total_orders_delivered'].sum()),
                'avg_items_per_order': round(state_df['total_items'].sum() / state_df['total_orders_delivered'].sum(),
                                             2) if state_df['total_orders_delivered'].sum() else 0
            }

        nationwide_totals = map_state_df.select_dtypes(include=['number']).sum()

        result['TT'] = {
            'total': {
                'order_demand': int(nationwide_totals['total_orders_delivered']),
                'avg_items_per_order': round(
                    nationwide_totals['total_items'] / nationwide_totals['total_orders_delivered'], 2) if
                nationwide_totals['total_orders_delivered'] else 0
            }
        }
        return result

    @log_function_call(ondcLogger)
    def map_state_data_orders_format(self, map_state_df: pd.DataFrame):
        map_state_df['delivery_district'] = map_state_df['delivery_district'].fillna('Unknown').str.upper()
        map_state_df['delivery_state_code'] = map_state_df['delivery_state_code'].fillna('Unknown')

        result = {}

        for state_code in map_state_df['delivery_state_code'].unique():
            state_df = map_state_df[map_state_df['delivery_state_code'] == state_code]
            state_data = result.setdefault(state_code, {'districts': {}, 'total': {}})

            for district in state_df['delivery_district'].unique():
                district_df = state_df[state_df['delivery_district'] == district]

                total_orders_delivered = district_df['total_orders_delivered'].sum()

                total_items = district_df['total_items'].sum()
                avg_items_per_order = total_items / total_orders_delivered if total_orders_delivered else 0

                district_data = {
                    'order_demand': int(total_orders_delivered),
                    'avg_items_per_order': round(avg_items_per_order, 2)
                }

                state_data['districts'][district] = district_data

            state_data['total'] = {
                'order_demand': int(state_df['total_orders_delivered'].sum()),
                'avg_items_per_order': round(state_df['total_items'].sum() / state_df['total_orders_delivered'].sum(),
                                             2) if state_df['total_orders_delivered'].sum() else 0

            }

        return result

    @log_function_call(ondcLogger)
    def map_state_wise_data_format(self, df):
        result = {
            "cases_time_series": [],
            "statewise": []
        }

        for row in df.itertuples():
            confirmed_orders = float(row.total_orders) if isinstance(row.total_orders, Decimal) else row.total_orders

            state_data = {
                'state': row.delivery_state,
                'statecode': row.delivery_state_code,
                'confirmed_orders': confirmed_orders,
                'order_demand': confirmed_orders,
            }
            result['statewise'].append(state_data)

        return result


def shift_date_months(start_date_str, end_date_str, months=-1):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    new_start_date = start_date + relativedelta(months=months)
    new_end_date = end_date + relativedelta(months=months)
    return new_start_date.strftime("%Y-%m-%d"), new_end_date.strftime("%Y-%m-%d")


def calculate_percentage_change(current, previous):
    if previous == 0:
        return "Infinity" if current != 0 else 0
    return round(((current - previous) / previous) * 100, 2)


class FetchCategoryList(APIView):
    """
    API view for fetching the maximum date.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request: HttpRequest, *args, **kwargs):
        """
        APIView FetchCategoryList
        """
        df = {'category': ['ALL'], 'sub_category': ['ALL']}
        return JsonResponse(df)


class FetchMaxDate(APIView):
    """
    API view for fetching the maximum date.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request: HttpRequest, *args, **kwargs):
        """
        APIView FetchMaxDate
        """
        df = self.fetch_data()
        max_date = df['max_date'].iloc[0]
        min_date = df['min_date'].iloc[0]
        json_result = {'min_date': min_date, 'max_date': max_date}
        return JsonResponse(json_result)

    def fetch_data(self):
        db_util = DatabaseUtility(alias='default')
        df = db_util.execute_query(max_date_retail_b2b, return_type='df')
        return df


def safe_divide(a, b, default=1):
    try:
        return np.divide(a, b)
    except Exception as e:
        return default



class FetchTopCardDeltaData(B2BBaseDataAPI):
    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchTopCardDeltaData
        """
        params = self.extract_common_params(request)
        params['domain_name'] = 'Retail'

        try:
            cache_key = self.generate_cache_key(params)
            data = cache.get(cache_key)

            if data is None:
                top_cards_current = self.fetch_current_data(params)
                previous_start_date, previous_end_date = self.get_previous_date_range(params)
                params['start_date'], params['end_date'] = previous_start_date, previous_end_date
                top_cards_previous = self.fetch_previous_data(params)

                merged_data = self.merge_data(top_cards_current, top_cards_previous)
                filtered_merged_df = self.clean_and_prepare_data(merged_data)

                top_cards_data = self.format_response_data(filtered_merged_df, previous_start_date, previous_end_date)
                cache.set(cache_key, top_cards_data, 60 * 60)
            else:
                top_cards_data = data

            return JsonResponse(top_cards_data, safe=False)

        except Exception as e:
            top_cards_data = self.handle_exception(params)
            return JsonResponse(top_cards_data, status=200, safe=False)

    def generate_cache_key(self, params):
        cleaned_list = [params['domain_name'], params['start_date'], params['end_date'], params['state']]
        cleaned_list = [element for element in cleaned_list if element not in [None, 'None']]
        return "FetchTopCardDeltaData_$$$".join(cleaned_list)

    def fetch_current_data(self, params):
        db_utility_top_card = DatabaseUtility()
        data_access_layer_tc = DataAccessLayer(db_utility_top_card)
        data_service_tc = DataService(data_access_layer_tc)
        return data_service_tc.get_total_orders_b2b(**params)

    def get_previous_date_range(self, params):
        original_start_date = params['start_date']
        original_end_date = params['end_date']
        previous_start_date, previous_end_date = shift_date_months(original_start_date, original_end_date)

        try:
            previous_st_date = datetime.strptime(previous_start_date, '%Y-%m-%d').date()
            min_date_obj = datetime.strptime(min_date, '%Y-%m-%d').date()
            if previous_st_date < min_date_obj:
                previous_start_date = min_date
                previous_end_date = original_end_date
        except Exception as e:
            print(e)
            previous_start_date, previous_end_date = shift_date_months(original_start_date, original_end_date)

        return previous_start_date, previous_end_date

    def fetch_previous_data(self, params):
        db_utility_top_card = DatabaseUtility()
        data_access_layer_tc = DataAccessLayer(db_utility_top_card)
        data_service_tc = DataService(data_access_layer_tc)
        return data_service_tc.get_total_orders_b2b(**params)

    def merge_data(self, current_data, previous_data):
        current_data['delivery_state'] = current_data['delivery_state'].astype(str)
        previous_data['delivery_state'] = previous_data['delivery_state'].astype(str)

        return pd.merge(
            current_data, previous_data,
            on='delivery_state', suffixes=('_current', '_previous'),
            how='outer', validate="many_to_many"
        )

    def clean_and_prepare_data(self, merged_df):
        merged_df['most_ordering_district_current'] = merged_df['most_ordering_district_current'].fillna(constant.NO_DATA_MSG)
        merged_df['delivery_state_code_current'] = merged_df['delivery_state_code_current'].fillna('TT')
        merged_df['delivery_state'] = merged_df['delivery_state'].fillna('TOTAL')
        merged_df = merged_df.fillna(0)

        merged_df['district_count_delta'] = np.round(
            100 * safe_divide(merged_df['total_districts_current'] - merged_df['total_districts_previous'],
                              merged_df['total_districts_previous']), 2
        )
        merged_df['orders_count_delta'] = np.round(
            100 * safe_divide(merged_df['delivered_orders_current'] - merged_df['delivered_orders_previous'],
                              merged_df['delivered_orders_previous']), 2
        )
        # merged_df['sellers_count_delta'] = np.round(
        #     100 * safe_divide(merged_df['total_active_sellers_current'] - merged_df['total_active_sellers_previous'],
        #                       merged_df['total_active_sellers_previous']), 2
        # )

        merged_df = merged_df.replace([np.inf, -np.inf], 100).replace([np.nan], 0).fillna(0)

        return merged_df.drop(
            ['delivered_orders_previous', 'total_districts_previous',
             'delivery_state_code_previous'], axis=1
        )

    def format_response_data(self, merged_df, previous_start_date, previous_end_date):
        date_format = '%b %d, %Y'
        prev_start_date_str = datetime.strftime(datetime.strptime(previous_start_date, '%Y-%m-%d'), date_format)
        prev_end_date_str = datetime.strftime(datetime.strptime(previous_end_date, '%Y-%m-%d'), date_format)

        top_card_data = {}
        for _, row in merged_df.iterrows():
            state_code = row['delivery_state_code_current']
            if state_code not in top_card_data:
                top_card_data[state_code] = [
                    self.create_metric_data(
                        row['delivered_orders_current'], 'Total Confirmed Orders', row['orders_count_delta'],
                        'Count of Distinct Network Order Id within the selected range. For Filters, The Total Confirmed Orders are within that category/sub_category'
                    ),
                    self.create_metric_data(
                        row['total_districts_current'], 'Total active districts', row['district_count_delta'],
                        'Unique count of Districts where order has been delivered within the date range. Districts are fetched using districts mapping using End pincode'
                    ),
                    self.create_max_orders_delivered_area_data(
                        row['most_ordering_district_current'])
                ]

        return {
            "prev_date_range": f"Vs {prev_start_date_str} - {prev_end_date_str}",
            "top_card_data": top_card_data
        }

    def create_metric_data(self, count, heading, delta, tooltip_text):
        return {
            "type": 'default',
            "count": int(count),
            "heading": heading,
            "tooltipText": tooltip_text,
            "icon": 'trending_up' if delta >= 0 else 'trending_down',
            "positive": bool(delta >= 0),
            "percentageCount": float(delta)
        }

    def create_max_orders_delivered_area_data(self, most_ordering_district):
        return {
            "type": 'max_state',
            "heading": 'Maximum number of orders delivered to',
            "tooltipText": 'Sort the Total Confirmed Orders by State/Districts, basis the date range and other filters selected. It will show top districts within a state if a state map is selected. Districts are mapped using delivery pincode.',
            "mainText": str(most_ordering_district)
        }

    def handle_exception(self, params):
        original_start_date = params['start_date']
        original_end_date = params['end_date']

        previous_start_date, previous_end_date = shift_date_months(original_start_date, original_end_date)
        date_format = '%b %d, %Y'
        prev_start_date_str = datetime.strftime(datetime.strptime(previous_start_date, '%Y-%m-%d'), date_format)
        prev_end_date_str = datetime.strftime(datetime.strptime(previous_end_date, '%Y-%m-%d'), date_format)

        top_card_data = {}
        state_codes = fetch_state_list()
        state_codes.loc[len(state_codes.index)] = ['TT']

        for _, state_data in state_codes.iterrows():
            state_code = state_data.get('delivery_state_code_current', 'TT')
            top_card_data[state_code] = {
                "Total Confirmed Orders": self.create_metric_data(
                    0, 'Total Confirmed Orders', 0,
                    'Count of Distinct Network Order Id within the selected range. For Filters, The Total Confirmed Orders are within that category/sub_category'
                ),
                "Total Active Districts": self.create_metric_data(
                    0, 'Total active districts', 0,
                    'Unique count of Districts where order has been delivered within the date range. Districts are fetched using districts mapping using End pincode'
                ),
                "Total Registered Sellers": self.create_metric_data(
                    0, 'Total registered sellers', 0,
                    'Unique count of combination of (Provider ID + Seller App) where order has been delivered within the date range'
                ),
                "Max Orders Delivered Area": self.create_max_orders_delivered_area_data('No Data to Display')
            }

        return {
            "prev_date_range": f"Vs {prev_start_date_str} - {prev_end_date_str}",
            "top_card_data": top_card_data
        }


class FetchMapStateWiseData(B2BBaseDataAPI):
    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
            B2BBaseDataAPI FetchMapStateWiseData
        """
        try:
            params = self.extract_common_params(request)

            data = data_service.get_cumulative_orders_statewise_b2b(**params)
            formatted_data = self.map_state_wise_data_format(data)
            return JsonResponse(formatted_data, safe=False)

        except Exception as e:
            error_message = {'error': f"An error occurred: {str(e)}"}
            return JsonResponse(error_message, status=200, safe=False)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int64):
            return int(obj)
        return super().default(obj)


class FetchMapStateData(B2BBaseDataAPI):
    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
            B2BBaseDataAPI FetchMapStateData
        """

        params = self.extract_common_params(request)
        data = data_service.get_cumulative_orders_statedata_b2b(**params)
        formatted_data = self.map_state_data_format(data)
        json_data = json.dumps(formatted_data, cls=CustomJSONEncoder)
        return HttpResponse(json_data, content_type='application/json')


class FetchDownloadableData(APIView):

    def convert_decimal_to_float(self, data):
        try:
            if isinstance(data, Decimal):
                return float(data)
            elif isinstance(data, pd.Series):
                return data.apply(self.convert_decimal_to_float).tolist()
            elif isinstance(data, list):
                return [self.convert_decimal_to_float(item) for item in data]
            elif isinstance(data, dict):
                return {key: self.convert_decimal_to_float(value) for key, value in data.items()}
            return data

        except Exception as e:
            raise RuntimeError(f"An error occurred during conversion: {str(e)}")

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
            APIView FetchDownloadableData
        """
        domain_name = request.GET.get('domainName', None)
        if domain_name == 'None':
            domain_name = None
        domain_name = None
        end_date = request.GET.get('endDate', None)
        start_date = request.GET.get('startDate', None)
        tab_name = request.GET.get('tabName', None)
        preview_limit = request.GET.get('previewLimit', None)

        if not start_date or not end_date:
            return JsonResponse(date_error_msg, status=400)

        with connection.cursor() as conn:

            downloadable_data_df = self.convert_decimal_to_float(
                fetch_downloadable_data_b2b(conn, start_date, end_date, domain_name, tab_name))

            if preview_limit:
                downloadable_data_df = downloadable_data_df.head(int(preview_limit))

            if downloadable_data_df is not None:
                for col_name, col_label in constant.download_table_col_reference.items():
                    if col_label in downloadable_data_df:
                        downloadable_data_df[col_label] = downloadable_data_df[col_label].astype(int)
                data_list = downloadable_data_df.to_dict(orient='records')
                json_data = json.dumps(data_list, cls=CustomJSONEncoder)
                return JsonResponse(json_data, safe=False)
            else:
                return JsonResponse({"error": "Failed to fetch downloadable data."}, status=500)


@log_function_call(ondcLogger)
def retailb2b(request):
    include_category = constant.INCLUDE_CATEGORY_FLAG
    if include_category == '1':
        include_category = True
    else:
        include_category = False
    context = {
        'include_category': include_category
    }
    return render(request, templatePath + 'index.html', context)

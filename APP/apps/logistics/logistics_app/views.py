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
from apps.src.chart_data.supply_chart import fetch_downloadable_data_logistics

from apps.src.database_utils.database_utility import DatabaseUtility
from apps.src.database_utils.data_access_layer import DataAccessLayer
from apps.src.database_utils.data_service_layer import DataService
from apps.src.database_utils.generic_queries import max_date_logistics
import logging

from apps.logging_conf import log_function_call, exceptionAPI, ondcLogger

load_dotenv()

from apps.utils import constant



templatePath = 'apps/logistics/web/html/'

db_utility = DatabaseUtility()
data_access_layer = DataAccessLayer(db_utility)
data_service = DataService(data_access_layer)


class LogisticsBaseDataAPI(APIView):
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
    if previous == 0 or previous is None:
        return 100 if current != 0 else 0
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
        df = db_util.execute_query(max_date_logistics, return_type='df')
        return df


class FetchTopCardDeltaData(LogisticsBaseDataAPI):
    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
            LogisticsBaseDataAPI FetchTopCardDeltaData
        """
        try:
            params = self.extract_common_params(request)
            original_start_date = params['start_date']
            original_end_date = params['end_date']

            previous_start_date, previous_end_date = shift_date_months(original_start_date, original_end_date)
            format_str = '%Y-%m-%d'
            date_format = '%b %d, %Y'
            previous_start_date = datetime.strptime(previous_start_date, format_str)
            previous_end_date = datetime.strptime(previous_end_date, format_str)

            prev_start_date_obj = str(datetime.strftime(previous_start_date, date_format))
            prev_end_date_obj = str(datetime.strftime(previous_end_date, date_format))

            total_orders_current, total_items_current = data_service.get_total_orders_logistics(**params)
            total_district_count_current = data_service.get_district_count_logistics(**params)
            max_orders_delivered_to = data_service.get_most_orders_delivered_to_logistics(**params)

            params['start_date'], params['end_date'] = shift_date_months(params['start_date'], params['end_date'])
            total_orders_previous, _ = data_service.get_total_orders_logistics(**params)
            total_district_count_previous = data_service.get_district_count_logistics(**params)

            try:
                avg_items = round(float(total_items_current / total_orders_current), 2)
            except Exception as e:
                avg_items = 0
            delta_data = {
                "prev_date_range": f"{prev_start_date_obj} to {prev_end_date_obj}",
                "cnf_delta": calculate_percentage_change(total_orders_current, total_orders_previous),
                "district_delta": calculate_percentage_change(total_district_count_current,
                                                              total_district_count_previous),
                "total_confirmed_orders": total_orders_current,
                "total_districts": total_district_count_current,
                "max_orders_delivered_area": max_orders_delivered_to,
                "avg_items": round(avg_items, 0)

            }

            return JsonResponse(delta_data, safe=False)

        except Exception as e:
            params = self.extract_common_params(request)
            original_start_date = params['start_date']
            original_end_date = params['end_date']

            previous_start_date, previous_end_date = shift_date_months(original_start_date, original_end_date)
            format_str = '%Y-%m-%d'
            date_format = '%b %d, %Y'
            previous_start_date = datetime.strptime(previous_start_date, format_str)
            previous_end_date = datetime.strptime(previous_end_date, format_str)

            prev_start_date_obj = str(datetime.strftime(previous_start_date, date_format))
            prev_end_date_obj = str(datetime.strftime(previous_end_date, date_format))

            delta_data = {
                "prev_date_range": f"{prev_start_date_obj} to {prev_end_date_obj}",
                "cnf_delta": 0,
                "district_delta": 0,
                "total_confirmed_orders": 0,
                "total_districts": 0,
                "max_orders_delivered_area": 'No Data to Display',
                "avg_items": 0,

            }
            return JsonResponse(delta_data, status=200, safe=False)


class FetchMapStateWiseData(LogisticsBaseDataAPI):
    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
            LogisticsBaseDataAPI FetchMapStateWiseData
        """
        try:
            params = self.extract_common_params(request)

            data = data_service.get_cumulative_orders_statewise_logistics(**params)
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


class FetchMapStateData(LogisticsBaseDataAPI):
    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
            LogisticsBaseDataAPI FetchMapStateData
        """

        params = self.extract_common_params(request)
        data = data_service.get_cumulative_orders_statedata_logistics(**params)
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

        # if not start_date or not end_date:
        #     return JsonResponse(date_error_msg, status=400)

        with connection.cursor() as conn:

            downloadable_data_df = self.convert_decimal_to_float(
                fetch_downloadable_data_logistics(conn, start_date, end_date, domain_name, tab_name))

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
def logistics(request):
    include_category = constant.INCLUDE_CATEGORY_FLAG
    if include_category == '1':
        include_category = True
    else:
        include_category = False
    context = {
        'include_category': include_category
    }
    return render(request, templatePath + 'index.html', context)

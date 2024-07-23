# Django/Python package imports
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
import logging
from rest_framework import status
from django.db import connection
from django.shortcuts import render
import pandas as pd
import json
import numpy as np
import os

from decimal import Decimal
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from datetime import datetime
from dotenv import load_dotenv

from apps.src.chart_data.supply_chart import fetch_state_sellers, fetch_top3_district_sellers, \
    fetch_top3_states_sellers, fetch_downloadable_data, get_max_state_sellers, get_max_district_sellers
from apps.src.database_utils.generic_queries import fetch_max_date_query, fetch_category_list_query, \
    fetch_district_list_query

from apps.src.chart_data.key_data_insights import fetch_max_gain_by_district, \
    fetch_max_gain_by_district_weekwise, \
    fetch_max_gain_by_state, \
    fetch_max_intrastate_gain_by_state, \
    fetch_max_gain_by_subcategory, \
    fetch_sellers_perc_with_orders

from apps.logging_conf import log_function_call, exceptionAPI
from apps.src.database_utils.database_utility import DatabaseUtility
from apps.src.database_utils.data_access_layer_sql import DataAccessLayer
from apps.src.database_utils.data_service_layer import DataService

from apps.utils import decorator


load_dotenv()

db_utility = DatabaseUtility()
data_access_layer = DataAccessLayer(db_utility)
data_service = DataService(data_access_layer)

from apps.utils import constant
from apps.logging_conf import ondcLogger

templatePath = 'apps/dashboard/web/html/'

def fetch_max_min_data():
    db_util = DatabaseUtility(alias='default')
    df = db_util.execute_query(fetch_max_date_query, return_type='df')
    max_date_data = df['max_date'].iloc[0]
    min_date_data = df['min_date'].iloc[0]

    return min_date_data, max_date_data

try:
    min_date, max_date = fetch_max_min_data()
except Exception as e:
    min_date = ''
    max_date = ''


def dashboard(request):
    include_category = constant.INCLUDE_CATEGORY_FLAG
    if include_category == '1':
        include_category = True
    else:
        include_category = False
    context = {
        'include_category': include_category
    }
    return render(request, templatePath + 'index.html', context)


class BaseDataAPI(APIView):
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

        category = request.query_params.get('category', None)
        if category in ('undefined', 'all', 'None', 'All'):
            category = None
        sub_category = request.query_params.get('subCategory', None)
        if sub_category in constant.sub_category_none_values:
            sub_category = None
        domain_name = request.query_params.get('domainName', None)
        if domain_name == 'None' or domain_name == 'Retail':
            domain_name = None
        state = request.query_params.get('state', None)
        if state == 'None' or state == 'undefined' or state == 'null':
            state = None

        return {
            "start_date": start_date,
            "end_date": end_date,
            "category": category,
            "sub_category": sub_category,
            "domain_name": domain_name,
            "state": state
        }

    def get_formatted_data(self, df):
        json_str = df.to_json(orient='records')
        return json_str

    @log_function_call(ondcLogger)
    def top_chart_format(self, df: pd.DataFrame, chart_type):
        if not pd.api.types.is_datetime64_any_dtype(df['order_date']):
            df['order_date'] = pd.to_datetime(df['order_date'])
        df['total_orders_delivered'] = pd.to_numeric(df['total_orders_delivered'], errors='coerce')

        formatted_data = {
            "series": [],
            "categories": df['order_date'].dt.strftime('%d-%b').unique().tolist()
        }
        if chart_type == 'cumulative':
            formatted_data["series"].append({
                "name": "India",
                "data": df['total_orders_delivered'].tolist()
            })
        else:
            for state in df[chart_type].unique():
                if state == '' or state == 'Missing':
                    continue
                state_data = {
                    "name": state,
                    "data": df[df[chart_type] == state]['total_orders_delivered'].tolist()
                }
                formatted_data["series"].append(state_data)

        return formatted_data

    @log_function_call(ondcLogger)
    def top_chart_hyperlocal_format(self, df: pd.DataFrame, chart_type):
        if not pd.api.types.is_datetime64_any_dtype(df['order_date']):
            df['order_date'] = pd.to_datetime(df['order_date'])
        df['intrastate_orders_percentage'] = pd.to_numeric(df['intrastate_orders_percentage'], errors='coerce')
        formatted_data = {
            "series": [],
            "categories": df['order_date'].dt.strftime('%d-%b').unique().tolist()
        }
        for state in df[chart_type].unique():
            if state == '' or state == 'Missing':
                continue
            state_data = {
                "name": state,
                "data": df[df[chart_type] == state]['intrastate_orders_percentage'].tolist()
            }
            formatted_data["series"].append(state_data)
        return formatted_data

    @log_function_call(ondcLogger)
    def sunburst_format(self, category_penetration_df, chart_type):
        sunburst_data = {'total_data': {}}
        for index, row in category_penetration_df.iterrows():
            category = row['category']
            sub_category = row['sub_category']
            order_demand = int(row[chart_type])

            if category not in sunburst_data:
                sunburst_data[category] = {'children': [], 'value': 0}
            if sub_category == 'ALL':
                sunburst_data['total_data'][category] = {'value': order_demand}
            else:
                sunburst_data[category]['children'].append({'name': sub_category, 'value': order_demand})
                sunburst_data[category]['value'] += order_demand

        ids, labels, parents, values, percent = [], [], [], [], []

        total_value = sum(item['value'] for item in sunburst_data['total_data'].values())

        for category, data in sunburst_data.items():
            if category != 'total_data':
                category_id = category
                ids.append(category_id)
                labels.append(category)
                parents.append("")
                values.append(data['value'])
                if total_value != 0:
                    category_percentage = (sunburst_data['total_data'][category]['value'] / total_value) * 100
                else:
                    category_percentage = 0
                percent.append(round(category_percentage, 2))

                for sub_category in data.get('children', []):
                    sub_category_id = f"{category_id}-{sub_category['name']}"
                    ids.append(sub_category_id)
                    labels.append(sub_category['name'])
                    parents.append(category_id)
                    values.append(sub_category['value'])
                    if data['value'] != 0:
                        sub_category_percentage = (sub_category['value'] / data['value']) * 100
                    else:
                        sub_category_percentage = 0
                    percent.append(round(sub_category_percentage, 2))

        return {'ids': ids, 'labels': labels, 'parents': parents, 'values': values, 'percent': percent}

    @log_function_call(ondcLogger)
    def zonal_commerce_format(self, zonal_commerce_df: pd.DataFrame, tree_type: str):
        from_area = 'seller_state'
        if tree_type == 'delivery_district':
            from_area = 'seller_district'
        state_data = {}
        for state in zonal_commerce_df[tree_type].unique():
            state_data = {
                "name": state,
                "children": []
            }
            state_orders = zonal_commerce_df[zonal_commerce_df[tree_type] == state]
            for index, row in state_orders.iterrows():
                seller_state_data = {
                    "name": f"{row[from_area]} ({row['flow_percentage']:.2f} %)",
                    "value": row['order_demand']
                }
                state_data["children"].append(seller_state_data)
        return state_data

    @log_function_call(ondcLogger)
    def get_date_difference(self, start_date: str, end_date: str):
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
        date_difference = (end_date_dt - start_date_dt).days
        if start_date == end_date:
            date_difference += 1
        return date_difference

    @log_function_call(ondcLogger)
    def state_bin_data_format(self, df: pd.DataFrame, chart_type: str, **kwargs):
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        date_difference = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days + 1

        bin_edges = [0, 1000, 5000, 10000, float('inf')]
        bin_label_1 = "< 1,000"
        bin_label_2 = "1,000 - 5,000"
        bin_label_3 = "5,000 - 10,000"
        bin_label_4 = "> 10,000"
        bin_labels = [bin_label_1, bin_label_2, bin_label_3, bin_label_4]

        if chart_type not in df.columns:
            raise ValueError(f"{chart_type} is not a valid column in the DataFrame")

        df['daily_order_demand'] = df[chart_type] / date_difference
        df['bin'] = pd.cut(df['daily_order_demand'], bins=bin_edges, labels=bin_labels, right=False)
        bins = {label: [] for label in bin_labels}

        for label in bin_labels:
            bins[label] = [' ' + state.title() for state in df[df['bin'] ==
                                                               label]['delivery_state'].unique()]

        return bins

    @log_function_call(ondcLogger)
    def calculate_delta_percentage(self, current_value, previous_value):
        if previous_value == 0:
            return str(0)
        return round(((float(current_value) - float(previous_value)) / float(previous_value)) * 100, 2)

    @log_function_call(ondcLogger)
    def map_state_data_format(self, map_state_df: pd.DataFrame):
        map_state_df['delivery_district'] = map_state_df['delivery_district'].fillna('Unknown').str.upper()
        map_state_df['delivery_state_code'] = map_state_df['delivery_state_code'].fillna('Unknown')
        map_state_df['intrastate_orders'] = map_state_df['intrastate_orders'].astype('float')
        map_state_df['intradistrict_orders'] = map_state_df['intradistrict_orders'].astype('float')

        result = {}

        for state_code in map_state_df['delivery_state_code'].unique():
            state_df = map_state_df[map_state_df['delivery_state_code'] == state_code]
            state_data = result.setdefault(state_code, {'districts': {}, 'total': {}})
            for district in state_df['delivery_district'].unique():
                district_df = state_df[state_df['delivery_district'] == district]
                total_orders_delivered = district_df['total_orders_delivered'].sum()
                total_items = district_df['total_items'].sum()
                avg_items_per_order = float(total_items / total_orders_delivered) if total_orders_delivered else 0
                total_active_sellers = district_df['active_sellers_count'].sum()
                total_intradistrict_orders = district_df['intradistrict_orders'].sum()
                intradistrict_percentage = float(float(total_intradistrict_orders) / float(
                    total_orders_delivered)) * 100 if total_orders_delivered else 0
                total_intrastate_orders = district_df['intrastate_orders'].sum()
                intrastate_percentage = float(float(total_intrastate_orders) / float(
                    total_orders_delivered)) * 100 if total_orders_delivered else 0
                district_data = {
                    'order_demand': int(total_orders_delivered),
                    'avg_items_per_order': round(avg_items_per_order, 2),
                    'intradistrict_percentage': round(intradistrict_percentage, 2),
                    'intrastate_percentage': round(intrastate_percentage, 2),
                    'active_sellers': int(total_active_sellers)
                }
                state_data['districts'][district] = district_data

            state_data['total'] = {
                'order_demand': int(state_df['total_orders_delivered'].sum()),
                'avg_items_per_order': round(
                    float(state_df['total_items'].sum() / state_df['total_orders_delivered'].sum()),
                    2) if state_df['total_orders_delivered'].sum() else 0,
                'intradistrict_percentage': round(
                    float(state_df['intradistrict_orders'].sum() / state_df['total_orders_delivered'].sum()) * 100,
                    2) if
                state_df['total_orders_delivered'].sum() else 0,
                'intrastate_percentage': round(
                    float(state_df['intrastate_orders'].sum() / state_df['total_orders_delivered'].sum()) * 100, 2) if
                state_df['total_orders_delivered'].sum() else 0,
                'active_sellers': int(state_df['active_sellers_count'].sum())
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
            active_sellers = float(row.active_sellers_count) if isinstance(row.active_sellers_count,
                                                                           Decimal) else row.active_sellers_count
            intrastate_orders = float(row.intrastate_orders) if row.intrastate_orders else 0
            intradistrict_orders = float(row.intradistrict_orders) if row.intradistrict_orders else 0

            state_data = {
                'state': row.delivery_state,
                'statecode': row.delivery_state_code,
                'confirmed_orders': confirmed_orders,
                'order_demand': confirmed_orders,
                'active_sellers': active_sellers,
                'intrastate_orders_percentage': round((intrastate_orders / confirmed_orders) * 100,
                                                      2) if confirmed_orders else 0,
                'intradistrict_orders_percentage': round((intradistrict_orders / confirmed_orders) * 100,
                                                         2) if confirmed_orders else 0,
            }
            result['statewise'].append(state_data)

        return result


class FetchCategoryList(APIView):
    """
    API view for fetching the category list.
    """
    @exceptionAPI(ondcLogger)
    def get(self, request: HttpRequest, *args, **kwargs):
        """
        APIView FetchCategoryList
        """
        p_d = "FetchCategoryList_$$$"

        data = cache.get(p_d)
        if data is None:
            try:
                category_list_df = self.fetch_data()
                category_list = category_list_df.to_dict(orient='records')
                cache.set(p_d, category_list, 60 * 60)
            except Exception as e:
                print(e)
                return JsonResponse({'error': str(e)}, status=500)
        else:
            category_list = data
        return JsonResponse(category_list, safe=False)

    def fetch_data(self):
        db_util = DatabaseUtility(alias='default')
        df = db_util.execute_query(fetch_category_list_query, return_type='df')
        return df


class FetchDistrictList(APIView):
    """
    API view for fetching the district list.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request: HttpRequest, *args, **kwargs):
        """
        APIView FetchDistrictList
        """
        p_d = "FetchDistrictList_$$$"

        data = cache.get(p_d)
        if data is None:
            try:

                with connection.cursor():
                    district_list_df = self.fetch_data()
                    state_district_mapping = defaultdict(list)
                    for _, row in district_list_df.iterrows():
                        state = row['delivery_state']
                        district = row['delivery_district']
                        state_district_mapping[state].append(district)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

            structured_data = [{'name': state, 'districts': [{'name': district} for district in districts]}
                               for state, districts in state_district_mapping.items()]
            cache.set(p_d, structured_data, 60 * 60)
        else:
            structured_data = data
        return JsonResponse(structured_data, safe=False)

    def fetch_data(self):
        db_util = DatabaseUtility(alias='default')
        df = db_util.execute_query(fetch_district_list_query, return_type='df')
        return df


def fetch_state_list():
    query = f''' select distinct "Statecode" as delivery_state_code_current from {constant.PINCODE_TABLE}'''
    db_util = DatabaseUtility(alias='default')
    df = db_util.execute_query(query, return_type='df')
    return df


''' Max Date '''


class FetchMaxDate(APIView):
    """
    API view for fetching the maximum date.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView FetchMaxDate
        """
        df = self.fetch_data()
        max_date_data = df['max_date'].iloc[0]
        min_date_data = df['min_date'].iloc[0]
        json_result = {'min_date': min_date_data, 'max_date': max_date_data}
        return JsonResponse(json_result)

    def fetch_data(self):
        db_util = DatabaseUtility(alias='default')
        df = db_util.execute_query(fetch_max_date_query, return_type='df')
        return df


class FetchTopStatesOrders(BaseDataAPI):
    """
    API view for fetching the top states orders.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchTopStatesOrders
        """
        params = self.extract_common_params(request)
        data = data_service.get_top_states_orders(**params)
        formatted_data = self.top_chart_format(data, chart_type='delivery_state')
        return JsonResponse(formatted_data, safe=False)


class FetchCumulativeOrders(BaseDataAPI):
    """
    API view for fetching the top states orders.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchCumulativeOrders
        """
        params = self.extract_common_params(request)
        data = data_service.get_cumulative_orders(**params)
        data_rv = data_service.get_cumulative_orders_rv(**params)
        merged_data = pd.merge(data, data_rv, on='order_date', how='outer', suffixes=('', '_rv'),
                               validate="many_to_many")
        merged_data = merged_data.replace([np.nan], 0)
        merged_data['total_orders_delivered'] = (merged_data['total_orders_delivered'] +
                                                 merged_data['total_orders_delivered_rv'])

        if 'order_date_rv' in merged_data:
            merged_data.drop(columns=['order_date_rv'], inplace=False)
        formatted_data = self.top_chart_format(merged_data, chart_type='cumulative')
        return JsonResponse(formatted_data, safe=False)


class FetchCumulativeSellers(BaseDataAPI):
    """
    API view for fetching the top states orders.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchCumulativeSellers
        """
        params = self.extract_common_params(request)
        data = data_service.get_cummulative_sellers(**params)
        formatted_data = self.top_chart_format(data, chart_type='cumulative')
        return JsonResponse(formatted_data, safe=False)


class FetchTopDistrictOrders(BaseDataAPI):
    """
    API view for fetching the top district orders.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchTopDistrictOrders
        """
        params = self.extract_common_params(request)
        data = data_service.get_top_district_orders(**params)
        formatted_data = self.top_chart_format(data, chart_type='delivery_district')
        return JsonResponse(formatted_data, safe=False)


class FetchCategoryPenetrationOrders(BaseDataAPI):
    """
    API view for fetching category penetration orders.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchCategoryPenetrationOrders
        """
        params = self.extract_common_params(request)
        data = data_service.get_category_penetration_orders(**params)
        formatted_data = self.sunburst_format(data, chart_type='order_demand')
        return JsonResponse(formatted_data, safe=False)


class FetchCategoryPenetrationSellers(BaseDataAPI):
    """
    API view for fetching category penetration orders.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchCategoryPenetrationSellers
        """
        params = self.extract_common_params(request)
        data = data_service.get_category_penetration_sellers(**params)
        formatted_data = self.sunburst_format(data, chart_type='active_sellers_count')
        return JsonResponse(formatted_data, safe=False)


class FetchOrdersPerState(BaseDataAPI):
    """
    API view for fetching orders per state.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchOrdersPerState
        """
        params = self.extract_common_params(request)
        data = data_service.get_states_orders(**params)
        formatted_data = self.state_bin_data_format(data, chart_type='total_orders_delivered', **params)
        return JsonResponse(formatted_data, safe=False)


class FetchMaxOrdersAPI(BaseDataAPI):

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchMaxOrdersAPI
        """
        params = self.extract_common_params(request)
        results = []

        state_orders = data_service.get_max_state_orders(**params)
        state_orders = state_orders.rename(columns={'order_demand': 'value'})
        results.append(state_orders)

        district_orders = data_service.get_max_district_orders(**params)
        district_orders = district_orders.rename(columns={'order_count': 'value'})
        results.append(district_orders)

        combined_results = pd.concat(results, ignore_index=True).fillna(0)
        json_response = combined_results.to_dict(orient='records')
        return JsonResponse(json_response, safe=False)


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


def safe_divide(a, b, default=1):
    try:
        return np.divide(a, b)
    except Exception as e:
        return default


class FetchTopCardDeltaData(BaseDataAPI):
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
        return data_service_tc.get_total_orders(**params)

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
        return data_service_tc.get_total_orders_prev(**params)

    def merge_data(self, current_data, previous_data):
        current_data['delivery_state'] = current_data['delivery_state'].astype(str)
        previous_data['delivery_state'] = previous_data['delivery_state'].astype(str)

        return pd.merge(
            current_data, previous_data,
            on='delivery_state', suffixes=('_current', '_previous'),
            how='outer', validate="many_to_many"
        )

    def clean_and_prepare_data(self, merged_df):
        merged_df['most_ordering_district'] = merged_df['most_ordering_district'].fillna(constant.NO_DATA_MSG)
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
        merged_df['sellers_count_delta'] = np.round(
            100 * safe_divide(merged_df['total_active_sellers_current'] - merged_df['total_active_sellers_previous'],
                              merged_df['total_active_sellers_previous']), 2
        )

        merged_df = merged_df.replace([np.inf, -np.inf], 100).replace([np.nan], 0).fillna(0)

        return merged_df.drop(
            ['delivered_orders_previous', 'total_districts_previous', 'total_active_sellers_previous',
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
                    self.create_metric_data(
                        row['total_active_sellers_current'], 'Total registered sellers', row['sellers_count_delta'],
                        'Unique count of combination of (Provider ID + Seller App) where order has been delivered within the date range'
                    ),
                    self.create_max_orders_delivered_area_data(
                        row['most_ordering_district'])
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
            top_card_data[state_code] = [
                self.create_metric_data(
                    0, 'Total Confirmed Orders', 0,
                    'Count of Distinct Network Order Id within the selected range. For Filters, The Total Confirmed Orders are within that category/sub_category'
                ),
                self.create_metric_data(
                    0, 'Total active districts', 0,
                    'Unique count of Districts where order has been delivered within the date range. Districts are fetched using districts mapping using End pincode'
                ),
                self.create_metric_data(
                    0, 'Total registered sellers', 0,
                    'Unique count of combination of (Provider ID + Seller App) where order has been delivered within the date range'
                ),
                self.create_max_orders_delivered_area_data('No Data to Display')
            ]

        return {
            "prev_date_range": f"Vs {prev_start_date_str} - {prev_end_date_str}",
            "top_card_data": top_card_data
        }



class FetchMapStateWiseData(BaseDataAPI):
    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchMapStateWiseData
        """
        try:
            params = self.extract_common_params(request)

            p_d = [params['domain_name'], params['start_date'],
                   params['end_date'], params['category'], params['sub_category'], params['state']]
            cleaned_list = [element for element in p_d if element not in [None, 'None']]

            p_d = "FetchMapStateWiseData_$$$".join(cleaned_list)

            resp_data = cache.get(p_d)
            if resp_data is None:
                data = data_service.get_cumulative_orders_statewise(**params)
                current_sellers = data_service.get_active_sellers(**params)

                current_sellers_renamed = current_sellers.rename(columns={'seller_state_code': 'delivery_state_code',
                                                                          'seller_state': 'delivery_state'})
                current_merged = data.merge(current_sellers_renamed,
                                            on=['delivery_state_code', 'delivery_state'],
                                            how='outer')

                current_merged.fillna(0, inplace=True)

                json_data = self.map_state_wise_data_format(current_merged)

                cache.set(p_d, json_data, 60 * 60)
            else:
                json_data = resp_data
            return JsonResponse(json_data, safe=False)

        except Exception as e:
            error_message = {'error': f"An error occurred: {str(e)}"}
            return JsonResponse(error_message, status=200, safe=False)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int64):
            return int(obj)
        return super().default(obj)


class FetchMapStateData(BaseDataAPI):
    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchMapStateData
        """
        params = self.extract_common_params(request)

        p_d = [params['domain_name'], params['start_date'],
               params['end_date'], params['category'], params['sub_category'], params['state']]
        cleaned_list = [element for element in p_d if element not in [None, 'None']]

        p_d = "FetchMapStateData_$$$".join(cleaned_list)

        resp_data = cache.get(p_d)
        if resp_data is None:

            data = data_service.get_cumulative_orders_statedata(**params)
            active_sellers_data = data_service.get_active_sellers_statedata(**params)

            active_sellers_renamed = active_sellers_data.rename(columns={'seller_state_code': 'delivery_state_code',
                                                                         'seller_state': 'delivery_state',
                                                                         'seller_district': 'delivery_district'})

            merged = data.merge(active_sellers_renamed,
                                on=['delivery_state_code', 'delivery_state', 'delivery_district'],
                                how='outer')

            merged.fillna(0, inplace=True)

            numeric_columns = ['active_sellers_count', 'total_orders_delivered', 'total_items']
            for col in numeric_columns:
                merged[col] = pd.to_numeric(merged[col], errors='coerce')

            formatted_data = self.map_state_data_format(merged)
            json_data = formatted_data

            # cache.set(p_d, json_data, 60 * 60)

        else:
            json_data = resp_data

        return HttpResponse(json_data, content_type='application/json')


class FetchTopStatesHyperlocal(BaseDataAPI):
    """
    API view for fetching the top states orders.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchTopStatesHyperlocal
        """
        params = self.extract_common_params(request)
        data = data_service.get_top_states_hyperlocal_orders(**params)
        formatted_data = self.top_chart_hyperlocal_format(data, chart_type='delivery_state')
        return JsonResponse(formatted_data, safe=False)


class FetchTopDistrictHyperlocal(BaseDataAPI):
    """
    API view for fetching the top states orders.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchTopDistrictHyperlocal
        """
        params = self.extract_common_params(request)
        data = data_service.get_top_district_hyperlocal_orders(**params)
        formatted_data = self.top_chart_hyperlocal_format(data, chart_type='delivery_district')
        return JsonResponse(formatted_data, safe=False)


class FetchTop5SellerStates(BaseDataAPI):
    """
    API view for fetching the top district orders.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchTop5SellerStates
        """
        params = self.extract_common_params(request)
        data = data_service.get_zonal_commerce_top_states(**params)
        formatted_data = self.zonal_commerce_format(data, tree_type='delivery_state')
        return JsonResponse(formatted_data, safe=False)


class FetchTop5SellersDistrict(BaseDataAPI):
    """
    API view for fetching the top district orders.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchTop5SellersDistrict
        """
        params = self.extract_common_params(request)
        district = request.query_params.get('district_name', None)
        if district == 'None' or district == 'undefined':
            district = None
        params['district'] = district
        data = data_service.get_zonal_commerce_top_districts(**params)
        formatted_data = self.zonal_commerce_format(data, tree_type='delivery_district')
        return JsonResponse(formatted_data, safe=False)


''' Key Data Insights - TO DO'''


class FetchKeyInsightsData(APIView):

    @log_function_call(ondcLogger)
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
        APIView FetchKeyInsightsData
        """
        with connection.cursor() as conn:

            max_gain_by_state_df = self.convert_decimal_to_float(fetch_max_gain_by_state(conn))
            max_gain_by_subcategory_df = self.convert_decimal_to_float(fetch_max_gain_by_subcategory(conn))

            max_gain_by_district_df = self.convert_decimal_to_float(fetch_max_gain_by_district(conn))

            max_gain_by_state_weekwise_df = self.convert_decimal_to_float(fetch_max_intrastate_gain_by_state(conn))

            max_gain_by_district_weekwise_df = self.convert_decimal_to_float(fetch_max_gain_by_district_weekwise(conn))

            sellers_perc_with_orders_df = self.convert_decimal_to_float(fetch_sellers_perc_with_orders(conn))

            if not max_gain_by_state_df.empty and not max_gain_by_subcategory_df.empty:
                data = {
                    "seller_card": {
                        "percentage_seller": int(
                            sellers_perc_with_orders_df['percentage_of_providers_meeting_80p'].iloc[0]),
                        "percentage_of_orders": "80",
                        "current_period": max_gain_by_state_df['current_period'].iloc[0],
                    },
                    "state_order_volume": {
                        "delta_volume_max_state": round(max_gain_by_state_df['total_gain_percent'].iloc[0], 0),
                        "state_name": max_gain_by_state_df['delivery_state'].iloc[0],
                        "current_period": max_gain_by_state_df['current_period'].iloc[0],
                        "previous_period": max_gain_by_state_df['prev_period'].iloc[0]
                    },
                    "state_order_volume_weekwise": {
                        "delta_volume_max_state": round(
                            max_gain_by_state_weekwise_df['intrastate_gain_percent'].iloc[0], 0),
                        "state_name": max_gain_by_state_weekwise_df['delivery_state'].iloc[0],
                        "current_period": max_gain_by_state_weekwise_df['current_period'].iloc[0],
                        "previous_period": max_gain_by_state_weekwise_df['prev_period'].iloc[0]
                    },
                    "district_order_volume": {
                        "delta_volume_max_state": round(max_gain_by_district_df['total_gain_percent'].iloc[0], 0),
                        "district_name": max_gain_by_district_df['delivery_district'].iloc[0],
                        "current_period": max_gain_by_district_df['current_period'].iloc[0],
                        "previous_period": max_gain_by_district_df['prev_period'].iloc[0]
                    },
                    "district_order_volume_weekwise": {
                        "delta_volume_max_state": round(
                            max_gain_by_district_weekwise_df['intradistrict_gain_percent'].iloc[
                                0], 0),
                        "district_name": max_gain_by_district_weekwise_df['delivery_district'].iloc[0],
                        "current_period": max_gain_by_district_weekwise_df['current_period'].iloc[0],
                        "previous_period": max_gain_by_district_weekwise_df['prev_period'].iloc[0]
                    },

                    "subcategory_order_volume": {
                        "delta_volume_max_subcat": round(max_gain_by_subcategory_df['gain_percent'].iloc[0], 0),
                        "sub_category": max_gain_by_subcategory_df['sub_category'].iloc[0],
                        "current_period": max_gain_by_subcategory_df['current_period'].iloc[0],
                        "previous_period": max_gain_by_subcategory_df['prev_period'].iloc[0]
                    }
                }
            else:
                data = {
                    "seller_card": {
                        "percentage_seller": 0,
                        "sub_cat_count": 0
                    },
                    "state_order_volume": {
                        "delta_volume_max_state": 0,
                        "state_name": 0
                    },
                    "unique_items": {
                        "unique_item_count": 0,
                        "delta_mtd_unique_items": 0
                    },
                    "highest_order_by_seller": {
                        "order_count": 0,
                        "previous_mtd": 0
                    },
                    "subcategory_order_volume": {
                        "delta_volume_max_subcat": 0,
                        "sub_category": 0
                    }
                }

        return Response(data, status=status.HTTP_200_OK)


class FetchTopStatesSellers(APIView):

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

    @log_function_call(ondcLogger)
    def process_fetch_result(self, result):
        if isinstance(result, pd.DataFrame):
            result_dict = result.to_dict(orient='records')
            return {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in
                    result_dict[0].items()} if result_dict else {}
        return self.convert_decimal_to_float(result)

    @log_function_call(ondcLogger)
    def dataframe_to_dict_of_lists(self, df):
        return {col: self.convert_decimal_to_float(df[col]) for col in df}

    @log_function_call(ondcLogger)
    def get_formatted_data(self, df):
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])

        df['active_sellers_count'] = pd.to_numeric(df['active_sellers_count'], errors='coerce')

        formatted_data = {
            "series": [],
            "categories": df['date'].dt.strftime(constant.chart_date_format).unique().tolist()
        }

        for state in df['state'].unique():
            if state == "MISSING" or state == "":
                continue

            state_specific_df = df[df['state'] == state]
            state_data_series = state_specific_df.groupby(state_specific_df['date'].dt.strftime(constant.chart_date_format))[
                'active_sellers_count'].sum().tolist()

            state_data = {
                "name": state,
                "data": state_data_series
            }
            formatted_data["series"].append(state_data)

        return formatted_data

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView FetchTopStatesSellers
        """

        domain_name = request.GET.get('domainName')
        end_date = request.GET.get('endDate')
        start_date = request.GET.get('startDate')
        category = request.GET.get('category')
        if category in ('undefined', 'all', 'None'):
            category = None
        state = request.GET.get('state')
        if state in ('undefined', 'all', 'None', 'null'):
            state = None
        sub_category = request.GET.get('subCategory')
        if sub_category in constant.sub_category_none_values:
            sub_category = None

        p_d = [domain_name, start_date, end_date, category, sub_category, state]
        cleaned_list = [element for element in p_d if element not in [None, 'None']]

        p_d = "FetchTopStatesSellers_$$$".join(cleaned_list)

        data = cache.get(p_d)
        if data is None:

            with connection.cursor() as conn:

                if state is not None:
                    state = state.upper()
                    top_3_state_sellers_df = fetch_top3_states_sellers(conn, start_date, end_date, category,
                                                                       sub_category, None, state)
                else:
                    top_3_state_sellers_df = fetch_top3_states_sellers(conn, start_date, end_date, category,
                                                                       sub_category, None, None)

                formatted_data = self.get_formatted_data(top_3_state_sellers_df)
                cache.set(p_d, formatted_data, 60 * 60)
        else:
            formatted_data = data
        return JsonResponse(formatted_data, safe=False)


class FetchTopDistrictSellers(APIView):

    def convert_decimal_to_float(self, data):
        if isinstance(data, Decimal):
            return float(data)
        elif isinstance(data, pd.Series):
            return data.apply(self.convert_decimal_to_float).tolist()
        elif isinstance(data, list):
            return [self.convert_decimal_to_float(item) for item in data]
        elif isinstance(data, dict):
            return {key: self.convert_decimal_to_float(value) for key, value in data.items()}
        return data

    def process_fetch_result(self, result):
        if isinstance(result, pd.DataFrame):
            result_dict = result.to_dict(orient='records')
            return {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in
                    result_dict[0].items()} if result_dict else {}
        return self.convert_decimal_to_float(result)

    def dataframe_to_dict_of_lists(self, df):
        return {col: self.convert_decimal_to_float(df[col]) for col in df}

    def get_formatted_data(self, df):
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])

        formatted_data = {
            "series": [],
            "categories": df['date'].dt.strftime('%d-%b').unique().tolist()
        }

        for district in df['district'].unique():
            district_data = {
                "name": district,
                "data": df[df['district'] == district]['active_sellers_count'].tolist()
            }
            formatted_data["series"].append(district_data)

        return formatted_data

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView FetchTopDistrictSellers
        """
        domain_name = request.GET.get('domainName')
        end_date = request.GET.get('endDate')
        start_date = request.GET.get('startDate')
        category = request.GET.get('category')
        if category in ('undefined', 'all', 'None'):
            category = None
        state = request.GET.get('state')
        sub_category = request.GET.get('subCategory')
        if sub_category in constant.sub_category_none_values:
            sub_category = None
        if not start_date or not end_date:
            return JsonResponse({"error": "Start date and end date are required."}, status=400)

        p_d = [domain_name, start_date, end_date, category, sub_category, state]
        cleaned_list = [element for element in p_d if element not in [None, 'None']]

        p_d = "FetchTopDistrictSellers_$$$".join(cleaned_list)

        data = cache.get(p_d)
        if data is None:
            with connection.cursor() as conn:
                if state is not None:
                    state = state.upper()
                    top_3_district_sellers_df = fetch_top3_district_sellers(conn, start_date, end_date, category,
                                                                            sub_category, None, state)
                else:
                    top_3_district_sellers_df = fetch_top3_district_sellers(conn, start_date, end_date, category,
                                                                            sub_category, None, None)
                formatted_data = self.get_formatted_data(top_3_district_sellers_df)

                cache.set(p_d, formatted_data, 60 * 60)
        else:
            formatted_data = data
        return JsonResponse(formatted_data, safe=False)


class FetchMaxSellersAPI(View):

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView FetchMaxSellersAPI
        """
        start_date = request.GET.get('startDate', None)
        end_date = request.GET.get('endDate', None)
        state = request.GET.get('state', None)
        category = request.GET.get('category', None)
        sub_category = request.GET.get('subCategory', None)
        if category in ('undefined', 'all', 'None'):
            category = None
            sub_category = None
        else:
            if sub_category in constant.sub_category_none_values:
                sub_category = None

        if not start_date or not end_date:
            return JsonResponse({"error": "Start date and end date are required."}, status=400)

        with connection.cursor() as conn:
            results = []

            state_orders = get_max_state_sellers(conn, start_date, end_date, state, category, sub_category)
            results.append(state_orders)

            district_orders = get_max_district_sellers(conn, start_date, end_date, state, category, sub_category)
            results.append(district_orders)

            combined_results = pd.concat(results, ignore_index=True)
            json_response = combined_results.to_json(orient='records')
            json_response = json.loads(json_response)

            return JsonResponse(json_response, safe=False)

    def format_max_orders_data(self, data):
        formatted_data = []
        for item in data:
            formatted_data.append({
                'delivery_district': item.get('delivery_district'),
                'category': item.get('consolidated_categories'),
                'sub_category': item.get('sub_category'),
                'date': item.get('created_date'),
                'max_orders': item.get('max_orders')
            })
        return formatted_data


class FetchSellersPerState(APIView):

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView FetchSellersPerState
        """
        domain_name = request.GET.get('domainName')
        end_date = request.GET.get('endDate')
        start_date = request.GET.get('startDate')
        category = request.GET.get('category')
        sub_category = request.GET.get('subCategory')
        if category in ('undefined', 'all', 'None'):
            category = None
            sub_category = None
        else:
            if sub_category in constant.sub_category_none_values:
                sub_category = None

        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')

        date_difference = (end_date_dt - start_date_dt).days

        if start_date == end_date:
            date_difference += 1
        with connection.cursor() as conn:
            state_orders_df = fetch_state_sellers(conn, start_date, end_date, category, sub_category)
            bins = {"< 100": [], "100 - 500": [], "500 - 1,000": [], "> 1,000": []}

            for index, row in state_orders_df.iterrows():
                state = row['seller_state']
                if state is not None:
                    state = state.title()
                    state = ' ' + state
                daily_order_demand = row['active_sellers_count'] / date_difference

                if daily_order_demand < 100:
                    bins["< 100"].append(state)
                elif 100 <= daily_order_demand < 500:
                    bins["100 - 500"].append(state)
                elif 500 <= daily_order_demand < 1000:
                    bins["500 - 1,000"].append(state)
                else:
                    bins["> 1,000"].append(state)

        return JsonResponse(bins, safe=False)


''' Download Data'''


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
            return JsonResponse(constant.date_error_msg, status=400)

        with connection.cursor() as conn:

            downloadable_data_df = self.convert_decimal_to_float(
                fetch_downloadable_data(conn, start_date, end_date, domain_name, tab_name))

            if preview_limit:
                downloadable_data_df = downloadable_data_df.head(int(preview_limit))

            if downloadable_data_df is not None:
                data_list = downloadable_data_df.to_dict(orient='records')

                json_data = json.dumps(data_list, cls=CustomJSONEncoder)
                return JsonResponse(json_data, safe=False)
            else:
                return JsonResponse({"error": "Failed to fetch downloadable data."}, status=500)


@log_function_call(ondcLogger)
def home(request):
    return render(request, 'dashboard/home.html')


@log_function_call(ondcLogger)
def retail_b2b(request):
    include_category = constant.INCLUDE_CATEGORY_FLAG
    if include_category == '1':
        include_category = True
    else:
        include_category = False
    context = {
        'include_category': include_category
    }
    return render(request, 'apps/retail_b2b/web/html/index.html', context)

def custom_404(request, exception):
    return render(request, templatePath + '404.html')

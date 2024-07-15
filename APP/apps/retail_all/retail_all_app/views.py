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
from apps.src.chart_data.supply_chart import fetch_downloadable_data_overall, fetch_overall_top3_states_sellers, fetch_overall_top3_district_sellers
from collections import defaultdict

from apps.src.database_utils.database_utility import DatabaseUtility
from apps.src.database_utils.dal_retail_overall import DataAccessLayer
from apps.src.database_utils.data_service_layer import DataService
from apps.src.database_utils.generic_queries import fetch_max_date_query, max_date_retail_overall, fetch_district_list_query
import logging
import hashlib, hmac

from apps.logging_conf import log_function_call, exceptionAPI, ondcLogger

load_dotenv()

from apps.utils import constant
from django.core.cache import cache
import calendar


templatePath = 'apps/retail_all/web/html/'

db_utility = DatabaseUtility()
data_access_layer = DataAccessLayer(db_utility)
data_service = DataService(data_access_layer)


class SummaryBaseDataAPI(APIView):
    """
    This class handles the base data API.
    """

    def extract_common_params(self, request):
        start_date = request.query_params.get('startDate', None)
        if start_date is None:
            start_date = request.query_params.get('start_date', None)

        end_date = request.query_params.get('endDate', None)
        if end_date is None:
            end_date = request.query_params.get('end_date', None)

        domain_name = request.query_params.get('domainName', None)
        if domain_name == 'None' or domain_name == 'undefined' or domain_name == 'null':
            domain_name = 'Retail'

        state = request.query_params.get('state', None)
        if state == 'None' or state == 'undefined' or state == 'null':
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
    def top_chart_format(self, df: pd.DataFrame, chart_type):
        df['order_date'] = df['order_month'].astype(int).apply(lambda x: f"{x:02}") + '-' + df['order_year'].astype(int).astype(str)
        if not pd.api.types.is_datetime64_any_dtype(df['order_date']):
            df['order_date'] = pd.to_datetime(df['order_date'])
        df['total_orders_delivered'] = pd.to_numeric(df['total_orders_delivered'], errors='coerce')

        formatted_data = {
            "series": [],
            "categories": df['order_date'].dt.strftime('%b-%y').unique().tolist()
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
        df['order_date'] = df['order_month'].astype(int).apply(lambda x: f"{x:02}") + '-' + df['order_year'].astype(int).astype(str)
        if not pd.api.types.is_datetime64_any_dtype(df['order_date']):
            df['order_date'] = pd.to_datetime(df['order_date'])
        df['intrastate_orders_percentage'] = pd.to_numeric(df['intrastate_orders_percentage'], errors='coerce')
        formatted_data = {
            "series": [],
            "categories": df['order_date'].dt.strftime('%b-%y').unique().tolist()
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
            cumulative_percentage = 0.0
            state_orders = zonal_commerce_df[zonal_commerce_df[tree_type] == state]
            for index, row in state_orders.iterrows():
                cumulative_percentage += float(row['flow_percentage'])

                seller_state_data = {
                    "name": f"{row[from_area]} ({row['flow_percentage']:.2f} %)",
                    "value": row['order_demand']
                }
                state_data["children"].append(seller_state_data)

            # Add the "others" entry if cumulative percentage is less than 100%
            if cumulative_percentage < 100.0:
                others_data = {
                    "name": f"Others ({100 - cumulative_percentage:.2f} %)",
                    "value": 100 - cumulative_percentage
                }
                state_data["children"].append(others_data)

            # data.append(state_data)
        return state_data

    @log_function_call(ondcLogger)
    def calculate_delta_percentage(self, current_value, previous_value):
        if previous_value == 0:
            return str(0)

        return round(((float(current_value) - float(previous_value)) / float(previous_value)) * 100, 2)

    # @log_function_call(ondcLogger)
    # def map_state_data_format(self, map_state_df: pd.DataFrame):
    #     map_state_df['delivery_district'] = map_state_df['delivery_district'].fillna('Unknown').str.upper()
    #     map_state_df['delivery_state_code'] = map_state_df['delivery_state_code'].fillna('Unknown')
    #     map_state_df['total_orders_delivered'] = map_state_df['total_orders_delivered'].astype(float)
    #     # map_state_df['total_items'] = map_state_df['total_items'].astype(float)
    #     result = {}
    #
    #     for state_code in map_state_df['delivery_state_code'].unique():
    #         state_df = map_state_df[map_state_df['delivery_state_code'] == state_code]
    #         state_data = result.setdefault(state_code, {'districts': {}, 'total': {}})
    #
    #         for district in state_df['delivery_district'].unique():
    #             district_df = state_df[state_df['delivery_district'] == district]
    #
    #             total_orders_delivered = district_df['total_orders_delivered'].sum()
    #
    #             # total_items = district_df['total_items'].sum()
    #             # avg_items_per_order = total_items / total_orders_delivered if total_orders_delivered else 0
    #
    #             district_data = {
    #                 'order_demand': int(total_orders_delivered),
    #                 # 'avg_items_per_order': round(avg_items_per_order, 2),
    #             }
    #
    #             state_data['districts'][district] = district_data
    #
    #         state_data['total'] = {
    #             'order_demand': int(state_df['total_orders_delivered'].sum()),
    #             # 'avg_items_per_order': round(state_df['total_items'].sum() / state_df['total_orders_delivered'].sum(),
    #             #                              2) if state_df['total_orders_delivered'].sum() else 0
    #         }
    #
    #     nationwide_totals = map_state_df.select_dtypes(include=['number']).sum()
    #
    #     result['TT'] = {
    #         'total': {
    #             'order_demand': int(nationwide_totals['total_orders_delivered']),
    #             # 'avg_items_per_order': round(
    #             #     nationwide_totals['total_items'] / nationwide_totals['total_orders_delivered'], 2) if
    #             # nationwide_totals['total_orders_delivered'] else 0
    #         }
    #     }
    #     return result

    # @log_function_call(ondcLogger)
    # def map_state_data_orders_format(self, map_state_df: pd.DataFrame):
    #     map_state_df['delivery_district'] = map_state_df['delivery_district'].fillna('Unknown').str.upper()
    #     map_state_df['delivery_state_code'] = map_state_df['delivery_state_code'].fillna('Unknown')
    #
    #     result = {}
    #
    #     for state_code in map_state_df['delivery_state_code'].unique():
    #         state_df = map_state_df[map_state_df['delivery_state_code'] == state_code]
    #         state_data = result.setdefault(state_code, {'districts': {}, 'total': {}})
    #
    #         for district in state_df['delivery_district'].unique():
    #             district_df = state_df[state_df['delivery_district'] == district]
    #
    #             total_orders_delivered = district_df['total_orders_delivered'].sum()
    #
    #             total_items = district_df['total_items'].sum()
    #             avg_items_per_order = total_items / total_orders_delivered if total_orders_delivered else 0
    #
    #             district_data = {
    #                 'order_demand': int(total_orders_delivered),
    #                 'avg_items_per_order': round(avg_items_per_order, 2)
    #             }
    #
    #             state_data['districts'][district] = district_data
    #
    #         state_data['total'] = {
    #             'order_demand': int(state_df['total_orders_delivered'].sum()),
    #             'avg_items_per_order': round(state_df['total_items'].sum() / state_df['total_orders_delivered'].sum(),
    #                                          2) if state_df['total_orders_delivered'].sum() else 0
    #
    #         }
    #
    #     return result

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
                total_active_sellers = district_df['active_sellers_count'].sum()
                total_intradistrict_orders = district_df['intradistrict_orders'].sum()
                intradistrict_percentage = float(float(total_intradistrict_orders) / float(
                    total_orders_delivered)) * 100 if total_orders_delivered else 0
                total_intrastate_orders = district_df['intrastate_orders'].sum()
                intrastate_percentage = float(float(total_intrastate_orders) / float(
                    total_orders_delivered)) * 100 if total_orders_delivered else 0
                district_data = {
                    'order_demand': int(total_orders_delivered),
                    'intradistrict_percentage': round(intradistrict_percentage, 2),
                    'intrastate_percentage': round(intrastate_percentage, 2),
                    'active_sellers': int(total_active_sellers)
                }
                state_data['districts'][district] = district_data

            state_data['total'] = {
                'order_demand': int(state_df['total_orders_delivered'].sum()),
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
            if row.delivery_state_code != 0:
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
            with connection.cursor():
                district_list_df = self.fetch_data()
                state_district_mapping = defaultdict(list)
                for _, row in district_list_df.iterrows():
                    state = row['delivery_state']
                    district = row['delivery_district']
                    state_district_mapping[state].append(district)

            structured_data = { state: [district for district in districts]
                               for state, districts in state_district_mapping.items()}
            cache.set(p_d, structured_data, 60 * 60)
        else:
            structured_data = data
        return JsonResponse(structured_data, safe=False)

    def fetch_data(self):
        db_util = DatabaseUtility(alias='default')
        df = db_util.execute_query(fetch_district_list_query, return_type='df')
        return df


def shift_date_months(start_date_str, end_date_str, months=-1):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    new_start_date = start_date + relativedelta(months=months)
    new_end_date = end_date + relativedelta(months=months)
    return new_start_date.strftime("%Y-%m-%d"), new_end_date.strftime("%Y-%m-%d")



def calculate_percentage_change(current, previous):
    if previous == 0:
        return 100 if current != 0 else 0
    return round(((current - previous) / previous) * 100, 2)


def fetch_state_list():
    query = f''' select distinct "Statecode" as delivery_state_code_current from {constant.PINCODE_TABLE}'''
    db_util = DatabaseUtility(alias='default')
    df = db_util.execute_query(query, return_type='df')
    return df


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
        # Extract the minimum and maximum year_month values
        min_year_month = df['min_year_month'].iloc[0]
        max_year_month = df['max_year_month'].iloc[0]

        # Convert these values to year and month
        min_year = min_year_month // 100
        min_month = min_year_month % 100

        max_year = max_year_month // 100
        max_month = max_year_month % 100

        # Construct min_date as the first day of the min year/month
        min_date = f"{min_year}-{min_month:02d}-01"

        # Calculate the last day of the max month
        last_day = calendar.monthrange(max_year, max_month)[1]
        max_date = f"{max_year}-{max_month:02d}-{last_day:02d}"

        # Optionally convert to datetime objects
        min_date_dt = pd.to_datetime(min_date)
        max_date_dt = pd.to_datetime(max_date)

        # Create the JSON result
        json_result = {
            'min_date': min_date_dt.strftime('%Y-%m-%d'),
            'max_date': max_date_dt.strftime('%Y-%m-%d')
        }
        return JsonResponse(json_result)

    def fetch_data(self):
        db_util = DatabaseUtility(alias='default')
        df = db_util.execute_query(max_date_retail_overall, return_type='df')
        return df

def safe_divide(a, b, default=1):
    try:
        return np.divide(a, b)
    except Exception as e:
        return default

def fetch_max_min_data():
    db_util = DatabaseUtility(alias='default')
    df = db_util.execute_query(max_date_retail_overall, return_type='df')
    # Extract the minimum and maximum year_month values
    min_year_month = df['min_year_month'].iloc[0]
    max_year_month = df['max_year_month'].iloc[0]

    # Convert these values to year and month
    min_year = min_year_month // 100
    min_month = min_year_month % 100

    max_year = max_year_month // 100
    max_month = max_year_month % 100

    # Construct min_date as the first day of the min year/month
    min_date = f"{min_year}-{min_month:02d}-01"

    # Calculate the last day of the max month
    last_day = calendar.monthrange(max_year, max_month)[1]
    max_date = f"{max_year}-{max_month:02d}-{last_day:02d}"

    # Optionally convert to datetime objects
    min_date_dt = pd.to_datetime(min_date)
    max_date_dt = pd.to_datetime(max_date)

    min_date= min_date_dt.strftime('%Y-%m-%d')
    max_date= max_date_dt.strftime('%Y-%m-%d')


    return min_date, max_date

try:
    min_date, max_date = fetch_max_min_data()
except Exception as e:
    min_date = ''
    max_date = ''

import os


class FetchTopCardDeltaData(SummaryBaseDataAPI):
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
        return data_service_tc.get_total_orders_summary(**params)

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
        return data_service_tc.get_total_orders_summary_prev(**params)

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
        date_format = '%b, %Y'
        prev_start_date_str = datetime.strftime(datetime.strptime(previous_start_date, '%Y-%m-%d'), date_format)
        prev_end_date_str = datetime.strftime(datetime.strptime(previous_end_date, '%Y-%m-%d'), date_format)

        top_card_data = {}
        for _, row in merged_df.iterrows():
            state_code = row['delivery_state_code_current']
            if state_code not in top_card_data:
                top_card_data[state_code] = [
                    self.create_metric_data(
                        row['delivered_orders_current'], 'Total Orders', row['orders_count_delta'],
                        'Count of Distinct Network Order Id within the selected range.'
                    ),
                    self.create_metric_data(
                        row['total_districts_current'], 'Districts', row['district_count_delta'],
                        'Unique count of Districts where orders has been delivered within the date range. Districts are fetched using districts mapping using End pincode'
                    ),
                    self.create_metric_data(
                        row['total_active_sellers_current'], 'Registered sellers', row['sellers_count_delta'],
                        'Unique count of combination of (Provider ID + Seller App) within the date range'
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
            "heading": 'records the highest order count',
            "tooltipText": 'Maximum Orders by State/Districts, basis the date range. It will show top districts within a state if a state map is selected. Districts are mapped using delivery pincode.',
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
                    0, 'Total Orders', 0,
                    'Count of Distinct Network Order Id within the selected range. For Filters, The Total Confirmed Orders are within that category/sub_category'
                ),
                self.create_metric_data(
                    0, 'Districts', 0,
                    'Unique count of Districts where order has been delivered within the date range. Districts are fetched using districts mapping using End pincode'
                ),
                self.create_metric_data(
                    0, 'Registered sellers', 0,
                    'Unique count of combination of (Provider ID + Seller App) where order has been delivered within the date range'
                ),
                self.create_max_orders_delivered_area_data('No Data to Display')
            ]

        return {
            "prev_date_range": f"Vs {prev_start_date_str} - {prev_end_date_str}",
            "top_card_data": top_card_data
        }


class FetchMapStateWiseData(SummaryBaseDataAPI):
    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchMapStateWiseData
        """
        # try:
        params = self.extract_common_params(request)

        p_d = [params['domain_name'], params['start_date'],
               params['end_date'], params['state']]
        cleaned_list = [element for element in p_d if element not in [None, 'None']]

        p_d = "FetchMapStateWiseData_$$$".join(cleaned_list)

        resp_data = cache.get(p_d)
        if resp_data is None:
            data = data_service.get_cumulative_orders_statewise_summary(**params)
            current_sellers = data_service.get_overall_active_sellers(**params)

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

        # except Exception as e:
        #     error_message = {'error': f"An error occurred: {str(e)}"}
        #     return JsonResponse(error_message, status=200, safe=False)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int64):
            return int(obj)
        return super().default(obj)


class FetchMapStateData(SummaryBaseDataAPI):
    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchMapStateData
        """
        params = self.extract_common_params(request)

        p_d = [params['domain_name'], params['start_date'],
               params['end_date'], params['state']]
        cleaned_list = [element for element in p_d if element not in [None, 'None']]

        p_d = "FetchMapStateData_$$$".join(cleaned_list)

        resp_data = cache.get(p_d)
        if resp_data is None:

            data = data_service.get_cumulative_orders_statedata_summary(**params)
            active_sellers_data = data_service.get_overall_active_sellers_statedata(**params)

            active_sellers_renamed = active_sellers_data.rename(columns={'seller_state_code': 'delivery_state_code',
                                                                         'seller_state': 'delivery_state',
                                                                         'seller_district': 'delivery_district'})

            merged = data.merge(active_sellers_renamed,
                                on=['delivery_state_code', 'delivery_state', 'delivery_district'],
                                how='outer')

            merged.fillna(0, inplace=True)

            numeric_columns = ['active_sellers_count', 'total_orders_delivered']
            for col in numeric_columns:
                merged[col] = pd.to_numeric(merged[col], errors='coerce')

            formatted_data = self.map_state_data_format(merged)
            # json_data = json.dumps(formatted_data, cls=CustomJSONEncoder)
            json_data = formatted_data

            cache.set(p_d, json_data, 60 * 60)

        else:
            json_data = resp_data
        return JsonResponse(json_data, safe=False)


class FetchTopStatesOrders(SummaryBaseDataAPI):
    """
    API view for fetching the top states orders.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchTopStatesOrders
        """
        params = self.extract_common_params(request)
        data = data_service.get_retail_overall_top_states_orders(**params)
        formatted_data = self.top_chart_format(data, chart_type='delivery_state')
        return JsonResponse(formatted_data, safe=False)

class FetchCumulativeOrders(SummaryBaseDataAPI):
    """
    API view for fetching the top states orders.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchCumulativeOrders
        """
        params = self.extract_common_params(request)
        data = data_service.get_retail_overall_orders(**params)
        merged_data = data.replace([np.nan], 0)
        # merged_data['total_orders_delivered'] = (merged_data['total_orders_delivered'] +
        #                                          merged_data['total_orders_delivered_rv'])

        formatted_data = self.top_chart_format(merged_data, chart_type='cumulative')
        return JsonResponse(formatted_data, safe=False)


class FetchCumulativeSellers(SummaryBaseDataAPI):
    """
    API view for fetching the top states orders.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchCumulativeSellers
        """
        params = self.extract_common_params(request)
        data = data_service.get_overall_cumulative_sellers(**params)
        formatted_data = self.top_chart_format(data, chart_type='cumulative')
        return JsonResponse(formatted_data, safe=False)


class FetchTopDistrictOrders(SummaryBaseDataAPI):
    """
    API view for fetching the top district orders.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchTopDistrictOrders
        """
        params = self.extract_common_params(request)
        data = data_service.get_overall_top_district_orders(**params)
        formatted_data = self.top_chart_format(data, chart_type='delivery_district')
        return JsonResponse(formatted_data, safe=False)

class FetchTopStatesHyperlocal(SummaryBaseDataAPI):
    """
    API view for fetching the top states orders.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchTopStatesHyperlocal
        """
        params = self.extract_common_params(request)
        data = data_service.get_overall_top_states_hyperlocal_orders(**params)
        formatted_data = self.top_chart_hyperlocal_format(data, chart_type='delivery_state')
        return JsonResponse(formatted_data, safe=False)


class FetchTopDistrictHyperlocal(SummaryBaseDataAPI):
    """
    API view for fetching the top states orders.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchTopDistrictHyperlocal
        """
        params = self.extract_common_params(request)
        data = data_service.get_overall_top_district_hyperlocal_orders(**params)
        formatted_data = self.top_chart_hyperlocal_format(data, chart_type='delivery_district')
        return JsonResponse(formatted_data, safe=False)



class FetchTop5SellerStates(SummaryBaseDataAPI):
    """
    API view for fetching the top district orders.
    """

    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchTop5SellerStates
        """
        params = self.extract_common_params(request)
        data = data_service.get_overall_zonal_commerce_top_states(**params)
        formatted_data = self.zonal_commerce_format(data, tree_type='delivery_state')
        return JsonResponse(formatted_data, safe=False)


class FetchTop5SellersDistrict(SummaryBaseDataAPI):
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
        data = data_service.get_overall_zonal_commerce_top_districts(**params)
        formatted_data = self.zonal_commerce_format(data, tree_type='delivery_district')
        return JsonResponse(formatted_data, safe=False)


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
        df['date'] = df['order_month'].astype(int).apply(lambda x: f"{x:02}") + '-' + df['order_year'].astype(int).astype(str)

        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])

        df['active_sellers_count'] = pd.to_numeric(df['active_sellers_count'], errors='coerce')

        formatted_data = {
            "series": [],
            "categories": df['date'].dt.strftime('%b-%y').unique().tolist()
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
                    top_3_state_sellers_df = fetch_overall_top3_states_sellers(conn, start_date, end_date, category,
                                                                       sub_category, None, state)
                else:
                    top_3_state_sellers_df = fetch_overall_top3_states_sellers(conn, start_date, end_date, category,
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
        df['date'] = df['order_month'].astype(int).apply(lambda x: f"{x:02}") + '-' + df['order_year'].astype(int).astype(str)

        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])

        formatted_data = {
            "series": [],
            "categories": df['date'].dt.strftime('%b-%y').unique().tolist()
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
        if state in ('undefined', 'all', 'None'):
            state = None
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
                    top_3_district_sellers_df = fetch_overall_top3_district_sellers(conn, start_date, end_date, category,
                                                                            sub_category, None, state)
                else:
                    top_3_district_sellers_df = fetch_overall_top3_district_sellers(conn, start_date, end_date, category,
                                                                            sub_category, None, None)
                formatted_data = self.get_formatted_data(top_3_district_sellers_df)

                cache.set(p_d, formatted_data, 60 * 60)
        else:
            formatted_data = data
        return JsonResponse(formatted_data, safe=False)


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
        if domain_name in ('None', None):
            domain_name = 'Retail'
        end_date = request.GET.get('endDate', None)
        start_date = request.GET.get('startDate', None)
        tab_name = request.GET.get('tabName', None)
        preview_limit = request.GET.get('previewLimit', None)

        # if not start_date or not end_date:
        #     return JsonResponse(date_error_msg, status=400)

        with connection.cursor() as conn:

            downloadable_data_df = self.convert_decimal_to_float(
                fetch_downloadable_data_overall(conn, start_date, end_date, domain_name, tab_name))

            if preview_limit:
                downloadable_data_df = downloadable_data_df.head(int(preview_limit))

            if downloadable_data_df is not None:
                for col_name, col_label in constant.download_table_col_reference.items():
                    if col_label in downloadable_data_df:
                        downloadable_data_df[col_label] = downloadable_data_df[col_label].astype(int)
                data_list = downloadable_data_df.to_dict(orient='records')
                # json_data = json.dumps(data_list, cls=CustomJSONEncoder)
                return JsonResponse(data_list, safe=False)
            else:
                return JsonResponse({"error": "Failed to fetch downloadable data."}, status=500)


@log_function_call(ondcLogger)
def summary(request):
    include_category = constant.INCLUDE_CATEGORY_FLAG
    if include_category == '1':
        include_category = True
    else:
        include_category = False
    context = {
        'include_category': include_category
    }
    return render(request, templatePath + 'index.html', context)


@log_function_call(ondcLogger)
def angular_app(request):
    development_type = os.getenv('DEPLOYMENT_TYPE')

    config = {
        'API_URL': development_type, 'ENABLE_STAGING_ROUTE': str(bool(development_type == 'stage'))
    }

    config_json = json.dumps(config, separators=(',', ':'))
    secret_key = os.getenv('PROJ_SEC_STR')
    signature = hmac.new(
        secret_key.encode(),
        config_json.encode(),
        hashlib.sha256
    ).hexdigest()

    return render(request, 'common/web/index.html', {'config': config, 'signature': signature})

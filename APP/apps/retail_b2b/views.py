__author__ = "Shashank Katyayan"
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from django.http import HttpRequest
from django.core.cache import cache
from django.db import connection
from collections import defaultdict
from dotenv import load_dotenv
import calendar

import pandas as pd
import numpy as np
from datetime import datetime
from apps.utils.helpers import get_cached_data


from apps.logging_conf import log_function_call, exceptionAPI, ondcLogger
from apps.src.api_response_utils import SummaryBaseDataAPI, shift_date_months
from apps.utils import constant
from apps.src.database_utils.database_utility import DatabaseUtility
from apps.src.database_utils.dal_retail_b2b import DataAccessLayer
from apps.src.database_utils.data_service_layer import DataService
from apps.src.database_utils.generic_queries import  fetch_district_list_query

db_utility = DatabaseUtility()
data_access_layer = DataAccessLayer(db_utility)
data_service = DataService(data_access_layer)
round_off_offset = 0


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

        data = get_cached_data(p_d)
        if data is None:
            with connection.cursor():
                district_list_df = self.fetch_data()
                state_district_mapping = defaultdict(list)
                for _, row in district_list_df.iterrows():
                    state = row['delivery_state']
                    district = row['delivery_district']
                    state_district_mapping[state].append(district)

            structured_data = {state: [district for district in districts]
                               for state, districts in state_district_mapping.items()}
            cache.set(p_d, structured_data, constant.CACHE_EXPIRY)
        else:
            structured_data = data
        return JsonResponse(structured_data, safe=False)

    def fetch_data(self):
        db_util = DatabaseUtility(alias='default')
        df = db_util.execute_query(fetch_district_list_query, return_type='df')
        return df


def fetch_state_list():
    query = f''' select distinct state_code as delivery_state_code_current from {constant.PINCODE_TABLE}'''
    db_util = DatabaseUtility(alias='default')
    df = db_util.execute_query(query, return_type='df')
    return df

def safe_divide(a, b, default=1):
    try:
        return np.divide(a, b)
    except Exception as e:
        return default


class FetchTopCardDeltaData(SummaryBaseDataAPI):

    def __init__(self):
        self.tooltip_text = {
            "Total Orders": 'Count of Distinct Network Order Id within the selected range.',
            "Districts": 'Unique count of Districts where orders have been delivered in the latest month within the date range. Districts are fetched using districts mapping using End pincode',
            "Sellers": 'Unique count of combination of (Provider ID + Seller App) within the date range',
            "records the highest order count": 'Maximum Orders by State/Districts, basis the date range. It will show top districts within a state if a state map is selected. Districts are mapped using delivery pincode.'

        }
    @exceptionAPI(ondcLogger)
    def get(self, request, *args):
        """
        APIView BaseDataAPI FetchTopCardDeltaData
        """
        params = self.extract_common_params(request)
        params['domain_name'] = 'Retail'

        try:
            cache_key = self.generate_cache_key(params)
            data = get_cached_data(cache_key)

            if data is None:
                top_cards_current = self.fetch_current_data(params)
                districts_count = data_service.get_district_count(**params)
                delta_required = 0 if (datetime.strptime(params['start_date'], "%Y-%m-%d").date()
                                   == datetime.strptime(constant.FIXED_MIN_DATE, "%Y-%m-%d").date()) else 1

                if delta_required:
                    previous_start_date, previous_end_date = self.get_previous_date_range(params)
                    params['start_date'], params['end_date'] = previous_start_date, previous_end_date
                    top_cards_previous = self.fetch_previous_data(params)
                else:
                    previous_start_date, previous_end_date = None, None
                    top_cards_previous = top_cards_current
                    top_cards_previous = top_cards_previous.drop(columns=['most_ordering_district'])
                merged_data = self.merge_data(top_cards_current, top_cards_previous)
                filtered_merged_df = self.clean_and_prepare_data(merged_data)

                total_district_count = districts_count['district_count'].sum()

                total_row = pd.DataFrame({
                    'delivery_state_code': ['TT'],
                    'delivery_state': ['Total'],
                    'district_count': [total_district_count]
                })

                districts_count = pd.concat([districts_count, total_row], ignore_index=True)
                top_cards_data = self.format_response_data(filtered_merged_df, previous_start_date, previous_end_date,
                                                           districts_count, delta_required)
                cache.set(cache_key, top_cards_data, constant.CACHE_EXPIRY)
            else:
                top_cards_data = data

            return JsonResponse(top_cards_data, safe=False)

        except Exception as e:
            error_message = {'error': f"An error occurred: {str(e)}"}
            return JsonResponse(error_message, status=200, safe=False)

    def generate_cache_key(self, params):
        cleaned_list = [params['domain_name'], params['start_date'], params['end_date'], params['state']]
        cleaned_list = [element for element in cleaned_list if element not in [None, 'None']]
        return "FetchTopCardDeltaData_Retail_B2B_$$$".join(cleaned_list)

    def fetch_current_data(self, params):
        return data_service.get_total_orders_summary(**params)

    def get_previous_date_range(self, params):
        original_start_date = params['start_date']
        original_end_date = params['end_date']
        previous_start_date, previous_end_date = shift_date_months(original_start_date, original_end_date)

        return previous_start_date, previous_end_date

    def fetch_previous_data(self, params):
        return data_service.get_total_orders_summary_prev(**params)

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
                              merged_df['total_districts_previous']), round_off_offset
        )
        merged_df['orders_count_delta'] = np.round(
            100 * safe_divide(merged_df['delivered_orders_current'] - merged_df['delivered_orders_previous'],
                              merged_df['delivered_orders_previous']), round_off_offset
        )
        # merged_df['sellers_count_delta'] = np.round(
        #     100 * safe_divide(merged_df['total_active_sellers_current'] - merged_df['total_active_sellers_previous'],
        #                       merged_df['total_active_sellers_previous']), round_off_offset
        # )

        merged_df = merged_df.replace([np.inf, -np.inf], 100).replace([np.nan], 0).fillna(0)

        return merged_df.drop(
            ['delivered_orders_previous', 'total_districts_previous', 'total_active_sellers_previous',
             'delivery_state_code_previous'], axis=1
        )

    def format_response_data(self, merged_df, previous_start_date, previous_end_date, district_count, delta_req=1):
        top_card_data = {}

        state_list = fetch_state_list()
        state_list.loc[len(state_list.index)] = ['TT']
        merged_df = pd.merge(state_list, merged_df, how='left', on='delivery_state_code_current', validate="many_to_many")
        merged_df['most_ordering_district'] = merged_df['most_ordering_district'].fillna(constant.NO_DATA_MSG)
        merged_df = merged_df.fillna(0)
        if delta_req:
            for _, row in merged_df.iterrows():
                state_code = row['delivery_state_code_current']
                if state_code not in top_card_data:
                    top_card_data[state_code] = [
                        self.create_metric_data(
                            int(row['delivered_orders_current']), 'Total Orders', row['orders_count_delta']
                            
                        ),
                        self.create_metric_data(
                            int(district_count[district_count['delivery_state_code'] == state_code]['district_count'].sum()),
                            'Districts', 0
                            
                        ),
                        # self.create_metric_data(
                        #     int(row['total_active_sellers_current']), 'Sellers', row['sellers_count_delta']
                            
                        # ),
                        self.create_max_orders_delivered_area_data(
                            row['most_ordering_district'])
                    ]

            date_format = '%b, %Y'
            prev_start_date_str = datetime.strftime(datetime.strptime(previous_start_date, '%Y-%m-%d'), date_format)
            prev_end_date_str = datetime.strftime(datetime.strptime(previous_end_date, '%Y-%m-%d'), date_format)

            return {
                "prev_date_range": f"Vs {prev_start_date_str}" if
                prev_start_date_str == prev_end_date_str else
                f"Vs {prev_start_date_str} - {prev_end_date_str}",
                "tooltip_text": self.tooltip_text,
                "top_card_data": top_card_data
            }
        else:

            for _, row in merged_df.iterrows():
                state_code = row['delivery_state_code_current']
                if state_code not in top_card_data:
                    top_card_data[state_code] = [
                        self.create_metric_data(
                            row['delivered_orders_current'], 'Total Orders', 0
                        ),
                        self.create_metric_data(
                            district_count[district_count['delivery_state_code'] == state_code]['district_count'].sum(),
                            'Districts', 0
                        ),
                        # self.create_metric_data(
                        #     row['total_active_sellers_current'], 'Sellers', 0
                        # ),
                        self.create_max_orders_delivered_area_data(
                            row['most_ordering_district'])
                    ]

            if previous_start_date is None or previous_end_date is None:
                return {
                    "prev_date_range": f"  ",
                    "tooltip_text": self.tooltip_text,
                    "top_card_data": top_card_data
                }

    def create_metric_data(self, count, heading, delta):
        if heading == 'Sellers' and count <3:
            return {
                "type": 'max_state',
                "heading": 'Sellers',
                "mainText": 'No Data To Display'
            }
        else:
            return {
                "type": 'default',
                "count": int(count),
                "heading": heading,
                "icon": 'trending_up' if delta >= 0 else 'trending_down',
                "positive": bool(delta >= 0),
                "percentageCount": float(delta),
                "showVarience": bool(delta)
            }

    def create_max_orders_delivered_area_data(self, most_ordering_district):
        return {
            "type": 'max_state',
            "heading": 'records the highest order count',
            "mainText": str(most_ordering_district)
        }



class FetchMapStateWiseData(SummaryBaseDataAPI):
    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchMapStateWiseData
        """
        params = self.extract_common_params(request)
        params['domain_name'] = 'Retail'
        p_d = [params['domain_name'], params['start_date'],
               params['end_date'], params['state']]
        cleaned_list = [element for element in p_d if element not in [None, 'None']]

        p_d = "FetchMapStateWiseData_Retail_B2B_$$$".join(cleaned_list)

        resp_data = get_cached_data(p_d)
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

            cache.set(p_d, json_data, constant.CACHE_EXPIRY)
        else:
            json_data = resp_data
        return JsonResponse(json_data, safe=False)


class FetchMapStateData(SummaryBaseDataAPI):
    @exceptionAPI(ondcLogger)
    def get(self, request, *args, **kwargs):
        """
        APIView BaseDataAPI FetchMapStateData
        """
        params = self.extract_common_params(request)
        params['domain_name'] = 'Retail'
        p_d = [params['domain_name'], params['start_date'],
               params['end_date'], params['state']]
        cleaned_list = [element for element in p_d if element not in [None, 'None']]

        p_d = "FetchMapStateData_Retail_B2B_$$$".join(cleaned_list)

        resp_data = get_cached_data(p_d)
        if resp_data is None:
            data = data_service.get_cumulative_orders_statedata_summary(**params)
            active_sellers_data_total = data_service.get_overall_active_sellers(**params)
            data.fillna(0, inplace=True)

            data['total_orders_delivered'] = pd.to_numeric(data['total_orders_delivered'], errors='coerce')
            active_sellers_data_total['active_sellers_count'] = pd.to_numeric(
                active_sellers_data_total['active_sellers_count'], errors='coerce')

            formatted_data = self.map_state_data_format(data, active_sellers_data_total)
            json_data = formatted_data

            cache.set(p_d, json_data, constant.CACHE_EXPIRY)

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
        params['domain_name'] = 'Retail'
        params_list = [value for value in params.values() if value not in [None, 'None']]

        p_d = "FetchTopStatesOrders_Retail_B2B_$$$".join(params_list)

        data = get_cached_data(p_d)

        if data is None:
            data = data_service.get_Retail_B2B_top_states_orders(**params)
            formatted_data = self.top_chart_format(data, chart_type='delivery_state')
            cache.set(p_d, formatted_data, constant.CACHE_EXPIRY)
        else:
            formatted_data = data
        return JsonResponse(formatted_data, safe=False)



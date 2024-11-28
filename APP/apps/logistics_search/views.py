__author__ = "Bikas Pandey"
from django.http import JsonResponse
from rest_framework.views import APIView
from django.http import HttpRequest
from django.core.cache import cache
from django.db import connection
from collections import defaultdict
from rest_framework import status
import pandas as pd
import numpy as np
from datetime import datetime
from apps.utils.helpers import get_cached_data


from apps.logging_conf import log_function_call, exceptionAPI, ondcLogger
from apps.src.api_response_utils import SummaryBaseDataAPI, shift_date_months
from apps.utils import constant
from apps.src.database_utils.database_utility import DatabaseUtility
from apps.src.database_utils.dal_logistic_search import DataAccessLayer
from apps.src.database_utils.data_service_layer import DataService
from apps.src.database_utils.generic_queries import  fetch_district_list_query

db_utility = DatabaseUtility()
data_access_layer = DataAccessLayer(db_utility)
data_service = DataService(data_access_layer)
round_off_offset = 0


def fetch_state_list():
    query = f''' select distinct "Statecode" as delivery_state_code_current from {constant.PINCODE_TABLE}'''
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
            "Total Orders": """Count of Distinct Network Order Id within the selected range.""",
            "Districts": """Unique count of Districts where orders have been delivered in the latest month within the date range. 
                Districts are fetched using districts mapping using End pincode""",
            "Sellers": 'Unique count of combination of (Provider ID + Seller App) within the date range',
            "records the highest order count": """Maximum Orders by State/Districts, basis the date range. 
                It will show top districts within a state if a state map is selected. Districts are mapped using delivery pincode."""
        }


    @exceptionAPI(ondcLogger)
    def get(self, request, *args):
        """
        APIView BaseDataAPI FetchTopCardDeltaData
        """
        city = request.GET.get('city', None)
        start_date = request.GET.get('startDate', None)
        end_date = request.GET.get('endDate', None)
        day_type = request.GET.get('dayType', 'All')

        if not start_date or not end_date:
            return JsonResponse(error_message, status=400, safe=False)
        
        params = {
            'city': city,
            'start_date': start_date,
            'end_date': end_date,
            'day_type': day_type
        }

        try:
            cache_key = f"Logistic_search_FetchTopCardDeltaData_{self.generate_cache_key(params)}"
            data = get_cached_data(cache_key)
            if data is None:
                card_data = data_service.get_logistic_searched_top_card_data(**params)

                card_data['city'] = city
                
                fetched_data = []
                
                if not city:
                    time_of_days = card_data['time_of_day'].unique()

                    for time in time_of_days:
                        df_data = card_data[card_data['time_of_day'] == time]

                        searched_sum = df_data['searched_data'].sum()

                        fetched_data.append(
                            {
                                'state': 'TT', 
                                'time_of_day': time, 
                                'total_conversion_percentage': "{:.2f}".format((df_data['confirmed_data'].sum()/(searched_sum if searched_sum else 1))*100),
                                'total_assigned_percentage':"{:.2f}".format((df_data['assigned_data'].sum()/(searched_sum if searched_sum else 1))*100),
                                'searched_data': searched_sum
                            }
                        )
                
                card_data = card_data.drop(columns=['confirmed_data', 'assigned_data'])

                fetched_data += card_data.to_dict(orient="records")
                formatted_response = {"data": {}}

                if not city:
                    for record in fetched_data:
                        state = record["state"]
                        time_of_day = record["time_of_day"]
                        # Ensure state exists in the formatted structure
                        if state not in formatted_response["data"]:
                            formatted_response["data"][state] = {}
                        # Add the time_of_day data
                        formatted_response["data"][state][time_of_day] = {
                            k: v for k, v in record.items() if k not in ["state", "time_of_day"]
                        }
                else:
                    for record in fetched_data:
                        time_of_day = record["time_of_day"]
                        # Ensure state exists in the formatted structure
                        if city not in formatted_response["data"]:
                            formatted_response["data"][city] = {}
                        # Add the time_of_day data
                        formatted_response["data"][city][time_of_day] = {
                            k: v for k, v in record.items() if k not in ["city", "time_of_day"]
                        }
                cache.set(cache_key, formatted_response, constant.CACHE_EXPIRY)
            else:
                formatted_response = data
            return JsonResponse(formatted_response, safe=False)

        except Exception as e:
            error_message = {'error': f"An error occurred: {str(e)}"}
            return JsonResponse(error_message, status=500, safe=False)

    def generate_cache_key(self, params):
        p_d = params.values()
        cleaned_list = [element for element in p_d if element not in [None, 'None']]
        return "FetchTopCardDeltaData_Logistic_Search_$$$".join(cleaned_list)


class FetchCityWiseData(SummaryBaseDataAPI):
    @exceptionAPI(ondcLogger)
    def get(self, request, *args):
        """
        APIView BaseDataAPI FetchCityWiseData
        """

        city = request.GET.get('city', None)
        start_date = request.GET.get('startDate', None)
        end_date = request.GET.get('endDate', None)
        day_type = request.GET.get('dayType', 'All')

        if not start_date or not end_date:
            return JsonResponse(error_message, status=400, safe=False)

        if not city:
            error_message = {'error': "Bad request! City not provided"}
            return JsonResponse(error_message, status=400, safe=False)
        
        params = {
            'city': city,
            'start_date': start_date,
            'end_date': end_date,
            'day_type': day_type
        }

        try:
            cache_key = f"Logistic_search_FetchCityWiseData_{self.generate_cache_key(params)}"
            data = get_cached_data(cache_key)
            if data is None:
                df = data_service.get_logistic_searched_data(**params)

                insight_data = self.prepare_insight_data(df)
                result = {}

                grouped = df.groupby('pick_up_pincode')

                for pincode, group in grouped:
                    result[pincode] = {}
                    
                    for _, row in group.iterrows():
                        result[pincode][row['time_of_day']] = {
                            'conversion_rate': row['conversion_rate'],
                            'assigned_rate': row['assigned_rate'],
                            'searched_data': row['searched_data'],
                            'pincode': int(pincode)
                        }
                fetched_data = result

                response_data = {'mapData': fetched_data, 'insightData': insight_data}
                cache.set(cache_key, response_data, constant.CACHE_EXPIRY)
            else:
                response_data = data
            return JsonResponse({"data": response_data}, safe=False)

        except Exception as e:
            error_message = {'error': f"An error occurred: {str(e)}"}
            return JsonResponse(error_message, status=500, safe=False)
    
    def prepare_insight_data(self, df):
        # time_of_days = df['time_of_day'].unique()
        time_of_days = ["Overall", "3am-6am", "6am-8am", "8am-10am", "10am-12pm", 
            "12pm-3pm", "3pm-6pm", "6pm-9pm", "9pm-12am", "12am-3am"]

        insight_data = {
            'high_demand': {},
            'high_conversion_rate': {},
            'high_demand_and_high_conversion_rate': {}, 
            'high_demand_and_low_conversion_rate': {},
            # 'high_demand_in_morning_hours': {},
            # 'high_demand_in_evening_hours': {}
        }

        for time in time_of_days:
            filtered_df = df[df['time_of_day']==time]

            # for high demand
            high_demand_df = filtered_df.sort_values(by='searched_data', ascending=False)[:10]

            data = {}
            for _, row in high_demand_df.iterrows():
                data[row['pick_up_pincode']] = {
                    'conversion_rate': float(row['conversion_rate']),
                    'searched_data': int(row['searched_data']),
                    'pincode': int(row['pick_up_pincode']),
                    'assigned_rate': float(row['assigned_rate'])
                }
            
            insight_data['high_demand'][str(time)] = data


            # insight_data['high_demand_in_morning_hours'][str(time)] = data if (time=='8am-10am') else {}
            # insight_data['high_demand_in_evening_hours'][str(time)] = data if (time=='6pm-9pm') else {}

            # high conversion rate

            high_conversion_rate_df = filtered_df.sort_values(by='conversion_rate', ascending=False)[:10]

            data = {}
            for _, row in high_conversion_rate_df.iterrows():
                data[row['pick_up_pincode']] = {
                    'conversion_rate': row['conversion_rate'],
                    'searched_data': row['searched_data'],
                    'pincode': int(row['pick_up_pincode'])
                }
            
            insight_data['high_conversion_rate'][str(time)] = data

            # high demand and high conversion rate
            
            searched_data_sum = float(filtered_df['searched_data'].sum())
            filtered_df['search %'] = (filtered_df['searched_data'].astype(float) / searched_data_sum) * 100.0

            average_conversion_rate = round(filtered_df['conversion_rate'].mean(), 0)
            filtered_df['conversion_rate_gt_avg'] = np.where(
                filtered_df['conversion_rate'] > average_conversion_rate,
                filtered_df['conversion_rate'],
                0
            )

            filtered_df = filtered_df.sort_values(by='search %', ascending=False)

            filtered_df_1 = filtered_df[filtered_df['conversion_rate_gt_avg'] != 0]
            filtered_df_1 = filtered_df_1[:10]


            data = {}
            for _, row in filtered_df_1.iterrows():
                data[row['pick_up_pincode']] = {
                    'conversion_rate': row['conversion_rate'],
                    'searched_data': row['searched_data'],
                    'pincode': int(row['pick_up_pincode'])
                }
            
            
            insight_data['high_demand_and_high_conversion_rate'][str(time)] = data

            # high demand and low conversion rate
            filtered_df_2 = filtered_df[filtered_df['conversion_rate_gt_avg'] == 0]
            filtered_df_2 = filtered_df_2[:10]
            data = {}

            for _, row in filtered_df_2.iterrows():
                data[row['pick_up_pincode']] = {
                    'conversion_rate': row['conversion_rate'],
                    'searched_data': row['searched_data'],
                    'pincode': int(row['pick_up_pincode'])
                }
            insight_data['high_demand_and_low_conversion_rate'][str(time)] = data
        
        # insight_data['high_demand_in_morning_hours']['Overall'] = insight_data['high_demand_in_morning_hours']['8am-10am']
        # insight_data['high_demand_in_evening_hours']['Overall'] = insight_data['high_demand_in_evening_hours']['6pm-9pm']
        return insight_data

    
    def generate_cache_key(self, params):
        p_d = params.values()
        cleaned_list = [element for element in p_d if element not in [None, 'None']]
        return "FetchCityWiseData_Logistic_Search_$$$".join(cleaned_list)


class FetchDateRange(SummaryBaseDataAPI):
    
    def get(self, request, *args):

        df = data_service.get_logistic_searched_data_date_range()
        date_range = {  
            "min_date": df.min()['min'].strftime('%Y-%m-%d'),
            "max_date": df.min()['max'].strftime('%Y-%m-%d')
        }

        return JsonResponse(date_range, status=200, safe=False) 


class FetchOverallIndiaData(APIView):
    @exceptionAPI(ondcLogger)
    def get(self, request, *args):
        """
            APIView BaseDataAPI FetchOverallIndiaData
        """
        start_date = request.GET.get('startDate', None)
        end_date = request.GET.get('endDate', None)
        day_type = request.GET.get('dayType', 'All')

        if not start_date and not end_date:
            error_message={'error': f"an error occured"}
            return JsonResponse(error_message, status=400)
        params = {
            'start_date' : start_date,
            'end_date' : end_date,
            'day_type': day_type
        }
        try:
            cache_key = f"Logistic_search_FetchOverallIndiaData_{self.generate_cache_key(params)}"
            data = get_cached_data(cache_key)
            if data is None:
                df = data_service.get_overall_total_searches(**params)
                df['total_searches'] = df['total_searches'].astype(int)
                result = df.to_dict(orient="records")
                return JsonResponse({"mapdata": result}, safe=False)
        
        except Exception as e:
            error_message = {'error': f"An error occurred: {str(e)}"}
            return JsonResponse(error_message, status=500)

    def generate_cache_key(self, params):
        p_d = params.values()
        cleaned_list = [element for element in p_d if element not in [None, 'None']]
        return "FetchStateWiseData_Logistic_Search_$$$".join(cleaned_list)
    

class FetchStateData(APIView):
    @exceptionAPI(ondcLogger)
    def get(self, request, *args):
        """
            APIView BaseDataAPI FetchStateData
        """
        start_date = request.GET.get('startDate', None)
        end_date = request.GET.get('endDate', None)
        state = request.GET.get('state', None)
        day_type = request.GET.get('dayType', 'All')

        if not (start_date and end_date and state):
            error_message={'error': f"an error occured"}
            return JsonResponse(error_message, status=400)
        params = {
            'start_date' : start_date,
            'end_date' : end_date,
            'state': state,
            'day_type': day_type
        }
        try:
            cache_key = f"Logistic_search_FetchStateData_{self.generate_cache_key(params)}"
            data = get_cached_data(cache_key)
            if data is None:
                df = data_service.get_overall_total_searches(**params)
                result = df.to_dict(orient="records")
                return JsonResponse({"mapdata": result}, safe=False)
        
        except Exception as e:
            error_message = {'error': f"An error occurred: {str(e)}"}
            return JsonResponse(error_message, status=500)

    def generate_cache_key(self, params):
        p_d = params.values()
        cleaned_list = [element for element in p_d if element not in [None, 'None']]
        return "FetchStateWiseData_Logistic_Search_$$$".join(cleaned_list)
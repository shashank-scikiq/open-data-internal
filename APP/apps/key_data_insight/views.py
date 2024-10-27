__author__ = "Bikas Pandey"

import os
import json
from copy import deepcopy
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.utils import constant
from apps.utils.helpers import get_cached_data
from django.core.cache import cache


json_location = os.getenv("JSON_LOCATION")

class FetchActiveSellerData(APIView):
    def get(self, request):
        return JsonResponse({"response": "dummy"}, safe=status.HTTP_200_OK)
        cache_key = "Key_data_insights"
        data = get_cached_data(cache_key)
        if data is None:
            response_insights = []

            insights = constant.INSIGHTS_MAP

            for i in insights.keys():
                if not insights.get(i, None):
                    continue
                try:
                    formatted_response = self.read_and_prepare_insights_data(file_name=i)
                    response_insights.append(formatted_response)
                except Exception as e:
                    return JsonResponse({"error": "Something went wrong in loading/preparing data.", "msg": e}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            
            response_data = {"insights": response_insights}
            cache.set(cache_key, response_data, constant.CACHE_EXPIRY)
        else:
            response_data = data
        
        return JsonResponse(response_data, safe=status.HTTP_200_OK)


    def read_and_prepare_insights_data(self, file_name):
        data = None
        insights_folder_dir = constant.INSIGHTS_FOLDER_DIR
        file_path = f"{insights_folder_dir}{file_name}.json"


        if os.path.exists(file_path):
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)

        meta_data = data.get("metaData", None)

        if meta_data:
            processed_meta_data = self.prepare_meta_data(file_name, meta_data['data'])
            data['metaData']['data'] = processed_meta_data
        
        return data
    
    def prepare_meta_data(self, file_name, data):
        meta_data = {}

        if file_name == 'active_sellers_share_india':
            meta_data = {
                "series": [
                    {
                        "name": 'Active Sellers',
                        "data": []
                    },
                    {
                        "name": 'Inactive Sellers',
                        "data": []
                    }
                ],
                "categories": [],
                "colors": ["#72A950", "#C4C4C4"]
            }
            for i in data:
                meta_data['series'][0]['data'].append(i['active_perc'])
                meta_data['series'][1]['data'].append(i['inactive_perc'])
                meta_data['categories'].append(i['month_year'])
        
        if file_name == 'new_repeat_sellers':
            meta_data = {
                "series": [
                    {
                        "name": 'New Sellers',
                        "data": []
                    },
                    {
                        "name": 'Repeat Sellers',
                        "data": []
                    }
                ],
                "categories": [],
                "colors": ["#9AB187", "#F3C881"]
            }
            for i in data:
                meta_data['series'][0]['data'].append(i['new'])
                meta_data['series'][1]['data'].append(i['repeat'])
                meta_data['categories'].append(i['Month-Year'])
            

        return meta_data
    
    ########### METADATA TYPE METHOD ################

    def process_table(self, meta_data):
        return {
            "title" : meta_data.get("title", ""),
            "subtitle" : meta_data.get("subtitle", ""),
            "data" : meta_data.get("data", [])
        }
    
    def process_line_chart(self,meta_data):
        return {
            "title" : meta_data.get("title"),
            "data": [
                {"date": item["order_date"], "active_sellers": item["active_sellers"]}
                for item in meta_data.get("data", [])
            ]
        }
    
    def process_bar_graph(self, meta_data):
        return {
        "title": meta_data.get("title", ""),
        "xaxis": {
            "categories": [item["order_date"] for item in meta_data.get("data", [])],
            
        },
        "yaxis": {
            "title": {
                "text": None  
            }
        },
        "data": [item["active_sellers"] for item in meta_data.get("data", [])]  
    }
    
    def process_pie_chart(self, meta_data):
        
        data_json = {
            f"slice_{index + 1}": {
                "label": item["order_date"],
                "value": item["active_perc"]
            }
            for index, item in enumerate(meta_data.get("data", []))
        }
        return {
            "title": meta_data.get("title", ""),
            "slices": data_json  
        }
        




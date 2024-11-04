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
        # return JsonResponse({"response": "dummy"}, safe=status.HTTP_200_OK)
        cache_key = "Key_data_insights"
        data = get_cached_data(cache_key)
        if data is None:
            response_insights = []

            insights = constant.INSIGHTS_MAP

            for i in insights.keys():
                print(f"Processing {i}")
                if not insights.get(i, None):
                    continue
                # try:
                formatted_response = self.read_and_prepare_insights_data(file_name=i)
                response_insights.append(formatted_response)
                # except Exception as e:
                #     return Response({"error": "Something went wrong in loading/preparing data."}, 
                #         status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            
            response_data = {"insights": response_insights}
            cache.set(cache_key, response_data, constant.CACHE_EXPIRY)
        else:
            response_data = data
        
        return JsonResponse(response_data, safe=status.HTTP_200_OK)


    def read_and_prepare_insights_data(self, file_name):
        data = None
        insights_folder_dir = constant.INSIGHTS_FOLDER_DIR
        file_path = f"{insights_folder_dir}{file_name}.json"
        # import pdb; pdb.set_trace()


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

        if file_name == "active_sellers_location":
            meta_data = {
                "series": [
                    {
                        "name": "Tier 1",
                        "data": []
                    },
                    {
                        "name": "Tier 2",
                        "data": []
                    },
                    {
                        "name": "Tier 3",
                        "data": []
                    }
                ],
                "colors": ["#A8D8B9", "#6A9BD1", "#FFA500"]

            }
            for i in data:
                meta_data['series'][
                    0 if i['Tier'] == 'Tier 1' else (1 if i['Tier'] == 'Tier 2' else 2)
                ]['data'].append({
                    "x": i['City'],
                    "y": i['perc_active_sellers']
                })

        if file_name == "active_total_sellers_national":
            meta_data = {
                "series": [
                    {
                        "name": 'Active Sellers',
                        "data": []
                    }
                ],
                "categories": [],
                "colors": ["#fcb65e"],
                "legends": ["Active Sellers"]
            }
            for i in data:
                meta_data['series'][0]['data'].append(i['perc_active'])
                meta_data['categories'].append(i['month_year'])

        if file_name == 'active_total_sellers_category':
            meta_data = {
                "colors": ["#fcb65e"],
                "legends": ["Active Sellers"],
                "charts": {}
            }
            for i in data:
                if not meta_data['charts'].get(i['category'], None):
                    meta_data['charts'][i['category']] = {
                            "series": [
                                {
                                    "name": 'Active Sellers',
                                    "data": []
                                }
                            ],
                            "categories": [],
                            
                        }

                meta_data['charts'][i['category']]['series'][0]['data'].append(i['perc_active'])
                # meta_data['charts'][i['category']]['series'][1]['data'].append(i['inactive_perc'])
                meta_data['charts'][i['category']]['categories'].append(i['month_year'])
        
        if file_name == 'active_total_sellers_state_sep':
            meta_data = {
                "colors": ["#fcb65e", "#dbdbdb"],
                "legends": ["Active Sellers", "Inactive Sellers"],
                "charts": {}
            }

            for i in data:
                if not meta_data["charts"].get(i['region'], None):
                    meta_data["charts"][i['region']] = {
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
                        
                    }
                meta_data["charts"][i['region']]['series'][0]['data'].append(i['perc_active'])
                meta_data["charts"][i['region']]['series'][1]['data'].append(i['perc_inactive'])
                meta_data["charts"][i['region']]['categories'].append(i['seller_state'])
        
        if file_name == 'qsr_distribution':
            meta_data = {
                "colors": ['#8E8FD1', '#E0E0E0'],
                "legends": ['QSR deliveries', 'Non-QSR deliveries'],
                "charts": {}
            }
            for i in data:
                meta_data["charts"][i['City']] = {
                    "series": [int(i['perc_QSR']), int(i['perc_NonQSR'])],
                    "labels": ['QSR deliveries', 'Non-QSR deliveries'],
                    "labelsColor": ["#fff", "#000"]
                }

        
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
        




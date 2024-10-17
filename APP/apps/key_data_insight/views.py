__author__ = "Bikas Pandey"

import os
import json
from copy import deepcopy
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

json_location = os.getenv("JSON_LOCATION")

class FetchActiveSellerData(APIView):
    def get(self, request, *args, **Kwargs):
        json_file_path= os.path.join(json_location, 'active_sellers_daily.json')
        
 
        try:
            # import pdb;pdb.set_trace()
            with open(json_file_path, 'r') as json_file:
                data= json.load(json_file)
        except FileNotFoundError:
            return Response({"error": "file not found"}, status=status.HTTP_404_NOT_FOUND)
        except json.JSONDecodeError:
            return Response({"error":"Invalid json format"}, status=status.HTTP_400_BAD_REQUEST)
        
        response_data = deepcopy({
            'card_title' : data.get("cardTitle", None),
            'main_text' : data.get("mainText", None),
            'sub_text' : data.get("subText", None)
        })

        if not data.get("isDetailsVisible", False):
            return Response(response_data, status.HTTP_200_OK)
        meta_data = data.get("metaData", {})
        meta_type = meta_data.get("type")

        if meta_type == 'table':
            response_data["metaData"]= self.process_table(meta_data)
        elif meta_type == 'line_chart':
            response_data["metaData"]= self.process_line_chart(meta_data)
        elif meta_type == 'pie_chart':
            response_data["metaData"]= self.process_pie_chart(meta_data)
        elif meta_type == 'bar_graph':
            response_data["metaData"]= self.process_bar_graph(meta_data)
        else:
            return Response({"error": "Unsupported metadata type"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(response_data, status=status.HTTP_200_OK)
    

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
            "date": [item["order_date"] for item in meta_data.get("data", [])],
            
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
        




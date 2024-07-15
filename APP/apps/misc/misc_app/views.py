from django.shortcuts import render

from django.http import JsonResponse
from dotenv import load_dotenv
from django.db import connection
import csv
import os

from apps.logging_conf import exceptionAPI, ondcLogger
from apps.src.database_utils.generic_queries import pincode_query
load_dotenv()

sub_category_none_values = ('undefined', 'all', 'None', 'Select Sub-Category')
chart_date_format = '%d-%b'

date_error_msg = {"error": "Start date and end date are required."}

templatePath = 'apps/misc/web/html/'


@exceptionAPI(ondcLogger)
def fetch_license(request):
    """
        APIView fetch_license
    """
    return render(request, 'apps/misc/web/html/license.html')


@exceptionAPI(ondcLogger)
def data_dictionary(request):
    """
    APIView data_dictionary
    """
    csv_file_path = os.environ.get("DATA_DICTIONARY_FILE", 'data_dictionary_open_data_dashboard.csv')

    with open(csv_file_path, 'r') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)
        data_rows = [row for row in csv_reader]

    response_data = {"headers": headers, "rows": data_rows}

    return JsonResponse(response_data, safe=False)


@exceptionAPI(ondcLogger)
def pincode(request):
    """
        APIView pincode
    """

    with connection.cursor() as conn:
        conn.execute(pincode_query)
        data_rows = conn.fetchall()
        headers = [desc[0] for desc in conn.description]
    response_data = {"headers": headers, "rows": data_rows}

    return JsonResponse(response_data, safe=False)


@exceptionAPI(ondcLogger)
def domain(request):
    """
            APIView domain
    """
    csv_file_path = os.environ.get("DOMAIN_MAPPING_FILE", 'domain_mapping_open_data_dashboard.csv')

    with open(csv_file_path, 'r') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)
        data_rows = [row for row in csv_reader]

    response_data = {"headers": headers, "rows": data_rows}

    return JsonResponse(response_data, safe=False)


@exceptionAPI(ondcLogger)
def data_dictionary_page(request):
    """
            APIView data_dictionary_page
    """
    return render(request, templatePath+'data_dictionary.html')


    



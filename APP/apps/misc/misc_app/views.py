from django.shortcuts import render
from django.core.cache import cache

from django.http import JsonResponse
from dotenv import load_dotenv
from django.db import connection
import csv
import os
import json
from apps.utils import constant
from apps.src.database_utils.database_utility import DatabaseUtility

from apps.logging_conf import exceptionAPI, ondcLogger
from apps.src.database_utils.generic_queries import pincode_query #landing_page_echart_data_query
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


def prepare_echart_data_for_landing_page(df):
    columns = df.columns.tolist()
    data = [[i[0].strip(), i[1].strftime('%Y-%m-%d'), i[2]] for i in df.values.tolist()]
    last_updated_date = df['date'].max().strftime('%B %Y')

    echart_config = json.loads(constant.LANDING_PAGE_ECHART_CONFIG).get('config', {})

    return {
        "lastUpdatedAt": last_updated_date,
        "chartConfig": echart_config,
        "data": [columns,] + data
    }

@exceptionAPI(ondcLogger)
def landing_page_echart_data(request):
    """
        APIView for landing page echart data
    """
    resp_data = {}
    p_d = "LandingPageEchartData_$$$"

    data = cache.get(p_d)

    if not data:
        db_util = DatabaseUtility(alias='default')
        df = db_util.execute_query(landing_page_echart_data_query, return_type='df')
        resp_data = prepare_echart_data_for_landing_page(df)
        cache.set(p_d, resp_data, constant.CACHE_EXPIRY)
    else:
        resp_data = data

    return JsonResponse(resp_data, safe=False)


def key_insights(request):
    return JsonResponse({
        'insights': [
            {
                'cardText': 'What % of active sellers contribute to 80% of the total Orders?',
                'title': "7% of the Active Sellers ",
                'subText': "contribute to 80% of the orders.",
                'metaData': False
            },
            {
                'cardText': 'What % of the total sellers are active with atleast 1 order?',
                'title': '10% of the total Sellers ',
                'subText': "have completed atleast 1 order.",
                'metaData': False
            },
            {
                'cardText': 'What are the top 5 subcategories in retail, that contribute to the highest number of orders on the Network ?',
                'title': '',
                'subText': "",
                'metaData': False,
                'query': """    
                    SELECT 
                        sum(aa.total_orders_delivered) as total_orders_delivered, aa.sub_category, aa.category
                        FROM ec2_all.sub_cat_district_wise_monthly_aggregates aa where domain_name = 'Retail' and order_year = 2024 and order_month = 8
                        group by domain_name, sub_category, category
                        order by total_orders_delivered desc, aa.category
                    limit 5
                """
            },
            {
                'cardText': 'What are the top 3 sub categories that show highest growth since the last Month ? ',
                'title': "",
                'subText': "",
                'metaData': False,
                'query': """
                    select upper(sub_category) as sub_category,
                        current_period,
                        prev_period,
                        gain_percent
                        from ec2_all.key_insights_sub_category
                        where current_mtd_demand > 1
                        order by gain_percent desc
                        limit 3
                    """
            },
            {
                'cardText': 'What is the distribution of states across Orders completed?',
                'title': "",
                'subText': "",
                'metaData': False
            }
        ]}, safe=False)



from apps.src.database_utils.generic_queries import (
    landing_page_echart_data_query, landing_page_cumulative_orders_query
)

import json
from apps.logging_conf import exceptionAPI, ondcLogger
from apps.utils import constant
from django.core.cache import cache
from apps.src.database_utils.database_utility import DatabaseUtility
from django.http import JsonResponse



def prepare_echart_data_for_landing_page(df):
    columns = df.columns.tolist()
    data = [[i[0].strip(), i[1].strftime('%Y-%m-%d'), i[2]] for i in df.values.tolist()]
    last_updated_date = df['date'].max().strftime('%B %d, %Y')

    echart_config = json.loads(constant.LANDING_PAGE_ECHART_CONFIG).get('config', {})

    return {
        "lastUpdatedAt": last_updated_date,
        "chartConfig": echart_config,
        "data": [columns,] + data
    }

@exceptionAPI(ondcLogger)
def landing_page_echart_data(request):
    """
        APIView for landing_page_echart_data
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


@exceptionAPI(ondcLogger)
def landing_page_cumulative_orders(request):
    """
        APIView for landing_page_cumulative_orders
    """
    resp_data = {}
    p_d = "LandingPageCumulativeOrders_$$$"

    data = cache.get(p_d)

    if not data:
        db_util = DatabaseUtility(alias='default')
        df = db_util.execute_query(landing_page_cumulative_orders_query, return_type='df')
        chart_data = df.to_dict(orient='records')[0]
        
        resp_data = {
            "updatedAt": chart_data['max'].strftime("%B %Y"),
            "order_count": int(chart_data['total_orders']) 
        }
        cache.set(p_d, resp_data, constant.CACHE_EXPIRY)
    else:
        resp_data = data

    return JsonResponse(resp_data, safe=False)

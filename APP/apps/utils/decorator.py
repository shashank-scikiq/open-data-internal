from functools import wraps
from django.http import JsonResponse
from django.core.cache import cache
from rest_framework import status
import os
import pandas as pd
from django.db import connection
from apps.utils import constant
# from django_setup.settings import APP_VERSION
import logging
from apps.utils.constant import ONDC_DASHBOARD_VERSION_TABLE

from apps.utils.helpers import get_cached_data


def verify_version():
    query = f"""
        SELECT
            id,
            major,
            minor,
            minor_minor
        FROM
            {ONDC_DASHBOARD_VERSION_TABLE}
        WHERE id = (select max(id) from {ONDC_DASHBOARD_VERSION_TABLE} )
    """

    version = pd.read_sql_query(query, connection)
    print(version)
    if len(version.index) > 0 :
        db_version = '{}.{}.{}'.format(str(version["major"][0]),
        str(version["minor"][0]), str(version["minor_minor"][0]))
        if APP_VERSION != db_version :
            error_msg = 'Application and Database version mismatch!'
            logging.exception("verifyVersion :" + str(error_msg) + ' ' +  APP_VERSION +' '+ db_version )
            # sys.exit(error_msg)

    else :
        error_msg = 'Application and Database version mismatch!'
        logging.exception("verifyVersion :" + str(error_msg) + ' ' +  APP_VERSION +' DB Version Not Available' )
        # sys.exit(error_msg)

def api_decorator():
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            func_name = func.__name__
            class_name = None

            if hasattr(func, '__qualname__'):  # For methods
                class_name = func.__qualname__.split('.')[0]
            if hasattr(func, '__self__') and func.__self__:
                class_name = func.__self__.__class__.__name__

            function_key = "$$$".join([func_name, args[1].query_params.urlencode()])

            cached_data = get_cached_data(class_name) or {}

            if function_key in cached_data:
                response_data = cached_data[function_key]
            else:
                response_data = func(*args, **kwargs)
                cached_data[function_key] = response_data

                cache.set(class_name, cached_data, constant.CACHE_EXPIRY)

            return JsonResponse(response_data, safe=False, status=status.HTTP_200_OK)

        return inner
    return wrapper




# verify_version()

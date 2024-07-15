import os
import pandas as pd
from django.db import connection
from django_setup.settings import APP_VERSION
from apps.logging_conf import log_function_call
import logging
import sys


ONDC_DASHBOARD_VERSION_TABLE = os.getenv('ONDC_DASHBOARD_VERSION_TABLE', 'ondc_dashboard_version')


# @log_function_call
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


verify_version()

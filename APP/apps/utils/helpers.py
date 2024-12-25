from django.core.cache import cache
from datetime import datetime
from apps.utils import constant
from dateutil.relativedelta import relativedelta


def get_cached_data(key):
    try:
        data = cache.get(key)
        return data
    except Exception as e:
        print('There is some issue with the cache, was called for the key', key)
        return None

def is_delta_required(params):
    return datetime.strptime(params['start_date'], "%Y-%m-%d").date() != datetime.strptime(
        constant.FIXED_MIN_DATE, "%Y-%m-%d"
    ).date()

def shift_date_months(start_date_str, end_date_str, months=-1):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    new_start_date = start_date + relativedelta(months=months)
    new_end_date = end_date + relativedelta(months=months)
    return new_start_date.strftime("%Y-%m-%d"), new_end_date.strftime("%Y-%m-%d")

def get_previous_date_range(params):
    original_start_date = params['start_date']
    original_end_date = params['end_date']
    previous_start_date, previous_end_date = shift_date_months(original_start_date, original_end_date)

    return previous_start_date, previous_end_date
from datetime import datetime
from apps.utils import constant
from dateutil.relativedelta import relativedelta

top_card_tooltip_text = {
    'Total Orders': 'Count of Distinct Network Order Id within the selected range.',
    'Districts': '''Unique count of Districts where orders have been delivered in the latest month within the date range. 
        Districts are fetched using districts mapping using End pincode''',
    'Total sellers': 'Unique count of combination of (Provider ID + Seller App) within the date range',
    'Active sellers': 'Unique count of combination of active (Provider ID + Seller App) within the date range',
    'records the highest order count': '''Maximum Orders by State/Districts, basis the date range. It will show top 
        districts within a state if a state map is selected. Districts are mapped using delivery pincode.''',
    'No. of items per order': 'Average items per orders'
}

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

def safe_divide(a, b, default=1):
    try:
        return a/b
    except Exception as e:
        return default
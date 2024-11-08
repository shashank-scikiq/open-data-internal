import os


FIXED_MIN_DATE = os.getenv('START_DATE')

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
ENABLE_CONSOLE_LOG = enable_console_log = os.getenv('ENABLE_CONSOLE_LOG', 'true').lower() in ('true', '1', 't')
ONDC_DASHBOARD_VERSION_TABLE = os.getenv('ONDC_DASHBOARD_VERSION_TBL', 'ondc_dashboard_version')

DISTRICT_TABLE = os.environ.get("DISTRICT_TBL")
SUB_CATEGORY_TABLE = os.environ.get("SUB_CATEGORY_TBL")
CATEGORY_TABLE = os.environ.get("CATEGORY_TBL")

sub_category_none_values = ('undefined', 'all', 'None', 'Select Sub-Category', 'All')
chart_date_format = '%d-%b'

date_error_msg = {"error": "Start date and end date are required."}

PINCODE_TABLE = os.getenv('TBL_PINCODE')

SELLER_TABLE = os.environ.get("SELLER_TBL")

B2B_DISTRICT_TABLE = os.environ.get("B2B_DISTRICT_TBL")

SUB_CATEGORY_PENETRATION_TABLE = os.environ.get("SUB_CATEGORY_PENETRATION_TBL")
ACTIVE_SELLERS_MASKING = os.environ.get("ACTIVE_SELLERS_MASKING")

category_sub_query = " AND category = %s"
sub_category_sub_query = " AND sub_category = %s"
domain_sub_query = " AND domain_name = %s"
delivery_state_sub_query = " AND upper(delivery_state) = upper(%s)"
seller_state_sub_query = " AND upper(seller_state) = upper(%s)"
NO_DATA_MSG = 'No Data to Display'
SUB_CATEGORY_PENETRATION_SELLERS = os.environ.get("SUB_CATEGORY_PENETRATION_TBL")
RV_DISTRICT_TABLE = os.environ.get("RV_DISTRICT_TBL")
DIM_DISTRICTS = os.environ.get("DIM_DISTRICTS", 'dim_districts')
DIM_CATEGORIES = os.environ.get("DIM_CATEGORIES", 'dim_categories')
DIM_DATES = os.environ.get("DIM_DATES", 'dim_dates')
B2B_DIM_DATES = os.environ.get("B2B_DIM_DATES", 'retail_b2b_dim_dates')
sub_category_ranking_sub_query = " AND scp.category = %(category)s"
swdlo_sub_category_ranking_sub_query = " AND swdlo.sub_category = %(sub_category)s"

category_ranking_sub_query = " AND scp.sub_category = %(sub_category)s"
swdlo_category_ranking_sub_query = " AND swdlo.category = %(category)s"

seller_category_ranking_sub_query = " AND ds.category = %(category)s"
seller_sub_category_ranking_sub_query = " AND ds.sub_category = %(sub_category)s"

tdr_domain_sub_query = " AND om.domain_name = %s"
swdlo_domain_sub_query = " AND swdlo.domain_name = %s"
tdr_sub_category_sub_query = " AND om.sub_category = %s"
tdr_category_sub_query = " AND om.category = %s"
tdr_delivery_state_sub_query = " AND upper(om.delivery_state) = upper(%s)"
tdr_seller_state_sub_query = " AND upper(om.seller_state) = upper(%s)"

swdlo_cat_sub_query = " AND swdlo.category = %s"
swdlo_sub_cat_sub_query = " AND swdlo.sub_category = %s"
swdlo_domain_sub_query_overall = " AND swdlo.domain_name = %(domain)s"
swdlo_delivery_st_sq = " AND upper(swdlo.delivery_state) = upper(%s)"

INCLUDE_CATEGORY_FLAG = os.getenv('INCL_CAT_SCAT')
LOGISTICS_DISTRICT_TABLE = os.getenv('LOGISTICS_DISTRICT_TBL')

MONTHLY_DISTRICT_TABLE = os.getenv('MONTHLY_DISTRICT_TBL')
CAT_MONTHLY_DISTRICT_TABLE = os.getenv('CAT_MONTHLY_DISTRICT_TBL')
SUB_CAT_MONTHLY_DISTRICT_TABLE = os.getenv('SUB_CAT_MONTHLY_DISTRICT_TBL')
MONTHLY_PROVIDERS = os.getenv('MONTHLY_PROVIDERS_TBL')
TOTAL_ACTIVE_SELLER_TBL = os.getenv('TOTAL_ACTIVE_SELLER_TBL')
TOTAL_ACTIVE_SELLER_CAT_SUBCAT_TBL = os.getenv('TOTAL_ACTIVE_SELLER_CAT_SUBCAT_TBL')
LOGISTICS_MONTHLY_PROVIDERS = os.getenv('LOGISTICS_MONTHLY_PROVIDERS_TBL')

download_table_col_reference = {
    'avg_items': 'Average Items per Order',
    'intradistrict': 'Intradistrict Orders Percentage',
    'intrastate': 'Intrastate Orders Percentage',
    'items': 'Total Confirmed Items',
    'orders': 'Confirmed Orders'
}

CACHE_EXPIRY = int(os.getenv('CACHE_EXPIRY'))

LANDING_PAGE_ECHART_TABLE = os.getenv('LANDING_PAGE_ECHART_TABLE')
LANDING_PAGE_ECHART_CONFIG = os.getenv('LANDING_PAGE_ECHART_CONFIG')
LANDING_PAGE_ECHART_DATA_TILL = os.getenv('LANDING_PAGE_ECHART_DATA_TILL')

LOGISTIC_SEARCH_TBL = os.getenv('LOGISTIC_SEARCH_TBL')
LOGISTIC_SEARCH_PINCODE_TBL = os.getenv('LOGISTIC_SEARCH_PINCODE_TBL')
ACTIVE_TOTAL_SELLER_TBL = os.getenv('ACTIVE_TOTAL_SELLERS_TABLE')

# INSIGHTS_FOLDER_DIR = os.getenv('INSIGHTS_FOLDER_DIR', '/app/webapp/KEY_DATA_INSIGHTS/')
INSIGHTS_FOLDER_DIR = '/app/Webapp/KEY_DATA_INSIGHTS/'


INSIGHTS_MAP = {
    "active_sellers_location": 1,
    "active_total_sellers_category": 1,
    "active_total_sellers_national": 1,
    "active_total_sellers_state_sep": 1,
    "qsr_distribution": 1,
    "flow_orders_sellers": 1,
    "new_repeat_sellers_monthly": 1,
    "qsr_sellers_orders": 1,


    "active_sellers_daily": 0,
    "new_repeat_sellers": 0,
    "active_sellers_share_india": 0
}

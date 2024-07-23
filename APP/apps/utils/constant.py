import os

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
swdlo_domain_sub_query = " AND swdlo.domain_name = %s"
swdlo_domain_sub_query_overall = " AND swdlo.domain_name = %(domain)s"
swdlo_delivery_st_sq = " AND upper(swdlo.delivery_state) = upper(%s)"

INCLUDE_CATEGORY_FLAG = os.getenv('INCL_CAT_SCAT')
LOGISTICS_DISTRICT_TABLE = os.getenv('LOGISTICS_DISTRICT_TBL')

MONTHLY_DISTRICT_TABLE = os.getenv('MONTHLY_DISTRICT_TBL')
MONTHLY_PROVIDERS = os.getenv('MONTHLY_PROVIDERS_TBL')
LOGISTICS_MONTHLY_PROVIDERS = os.getenv('LOGISTICS_MONTHLY_PROVIDERS_TBL')

download_table_col_reference = {
    'avg_items': 'Average Items per Order',
    'intradistrict': 'Intradistrict Orders Percentage',
    'intrastate': 'Intrastate Orders Percentage',
    'items': 'Total Confirmed Items',
    'orders': 'Confirmed Orders'
}
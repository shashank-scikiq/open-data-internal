__author__ = "Shashank Katyayan"
from rest_framework.views import APIView
import apps.utils.constant as constant
from datetime import datetime
import pandas as pd
from apps.logging_conf import log_function_call, ondcLogger
from decimal import Decimal
from dateutil.relativedelta import relativedelta

round_off_offset = 0

class SummaryBaseDataAPI(APIView):
    """
    This class handles the base data API.
    """

    
    @log_function_call(ondcLogger)
    def sunburst_format(self, category_penetration_df, chart_type):
        sunburst_data = {'total_data': {}}
        for index, row in category_penetration_df.iterrows():
            category = row['category']
            sub_category = row['sub_category']
            order_demand = int(row[chart_type])

            if category not in sunburst_data:
                sunburst_data[category] = {'children': [], 'value': 0}
            if sub_category == 'ALL':
                sunburst_data['total_data'][category] = {'value': order_demand}
            else:
                sunburst_data[category]['children'].append({'name': sub_category, 'value': order_demand})
                sunburst_data[category]['value'] += order_demand

        ids, labels, parents, values, percent = [], [], [], [], []

        total_value = sum(item['value'] for item in sunburst_data['total_data'].values())

        for category, data in sunburst_data.items():
            if category != 'total_data':
                category_id = category
                ids.append(category_id)
                labels.append(category)
                parents.append("")
                values.append(data['value'])
                if total_value != 0:
                    category_percentage = (sunburst_data['total_data'][category]['value'] / total_value) * 100
                else:
                    category_percentage = 0
                percent.append(round(category_percentage, 2))

                for sub_category in data.get('children', []):
                    sub_category_id = f"{category_id}-{sub_category['name']}"
                    ids.append(sub_category_id)
                    labels.append(sub_category['name'])
                    parents.append(category_id)
                    values.append(sub_category['value'])
                    if data['value'] != 0:
                        sub_category_percentage = (sub_category['value'] / data['value']) * 100
                    else:
                        sub_category_percentage = 0
                    percent.append(round(sub_category_percentage, 2))

        return {'ids': ids, 'labels': labels, 'parents': parents, 'values': values, 'percent': percent}



    @log_function_call(ondcLogger)
    def extract_common_params(self, request):
        start_date = request.query_params.get('startDate', None)
        if start_date is None:
            start_date = request.query_params.get('start_date', None)

        start_date = constant.FIXED_MIN_DATE if (datetime.strptime(start_date, "%Y-%m-%d").date()
                                                 < datetime.strptime(constant.FIXED_MIN_DATE,
                                                                     "%Y-%m-%d").date()) else start_date

        end_date = request.query_params.get('endDate', None)
        if end_date is None:
            end_date = request.query_params.get('end_date', None)
        
        category = request.query_params.get('category', None)
        if category in ('undefined', 'all', 'None', 'All'):
            category = None
        else:
            category = category.replace("'", "''")
        sub_category = request.query_params.get('subCategory', None)
        if sub_category in ('undefined', 'all', 'All', 'None', 'Select Sub-Category'):
            sub_category = None
        else:
            sub_category = sub_category.replace("'", "''")

        domain_name = request.query_params.get('domainName', None)
        if domain_name == 'None' or domain_name == 'undefined' or domain_name == 'null':
            domain_name = 'Retail'

        state = request.query_params.get('state', None)
        if state == 'None' or state == 'undefined' or state == 'null':
            state = None
        
        seller_type = request.query_params.get('sellerType', 'Total')


        return {
            "start_date": start_date,
            "end_date": end_date,
            "domain_name": domain_name,
            "state": state,
            "category": category,
            "sub_category": sub_category,
            "seller_type": seller_type
        }


    @log_function_call(ondcLogger)
    def top_chart_format(self, df: pd.DataFrame, chart_type):
        if df.empty:
            return {}

        df['order_date'] = df['order_month'].astype(int).apply(lambda x: f"{x:02}") + '-' + df['order_year'].astype(
            int).astype(str)
        if not pd.api.types.is_datetime64_any_dtype(df['order_date']):
            df['order_date'] = pd.to_datetime(df['order_date'])
        df['total_orders_delivered'] = pd.to_numeric(df['total_orders_delivered'], errors='coerce')

        formatted_data = {
            "series": [],
            "categories": df['order_date'].dt.strftime('%b-%y').unique().tolist()
        }
        if chart_type == 'cumulative':
            formatted_data["series"].append({
                "name": "India",
                "data": df['total_orders_delivered'].tolist()
            })
        else:
            for state in df[chart_type].unique():
                if state == '' or state == 'Missing':
                    continue
                state_data = {
                    "name": state,
                    "data": df[df[chart_type] == state]['total_orders_delivered'].tolist()
                }
                formatted_data["series"].append(state_data)

        return formatted_data

    @log_function_call(ondcLogger)
    def top_seller_chart_format(self, df: pd.DataFrame, chart_type):
        if df.empty:
            return {}

        df['order_date'] = df['order_month'].astype(int).apply(lambda x: f"{x:02}") + '-' + df['order_year'].astype(
            int).astype(str)
        if not pd.api.types.is_datetime64_any_dtype(df['order_date']):
            df['order_date'] = pd.to_datetime(df['order_date'])
        df['active_sellers_count'] = pd.to_numeric(df['active_sellers_count'], errors='coerce')

        formatted_data = {
            "series": [],
            "categories": df['order_date'].dt.strftime('%b-%y').unique().tolist()
        }
        if chart_type == 'cumulative':
            formatted_data["series"].append({
                "name": "India",
                "data": df['active_sellers_count'].tolist()
            })
        else:
            for state in df[chart_type].unique():
                if state == '' or state == 'Missing':
                    continue
                state_data = {
                    "name": state,
                    "data": df[df[chart_type] == state]['active_sellers_count'].tolist()
                }
                formatted_data["series"].append(state_data)

        return formatted_data

    @log_function_call(ondcLogger)
    def top_chart_hyperlocal_format(self, df: pd.DataFrame, chart_type):
        if df.empty:
            return {}

        df['order_date'] = df['order_month'].astype(int).apply(lambda x: f"{x:02}") + '-' + df['order_year'].astype(
            int).astype(str)
        if not pd.api.types.is_datetime64_any_dtype(df['order_date']):
            df['order_date'] = pd.to_datetime(df['order_date'])
        df['intrastate_orders_percentage'] = pd.to_numeric(df['intrastate_orders_percentage'], errors='coerce')
        formatted_data = {
            "series": [],
            "categories": df['order_date'].dt.strftime('%b-%y').unique().tolist()
        }
        for state in df[chart_type].unique():
            if state == '' or state == 'Missing':
                continue
            state_data = {
                "name": state,
                "data": df[df[chart_type] == state]['intrastate_orders_percentage'].tolist()
            }
            formatted_data["series"].append(state_data)
        return formatted_data

    @log_function_call(ondcLogger)
    def zonal_commerce_format(self, zonal_commerce_df: pd.DataFrame, tree_type: str):
        ROUND_OFF_PRECISION = 0
        round_off_chart_offset = f".{ROUND_OFF_PRECISION}f"
        from_area = 'seller_state'
        if tree_type == 'delivery_district':
            from_area = 'seller_district'
        elif tree_type== 'seller_district':
            from_area = 'delivery_district'
        state_data = {}
        for state in zonal_commerce_df[tree_type].unique():
            state_data = {
                "name": state,
                "children": []
            }
            cumulative_percentage = 0.0
            state_orders = zonal_commerce_df[zonal_commerce_df[tree_type] == state]
            for index, row in state_orders.iterrows():
                cumulative_percentage += float(row['flow_percentage'])

                seller_state_data = {
                    "name": f"{row[from_area]} ({row['flow_percentage']:.2f} %)",
                    "value": row['order_demand']
                }
                state_data["children"].append(seller_state_data)

            if cumulative_percentage < 100.0:
                others_data = {
                    "name": f"Others ({100 - cumulative_percentage:.2f} %)",
                    "value": 100 - cumulative_percentage
                }
                state_data["children"].append(others_data)

        return state_data

    @log_function_call(ondcLogger)
    def calculate_delta_percentage(self, current_value, previous_value):
        if previous_value == 0:
            return str(0)

        return round(((float(current_value) - float(previous_value)) / float(previous_value)) * 100, round_off_offset)

    @log_function_call(ondcLogger)
    def map_state_data_format(self, map_state_df: pd.DataFrame, active_sellers_data_total):
        map_state_df['delivery_district'] = map_state_df['delivery_district'].fillna('Unknown').str.upper()
        map_state_df['delivery_state_code'] = map_state_df['delivery_state_code'].fillna('Unknown')
        map_state_df['intrastate_orders'] = map_state_df['intrastate_orders'].astype('float')
        map_state_df['intradistrict_orders'] = map_state_df['intradistrict_orders'].astype('float')

        result = {}

        state_codes = []
        if active_sellers_data_total is not None and not active_sellers_data_total.empty:
            state_codes = list(set(active_sellers_data_total['seller_state_code']).union(set(map_state_df['delivery_state_code'])))
        else: 
            state_codes = list(set(map_state_df['delivery_state_code']))

        

        for state_code in state_codes:
            state_df = map_state_df[map_state_df['delivery_state_code'] == state_code]
            state_data = result.setdefault(state_code, {'districts': {}, 'total': {}})
            for district in state_df['delivery_district'].unique():
                district_df = state_df[state_df['delivery_district'] == district]
                total_orders_delivered = district_df['total_orders_delivered'].sum()
                # total_active_sellers = district_df['active_sellers_count'].sum()
                total_intradistrict_orders = district_df['intradistrict_orders'].sum()
                intradistrict_percentage = float(float(total_intradistrict_orders) * 100 / float(
                    total_orders_delivered)) if total_orders_delivered else 0
                total_intrastate_orders = district_df['intrastate_orders'].sum()
                intrastate_percentage = float(float(total_intrastate_orders) * 100 / float(
                    total_orders_delivered)) if total_orders_delivered else 0
                district_data = {
                    'order_demand': int(total_orders_delivered),
                    'intradistrict_percentage': round(intradistrict_percentage, round_off_offset),
                    'intrastate_percentage': round(intrastate_percentage, round_off_offset),
                    'active_sellers': int(0)
                }
                state_data['districts'][district] = district_data

            state_data['total'] = {
                'order_demand': int(state_df['total_orders_delivered'].sum()),
                'intradistrict_percentage': round(
                    float(100 * state_df['intradistrict_orders'].sum() / state_df['total_orders_delivered'].sum()),
                    round_off_offset) if
                state_df['total_orders_delivered'].sum() else 0,
                'intrastate_percentage': round(
                    float(state_df['intrastate_orders'].sum() * 100 / state_df['total_orders_delivered'].sum()),
                    round_off_offset) if
                state_df['total_orders_delivered'].sum() else 0,
                # 'active_sellers': int(state_df['active_sellers_count'].sum())
                'active_sellers': int(
                    active_sellers_data_total[active_sellers_data_total['seller_state_code'] == state_code][
                        'active_sellers_count'].sum()) if active_sellers_data_total is not None else 0
            }

        return result

    @log_function_call(ondcLogger)
    def map_state_wise_data_format(self, df):
        result = {
            "cases_time_series": [],
            "statewise": []
        }

        for row in df.itertuples():
            confirmed_orders = float(row.total_orders) if isinstance(row.total_orders, Decimal) else row.total_orders
            active_sellers = float(row.active_sellers_count) if isinstance(row.active_sellers_count,
                                                                           Decimal) else row.active_sellers_count
            intrastate_orders = float(row.intrastate_orders) if row.intrastate_orders else 0
            intradistrict_orders = float(row.intradistrict_orders) if row.intradistrict_orders else 0
            if row.delivery_state_code != 0:
                state_data = {
                    'state': row.delivery_state,
                    'statecode': row.delivery_state_code,
                    'confirmed_orders': confirmed_orders,
                    'order_demand': int(confirmed_orders),
                    'active_sellers': int(active_sellers),
                    'intrastate_orders_percentage': round((intrastate_orders * 100 / confirmed_orders),
                                                          round_off_offset) if confirmed_orders else 0,
                    'intradistrict_orders_percentage': round((intradistrict_orders * 100 / confirmed_orders),
                                                             round_off_offset) if confirmed_orders else 0,
                }
                result['statewise'].append(state_data)

        return result
    
    @log_function_call(ondcLogger)
    def state_bin_data_format(self, df: pd.DataFrame, chart_type: str, **kwargs):
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        date_difference = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days + 1

        bin_edges = [0, 1000, 5000, 10000, float('inf')]
        bin_label_1 = "< 1,000"
        bin_label_2 = "1,000 - 5,000"
        bin_label_3 = "5,000 - 10,000"
        bin_label_4 = "> 10,000"
        bin_labels = [bin_label_1, bin_label_2, bin_label_3, bin_label_4]

        if chart_type not in df.columns:
            raise ValueError(f"{chart_type} is not a valid column in the DataFrame")

        df['daily_order_demand'] = df[chart_type] / date_difference
        df['bin'] = pd.cut(df['daily_order_demand'], bins=bin_edges, labels=bin_labels, right=False)
        bins = {label: [] for label in bin_labels}

        for label in bin_labels:
            bins[label] = [' ' + state.title() for state in df[df['bin'] ==
                                                               label]['delivery_state'].unique()]

        return bins


def shift_date_months(start_date_str, end_date_str, months=-1):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    new_start_date = start_date + relativedelta(months=months)
    new_end_date = end_date + relativedelta(months=months)
    return new_start_date.strftime("%Y-%m-%d"), new_end_date.strftime("%Y-%m-%d")

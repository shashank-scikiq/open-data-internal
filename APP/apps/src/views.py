from rest_framework.viewsets import ViewSet
from apps.utils import constant
from datetime import datetime
import pandas as pd


class BaseViewSet(ViewSet):

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

        district = request.query_params.get('district_name', None)

        params = {
            'start_date': start_date,
            'end_date': end_date,
            'domain_name': domain_name,
            'state': state,
            'category': category,
            'sub_category': sub_category,
            'seller_type': seller_type
        }
        if not(district == 'None' or district == 'undefined'):
            params['district'] = district


        return params

    def format_order_chart(self, df, params, chart_type=None):
        if df.empty:
            return {}

        df['order_date'] = pd.to_datetime(
            df['order_month'].astype(str).str.zfill(2) + '-' + df['order_year'].astype(str), errors='coerce'
        )
        df['total_orders_delivered'] = pd.to_numeric(df['total_orders_delivered'], errors='coerce')

        formatted_data = {
            "series": [],
            "categories": df['order_date'].dt.strftime('%b-%y').unique().tolist()
        }

        if chart_type == 'cumulative':
            formatted_data["series"].append({
                "name": "India" if params['state'] is None else params['state'],
                "data": df['total_orders_delivered'].tolist()
            })
        else:
            for state in df[chart_type].dropna().unique():
                if state in ('', 'Missing'):
                    continue
                state_data = {
                    "name": state,
                    "data": df[df[chart_type] == state]['total_orders_delivered'].tolist()
                }
                formatted_data["series"].append(state_data)

        return formatted_data

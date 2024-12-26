from rest_framework.decorators import action
import pandas as pd
import numpy as np
from datetime import datetime

from apps.utils.helpers import is_delta_required, get_previous_date_range
from apps.utils.decorator import api_decorator as decorator
from apps.utils import constant
from apps.src.views import BaseViewSet
from apps.src.database_utils.dal_logistics_overall import LogisticsDataAccessLayer

top_card_tooltip_text = {
    "Total Orders": 'Count of Distinct Network Order Id within the selected range.',
    "Districts":  'Unique count of Districts where orders has been delivered in the latest month within the date range. Districts are fetched using districts mapping using End pincode',
    "records the highest order count": 'Maximum Orders by State/Districts, basis the date range. It will show top districts within a state if a state map is selected. Districts are mapped using delivery pincode.'
}

class LogisticsViewset(BaseViewSet):
    access_layer = LogisticsDataAccessLayer()

    def prepare_params(self, request):
        params = self.extract_common_params(request)
        params['domain_name'] = 'Logistics'
        return params
    
    def prepare_missing_data(self, order_df, calc_most_ordering_district=True):
        state_level_data = (
            order_df.groupby(["delivery_state_code", "delivery_state"], as_index=False)
            .agg(
                total_districts=("delivery_district", "count"),
                delivered_orders=("total_orders_in_district", "sum")
            )
        )
        
        if calc_most_ordering_district:
            most_ordering_district = (
                order_df.loc[order_df.groupby(
                    ["delivery_state_code", "delivery_state"]
                )["total_orders_in_district"].idxmax()]
                [["delivery_state_code", "delivery_state", "delivery_district"]]
                .rename(columns={"delivery_district": "most_ordering_district"})
            )
            most_ordering_district.reset_index(drop=True, inplace=True)

            state_level_data = pd.merge(
                state_level_data,
                most_ordering_district,
                on=["delivery_state_code", "delivery_state"]
            )

        state_level_data = state_level_data.fillna(0)

        total_row = pd.DataFrame({
            'delivery_state_code': ['TT'],
            'delivery_state': ['TOTAL'],
            'total_districts': [state_level_data['total_districts'].sum()],
            'delivered_orders': [state_level_data['delivered_orders'].sum()],
            'most_ordering_district': [state_level_data.loc[state_level_data['delivered_orders'].idxmax(), 'delivery_state']]
        })
        state_level_data = pd.concat([state_level_data, total_row], ignore_index=True)

        return state_level_data

    def transform_top_card_data(self, current_df, previous_df=pd.DataFrame()):
        previous_state_level_data = pd.DataFrame()
        current_state_level_data = self.prepare_missing_data(current_df)

        # For previous date range
        if not previous_df.empty:
            previous_state_level_data = self.prepare_missing_data(previous_df, False)
        return current_state_level_data, previous_state_level_data
    
    def fetch_top_card_data(self, params):
        current_data = self.access_layer.fetch_district_level_order_summary(**params)

        delta_required = is_delta_required(params)
        if delta_required:
            previous_start_date, previous_end_date = get_previous_date_range(params)
            params.update({'start_date': previous_start_date, 'end_date': previous_end_date})
            previous_data = self.access_layer.fetch_district_level_order_summary(**params)
        else:
            previous_data = pd.DataFrame()
        
        current_data, previous_data = self.transform_top_card_data(
            current_data, previous_data
        )
        previous_data = previous_data.drop(columns=['most_ordering_district']) if not previous_data.empty \
            else current_data.drop(columns=['most_ordering_district'])

        return current_data, previous_data

    def merge_and_clean_data(self, current_data, previous_data):
        merged_data = pd.merge(
            current_data, previous_data,
            on='delivery_state', suffixes=('_current', '_previous'),
            how='outer', validate="many_to_many"
        )
        return self.clean_and_prepare_data(merged_data)

    def clean_and_prepare_data(self, merged_df):
        fill_values = {
            'most_ordering_district': constant.NO_DATA_MSG,
            'delivery_state_code_current': 'TT',
            'delivery_state': 'TOTAL',
            np.inf: 100, -np.inf: 100, np.nan: 0
        }
        merged_df = merged_df.fillna(fill_values)
        
        delta_columns = [
            ('total_districts', 'district_count_delta'),
            ('delivered_orders', 'orders_count_delta')
        ]
        for value, delta in delta_columns:
            merged_df[delta] = np.where(
                merged_df[f'{value}_previous'].astype(float) == 0,
                0,
                (merged_df[f'{value}_current'] - merged_df[f'{value}_previous']).astype(float)*100.0/
                    merged_df[f'{value}_previous'].astype(float)
            ).round(constant.ROUND_OFF_DIGITS)
        
        drop_columns = [
            'delivered_orders_previous', 'total_districts_previous',
            'delivery_state_code_previous'
        ]
        merged_df = merged_df.drop(columns=drop_columns).fillna(0)
        return merged_df.copy()

    def build_response_data(self, merged_df, params):
        top_card_data = {}
        state_list = pd.DataFrame({
            "delivery_state_code_current": constant.STATE_CODES.keys(),
            "delivery_state": constant.STATE_CODES.values()
        })

        merged_df = pd.merge(state_list, merged_df, how='left', on=["delivery_state_code_current", "delivery_state"])
        merged_df = merged_df.fillna(0)

        for _, row in merged_df.iterrows():
            state_code = row['delivery_state_code_current']
            top_card_data[state_code] = self.build_state_metrics(row)
        return {
            "prev_date_range": self.format_previous_date_range(params),
            "tooltip_text": top_card_tooltip_text,
            "top_card_data": top_card_data
        }

    def build_state_metrics(self, row):
        metrics = [
            self.create_metric_data(row['delivered_orders_current'], 'Total Orders', row.get('orders_count_delta', 0)),
            self.create_metric_data(row['total_districts_current'], 'Districts', 0),
            self.create_max_orders_delivered_area_data(row["most_ordering_district"])
        ]
        return metrics

    def format_previous_date_range(self, params):
        prev_start_date, prev_end_date = params.get('start_date'), params.get('end_date')
        if prev_start_date and prev_end_date:
            date_format = '%b, %Y'
            prev_start_date_str = datetime.strptime(prev_start_date, '%Y-%m-%d').strftime(date_format)
            prev_end_date_str = datetime.strptime(prev_end_date, '%Y-%m-%d').strftime(date_format)
            return f"Vs {prev_start_date_str}" if prev_start_date_str == prev_end_date_str else f"Vs {prev_start_date_str} - {prev_end_date_str}"
        return " "

    def create_metric_data(self, count, heading, delta, count_suffix=''):
        return {
            "type": 'default',
            "count": f"{count}{count_suffix}" if count_suffix else count,
            "heading": heading,
            "icon": 'trending_up' if delta >= 0 else 'trending_down',
            "positive": delta >= 0,
            "percentageCount": float("{:.2f}".format(delta)),
            "showVarience": bool(delta)
        }

    def create_max_orders_delivered_area_data(self, most_ordering_district):
        return {
            "type": 'max_state',
            "heading": 'records the highest order count',
            "mainText": str(most_ordering_district)
        }
    
    @action(detail=False, methods=['get'], url_path='top_card_delta')
    @decorator()
    def get_top_card_delta(self, request):
        params = self.prepare_params(request)
        current_data, previous_data = self.fetch_top_card_data(params)
        merged_data = self.merge_and_clean_data(current_data, previous_data)

        top_cards_data = self.build_response_data(
            merged_data, params
        )
        return top_cards_data
    
    @action(detail=False, methods=['get'], url_path='top_seller_states')
    @decorator()
    def get_interstate_coming_orders(self, request):
        params = self.prepare_params(request)
        order_df = self.access_layer.fetch_interstate_coming_orders(**params)

        if order_df.empty:
            return {}
        
        total_orders = order_df['order_demand'].sum()
        top_5_orders = order_df['order_demand'].nlargest(5).sum()

        top_5_order_df = order_df.head(5)
        top_5_order_df['percentage'] = np.where(
            total_orders == 0,
            0,
            (
                top_5_order_df['order_demand'].astype(float) *100.0 / 
                total_orders.astype(float)
            ).round(constant.ROUND_OFF_DIGITS)
        )

        total_row = pd.DataFrame({
            'seller_state': ['Others'],
            'delivery_state': [params['state']],
            'order_demand': [total_orders - top_5_orders],
            'percentage': [
                float(
                    ((total_orders - top_5_orders)*100.0) / total_orders
                ) if total_orders else 0
            ]
        })
        state_level_data = pd.concat([top_5_order_df, total_row], ignore_index=True)
        
        response_data = {
            'name': params['state'],
            'children': [
                {
                    'name': f"{i['seller_state']} ({round(float(i['percentage']), 2)}%)"
                } for i in state_level_data.to_dict(orient="records")
            ]
        }
        # import pdb; pdb.set_trace()
        return response_data
    
    @action(detail=False, methods=['get'], url_path='top_delivery_states')
    @decorator()
    def get_interstate_going_orders(self, request):
        params = self.prepare_params(request)
        order_df = self.access_layer.fetch_interstate_going_orders(**params)

        if order_df.empty:
            return {}
        total_orders = order_df['order_demand'].sum()
        top_5_orders = order_df['order_demand'].nlargest(5).sum()

        top_5_order_df = order_df.head(5)
        top_5_order_df['percentage'] = np.where(
            total_orders == 0,
            0,
            (
                top_5_order_df['order_demand'].astype(float) *100.0 / 
                total_orders.astype(float)
            ).round(constant.ROUND_OFF_DIGITS)
        )

        total_row = pd.DataFrame({
            'seller_state': [params['state']],
            'delivery_state': ['Others'],
            'order_demand': [total_orders - top_5_orders],
            'percentage': [
                float(
                    ((total_orders - top_5_orders)*100.0) / total_orders
                ) if total_orders else 0
            ]
        })
        state_level_data = pd.concat([top_5_order_df, total_row], ignore_index=True)
        
        response_data = {
            'name': params['state'],
            'children': [
                {
                    'name': f"{i['delivery_state']} ({round(float(i['percentage']), constant.ROUND_OFF_DIGITS)}%)"
                } for i in state_level_data.to_dict(orient="records")
            ]
        }

        return response_data

    @action(detail=False, methods=['get'], url_path='top_seller_districts')
    @decorator()
    def get_interdistrict_going_orders(self, request):
        params = self.prepare_params(request)
        order_df = self.access_layer.fetch_interdistrict_going_orders(**params)

        if order_df.empty:
            return {}
        
        total_orders = order_df['order_demand'].sum()
        top_5_orders = order_df['order_demand'].nlargest(5).sum()

        top_5_order_df = order_df.head(5)
        top_5_order_df['percentage'] = np.where(
            total_orders == 0,
            0,
            (
                top_5_order_df['order_demand'].astype(float) *100.0 / 
                total_orders.astype(float)
            ).round(constant.ROUND_OFF_DIGITS)
        )

        total_row = pd.DataFrame({
            'seller_district': [params['district']],
            'delivery_district': ['Others'],
            'order_demand': [total_orders - top_5_orders],
            'percentage': [
                float(
                    ((total_orders - top_5_orders)*100.0) / total_orders
                ) if total_orders else 0
            ]
        })
        district_level_data = pd.concat([top_5_order_df, total_row], ignore_index=True)
        
        response_data = {
            'name': params['district'],
            'children': [
                {
                    'name': f"{i['delivery_district']} ({round(float(i['percentage']), constant.ROUND_OFF_DIGITS)}%)"
                } for i in district_level_data.to_dict(orient="records")
            ]
        }

        return response_data

    @action(detail=False, methods=['get'], url_path='top_delivery_districts')
    @decorator()
    def get_interdistrict_coming_orders(self, request):
        params = self.prepare_params(request)
        order_df = self.access_layer.fetch_interdistrict_coming_orders(**params)

        if order_df.empty:
            return {}
        
        total_orders = order_df['order_demand'].sum()
        top_5_orders = order_df['order_demand'].nlargest(5).sum()

        top_5_order_df = order_df.head(5)
        top_5_order_df['percentage'] = np.where(
            total_orders == 0,
            0,
            (
                top_5_order_df['order_demand'].astype(float) *100.0 / 
                total_orders.astype(float)
            ).round(constant.ROUND_OFF_DIGITS)
        )

        total_row = pd.DataFrame({
            'seller_district': ['Others'],
            'delivery_district': [params['district']],
            'order_demand': [total_orders - top_5_orders],
            'percentage': [
                float(
                    ((total_orders - top_5_orders)*100.0) / total_orders
                ) if total_orders else 0
            ]
        })
        district_level_data = pd.concat([top_5_order_df, total_row], ignore_index=True)
        
        response_data = {
            'name': params['district'],
            'children': [
                {
                    'name': f"{i['seller_district']} ({round(float(i['percentage']), constant.ROUND_OFF_DIGITS)}%)"
                } for i in district_level_data.to_dict(orient="records")
            ]
        }
        return response_data
    
    @action(detail=False, methods=['get'], url_path='map_data')
    @decorator()
    def get_map_data(self, request):
        params = self.prepare_params(request)
        df = self.access_layer.fetch_district_level_order_summary_with_seller_state_info(**params)

        total_order_df = df.groupby(
            ['delivery_state_code', 'delivery_state', 'delivery_district'], as_index=False
        )['total_orders_in_district'].sum()
        total_order_df.rename(columns={'total_orders_in_district': 'total_order'}, inplace=True)

        # 2. Calculate `intrastate_orders` (sum of `total_orders_in_district` where delivery_state == seller_state)
        intrastate_df = df[df['delivery_state'] == df['seller_state']].groupby(
            ['delivery_state_code', 'delivery_state', 'delivery_district'], as_index=False
        )['total_orders_in_district'].sum()
        intrastate_df.rename(columns={'total_orders_in_district': 'intrastate_orders'}, inplace=True)

        # 3. Calculate `intradistrict_orders` (sum of `total_orders_in_district` where delivery_district == seller_district)
        intradistrict_df = df[df['delivery_district'] == df['seller_district']].groupby(
            ['delivery_state_code', 'delivery_state', 'delivery_district'], as_index=False
        )['total_orders_in_district'].sum()
        intradistrict_df.rename(columns={'total_orders_in_district': 'intradistrict_orders'}, inplace=True)

        # 4. Merge the results into a single DataFrame
        final_df = total_order_df.merge(intrastate_df, on=['delivery_state_code', 'delivery_state', 'delivery_district'], how='left')
        final_df = final_df.merge(intradistrict_df, on=['delivery_state_code', 'delivery_state', 'delivery_district'], how='left')

        # 5. Fill NaN values with 0 (for cases where no matching intrastate or intradistrict orders were found)
        final_df.fillna(0, inplace=True)

        state_level_agg = final_df.groupby(
            ['delivery_state_code', 'delivery_state'], as_index=False
        ).sum()

        # 2. Add the 'AGG' value for delivery_district
        state_level_agg['delivery_district'] = 'AGG'

        # 3. Append the aggregated rows to the original DataFrame
        final_df_with_agg = pd.concat([final_df, state_level_agg], ignore_index=True)

        # 4. Sort the DataFrame if needed
        final_df_with_agg.sort_values(by=['delivery_state_code', 'delivery_district'], inplace=True)


        final_df_with_agg['intrastate_orders'] = np.where(
            final_df_with_agg['total_order'] == 0,
            0,
            (
                final_df_with_agg['intrastate_orders'].astype(float)*100.0 / 
                final_df_with_agg['total_order'].astype(float)
            ).round(constant.ROUND_OFF_DIGITS)
        )
        final_df_with_agg['intradistrict_orders'] = np.where(
            final_df_with_agg['total_order'] == 0,
            0,
            (
                final_df_with_agg['intradistrict_orders'].astype(float)*100.0 / 
                final_df_with_agg['total_order'].astype(float)
            ).round(constant.ROUND_OFF_DIGITS)
        )

        response_data = final_df_with_agg.to_dict(orient="records")

        return response_data


    @action(detail=False, methods=['get'], url_path='top_cummulative_orders')
    @decorator()
    def get_top_cumulative_orders(self, request):
        params = self.prepare_params(request)
        data = self.access_layer.fetch_month_wise_orders_at_global_level(**params)

        merged_data = data.replace([np.nan], 0)
        chart_type = 'cumulative'
        
        formatted_data = self.format_order_chart(merged_data, params, chart_type)
        return formatted_data
    
    @action(detail=False, methods=['get'], url_path='top_state_orders')
    @decorator()
    def get_top_state_orders(self, request):
        params = self.prepare_params(request)
        data = self.access_layer.fetch_month_wise_orders_at_state_level(**params)
        merged_data = data.replace([np.nan], 0)

        values_to_drop = ['', 'Missing', 'MISSING']
        merged_data = merged_data[~merged_data['delivery_state'].isin(values_to_drop)]
        
        top_states = merged_data.groupby(
            ['delivery_state'], as_index=False
        ).agg(
            total_orders_delivered=('total_orders_delivered', 'sum')
        ).sort_values(by=['total_orders_delivered'], ascending=[False])[:3]['delivery_state'].unique()
        merged_data = merged_data[merged_data['delivery_state'].isin(top_states)]
        merged_data = merged_data.reset_index(drop=True)

        formatted_data = self.format_order_chart(merged_data, params, chart_type='delivery_state')
        return formatted_data
    
    @action(detail=False, methods=['get'], url_path='top_district_orders')
    @decorator()
    def get_top_district_orders(self, request):
        params = self.prepare_params(request)
        data = self.access_layer.fetch_month_wise_orders_at_district_level(**params)
        merged_data = data.replace([np.nan], 0)

        values_to_drop = ['', 'Missing', 'MISSING']
        merged_data = merged_data[~merged_data['delivery_district'].isin(values_to_drop)]

        top_districts = merged_data.groupby(
            ['delivery_district'], as_index=False
        ).agg(
            total_orders_delivered=('total_orders_delivered', 'sum')
        ).sort_values(by=['total_orders_delivered'], ascending=[False])[:3]['delivery_district'].unique()
        merged_data = merged_data[merged_data['delivery_district'].isin(top_districts)]
        merged_data = merged_data.reset_index(drop=True)

        formatted_data = self.format_order_chart(merged_data, params, chart_type='delivery_district')
        return formatted_data

    

    @action(detail=False, methods=['get'], url_path='top_state_hyperlocal')
    @decorator()
    def get_top_state_hyperlocal(self, request):
        params = self.prepare_params(request)
        data = self.access_layer.fetch_month_wise_hyperlocal_orders_at_state_level(**params)
        merged_data = data.replace([np.nan], 0)
        values_to_drop = ['', 'Missing', 'MISSING']
        merged_data = merged_data[~merged_data['delivery_state'].isin(values_to_drop)]

        top_states = merged_data.groupby(
            ['delivery_state'], as_index=False
        ).agg(
            total_orders_delivered=('intrastate_orders_total', 'sum')
        ).sort_values(by=['total_orders_delivered'], ascending=[False])[:3]['delivery_state'].unique()
        merged_data = merged_data[merged_data['delivery_state'].isin(top_states)]

        merged_data['intrastate_orders_percentage'] = np.where(
            merged_data['total_orders_delivered'] == 0, 
            0 , 
            (merged_data['intrastate_orders_total']*100.0)/merged_data['total_orders_delivered']
        ).round(constant.ROUND_OFF_DIGITS)
        merged_data = merged_data.reset_index(drop=True)
        
        formatted_data = self.format_hyperlocal_chart(merged_data, params, chart_type='delivery_state')
        return formatted_data
    
    @action(detail=False, methods=['get'], url_path='top_district_hyperlocal')
    @decorator()
    def get_top_district_hyperlocal(self, request):
        params = self.prepare_params(request)
        data = self.access_layer.fetch_month_wise_hyperlocal_orders_at_district_level(**params)
        merged_data = data.replace([np.nan], 0)
        values_to_drop = ['', 'Missing', 'MISSING']
        merged_data = merged_data[~merged_data['delivery_district'].isin(values_to_drop)]

        top_districts = merged_data.groupby(
            ['delivery_district'], as_index=False
        ).agg(
            total_orders_delivered=('intradistrict_orders', 'sum')
        ).sort_values(by=['total_orders_delivered'], ascending=[False])[:3]['delivery_district'].unique()
        merged_data = merged_data[merged_data['delivery_district'].isin(top_districts)]

        merged_data['intrastate_orders_percentage'] = np.where(
            merged_data['total_orders_delivered'] == 0, 
            0 , 
            (merged_data['intradistrict_orders']*100.0)/merged_data['total_orders_delivered']
        ).round(constant.ROUND_OFF_DIGITS)
        merged_data = merged_data.reset_index(drop=True)

        formatted_data = self.format_hyperlocal_chart(merged_data, params, chart_type='delivery_district')
        return formatted_data

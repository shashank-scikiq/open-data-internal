__author__ = "Shashank Katyayan"

import asyncio
import logging
from apps.src.database_utils.ClsBaseMetrics import Metric
from apps.utils import constant
from datetime import datetime
from datetime import datetime
from django.db.models import Sum, F, Q, Window
from django.db.models.functions import Coalesce, Trim, RowNumber
from django.db.models import Value as V
from apps.logistics_all.logistics_all_app.models import DistrictWiseMonthlyAggregate
import pandas as pd
from django.db.models import Q, Sum, Window, F, Value as V, Subquery, OuterRef
from django.db.models.functions import RowNumber, Coalesce, Trim
import pandas as pd
from datetime import datetime
from django.db import models

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZonalCommerceMetric(Metric):

    def __init__(self, db_utility):
        self.db_utility = db_utility

    def run(self, start_date, end_date, **kwargs):
        self.top_card_delta(start_date, end_date, **kwargs)

    def top_card_delta(self, start_date, end_date, **kwargs):
        logger.info("Computing Zonal Commerce Metric: Top Card Delta")
        # Simulate computation
        logger.info("Completed Zonal Commerce Metric: Top Card Delta")

    def map_state_data(self, start_date, end_date, **kwargs):
        logger.info("Computing Zonal Commerce Metric: Map State Data")
        # Simulate computation
        logger.info("Completed Zonal Commerce Metric: Map State Data")

    def map_statewise_data(self, start_date, end_date, **kwargs):
        logger.info("Computing Zonal Commerce Metric: Map Statewise Data")
        # Simulate computation
        logger.info("Completed Zonal Commerce Metric: Map Statewise Data")

    def top_cumulative_chart(self, start_date, end_date, **kwargs):
        logger.info("Computing Zonal Commerce Metric: Top Cumulative Chart")
        # Simulate computation
        logger.info("Completed Zonal Commerce Metric: Top Cumulative Chart")

    # def top_states_chart(self, start_date, end_date, **kwargs):
    #     logger.info("Computing Zonal Commerce Metric: Top States Chart")
    #     # Simulate computation
    #     logger.info("Completed Zonal Commerce Metric: Top States Chart")

    # def top_district_chart(self, start_date, end_date, **kwargs):
    #     logger.info("Computing Zonal Commerce Metric: Top District Chart")
    #     # Simulate computation
    #     logger.info("Completed Zonal Commerce Metric: Top District Chart")

    # def tree_chart(self, start_date, end_date, **kwargs):
    #     logger.info("Computing Zonal Commerce Metric: Tree Chart")
    #     # Simulate computation
    #     logger.info("Completed Zonal Commerce Metric: Tree Chart")

    def top_states_chart(self, start_date, end_date, category=None, sub_category=None,
                                                   domain_name=None, state=None):
        selected_view = constant.MONTHLY_DISTRICT_TABLE
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        end_month = edate_obj.month
        start_year = stdate_obj.year
        end_year = edate_obj.year

        parameters = [start_year, start_year, start_month, end_year, end_year, end_month]

        base_query = f"""
            WITH TopStates AS (
                SELECT 
                    COALESCE(delivery_state, 'MISSING') AS delivery_state,
                    SUM(total_orders_delivered) AS total_orders_delivered,
                    SUM(intrastate_orders) AS intrastate_orders_total,
                    ROUND(SUM(intrastate_orders::numeric) / NULLIF(SUM(total_orders_delivered::numeric), 0), 2) * 100 AS intrastate_orders_percentage
                FROM 
                    {selected_view}
                WHERE 
                    (order_year > %s OR (order_year = %s AND order_month >= %s))
                    AND (order_year < %s OR (order_year = %s AND order_month <= %s))
                    AND delivery_state != 'MISSING'
        """

        if domain_name:
            base_query += " AND domain_name = %s"
            parameters.append(domain_name)

        if state:
            base_query += " AND upper(delivery_state) = upper(%s)"
            parameters.append(state)

        base_query += f"""
                GROUP BY 
                    delivery_state
                ORDER BY 
                    intrastate_orders_percentage DESC
                LIMIT 3
            ),
            FinalResult AS (
                SELECT 
                    om.order_month AS order_month,
                    om.order_year AS order_year,
                    COALESCE(om.delivery_state, 'MISSING') AS delivery_state,
                    SUM(om.total_orders_delivered) AS total_orders_delivered,
                    ROUND(SUM(om.intrastate_orders::numeric) / NULLIF(SUM(om.total_orders_delivered::numeric), 0), 2) * 100 AS intrastate_orders_percentage
                FROM 
                    {selected_view} om
                INNER JOIN 
                    TopStates ts ON COALESCE(om.delivery_state, 'MISSING') = ts.delivery_state
                WHERE 
                    (om.order_year > %s OR (om.order_year = %s AND om.order_month >= %s))
                    AND (om.order_year < %s OR (om.order_year = %s AND om.order_month <= %s))
        """

        parameters.extend([start_year, start_year, start_month, end_year, end_year, end_month])

        if domain_name:
            base_query += " AND om.domain_name = %s"
            parameters.append(domain_name)

        if state:
            base_query += " AND upper(om.delivery_state) = upper(%s)"
            parameters.append(state)

        base_query += """
                GROUP BY 
                    om.order_month, om.order_year, om.delivery_state
                ORDER BY 
                    om.order_year, om.order_month, intrastate_orders_percentage DESC
            )
            select * from FinalResult
        """

        base_query = base_query.format(selected_view=selected_view)
        df = self.db_utility.execute_query(base_query, parameters)

        return df

    def top_district_chart(self, start_date, end_date, category=None, sub_category=None,
                                                     domain_name=None, state=None):

        selected_view = constant.MONTHLY_DISTRICT_TABLE
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        end_month = edate_obj.month
        start_year = stdate_obj.year
        end_year = edate_obj.year

        parameters = {
            'start_month': start_month,
            'start_year': start_year,
            'end_month': end_month,
            'end_year': end_year
        }

        base_query = f"""
            WITH TopDistricts AS (
                SELECT 
                    delivery_district,
                    SUM(total_orders_delivered) AS total_order_demand,
                    SUM(intradistrict_orders) AS intradistrict_orders,
                    ROUND((SUM(intradistrict_orders::numeric) / NULLIF(SUM(total_orders_delivered::numeric), 0)), 2) * 100 AS intradistrict_percentage
                FROM 
                    {selected_view}
                WHERE 
                    (order_year > %(start_year)s OR (order_year = %(start_year)s AND order_month >= %(start_month)s))
                    AND (order_year < %(end_year)s OR (order_year = %(end_year)s AND order_month <= %(end_month)s))
                    AND delivery_district <> '' AND UPPER(delivery_district) <> 'UNDEFINED'
                    AND delivery_district IS NOT NULL
        """

        if domain_name:
            base_query += " AND domain_name = %(domain_name)s"
            parameters['domain_name'] = domain_name

        if state:
            base_query += " AND upper(delivery_state) = upper(%(state)s)"
            parameters['state'] = state

        base_query += f"""
                GROUP BY 
                    delivery_district
                ORDER BY 
                    intradistrict_percentage DESC
                LIMIT 3
            ),
            FinalResult AS (
                SELECT 
                    om.order_month AS order_month,
                    om.order_year AS order_year,
                    om.delivery_district AS delivery_district,
                    SUM(om.total_orders_delivered) AS total_orders_delivered,
                    SUM(om.intradistrict_orders) AS intradistrict_orders,
                    ROUND((SUM(om.intradistrict_orders::numeric) / NULLIF(SUM(om.total_orders_delivered::numeric), 0)), 2) * 100 AS intrastate_orders_percentage
                FROM 
                    {selected_view} om
                INNER JOIN 
                    TopDistricts td ON om.delivery_district = td.delivery_district
                WHERE 
                    (om.order_year > %(start_year)s OR (om.order_year = %(start_year)s AND om.order_month >= %(start_month)s))
                    AND (om.order_year < %(end_year)s OR (om.order_year = %(end_year)s AND om.order_month <= %(end_month)s))
        """

        if domain_name:
            base_query += " AND om.domain_name = %(domain_name)s"

        if state:
            base_query += " AND upper(om.delivery_state) = upper(%(state)s)"

        base_query += """
                GROUP BY 
                    om.order_month, om.order_year, om.delivery_district
                ORDER BY 
                    om.order_year, om.order_month, intrastate_orders_percentage DESC
            )
            SELECT * FROM FinalResult;
        """

        base_query = base_query.format(selected_view=selected_view)
        df = self.db_utility.execute_query(base_query, parameters)

        return df

    # from datetime import datetime
    # from django.db.models import Q, Sum, F, Window, RowNumber, Subquery, Value as V
    # from django.db.models.functions import Coalesce, Trim
    # import pandas as pd

    def state_tree_chart(self, start_date, end_date, category=None, sub_category=None, domain_name=None, state=None):
        # Convert string to datetime object
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        start_year = stdate_obj.year
        end_month = edate_obj.month
        end_year = edate_obj.year

        # Define base filters
        filters = (
                (Q(order_year__gt=start_year) | (Q(order_year=start_year) & Q(order_month__gte=start_month))) &
                (Q(order_year__lt=end_year) | (Q(order_year=end_year) & Q(order_month__lte=end_month))) &
                Q(delivery_state__iexact='Maharashtra')  # Case-insensitive exact match for 'Maharashtra'
        )

        if state:
            filters &= Q(delivery_state__iexact=state.upper())  # Case-insensitive exact match for provided state

        if domain_name:
            filters &= Q(domain_name=domain_name)

        # Subquery to calculate total orders per delivery state (Maharashtra)
        total_orders_subquery = DistrictWiseMonthlyAggregate.objects.filter(
            delivery_state__iexact='Maharashtra'
        ).filter(
            filters
        ).values('delivery_state').annotate(
            total_orders=Sum('total_orders_delivered')
        ).values('total_orders')

        # Main query to get top 5 seller states per delivery state
        main_query = DistrictWiseMonthlyAggregate.objects.filter(
            filters
        ).annotate(
            seller_state_cleaned=Coalesce(Trim(F('seller_state')), V('Missing'))
        ).values(
            'delivery_state', 'seller_state_cleaned'
        ).annotate(
            order_demand=Sum('total_orders_delivered'),
            flow_percentage=(Sum('total_orders_delivered') * 100.0) / Subquery(total_orders_subquery)
        ).annotate(
            rn=Window(
                expression=RowNumber(),
                partition_by=F('delivery_state'),
                order_by=F('flow_percentage').desc()
            )
        ).filter(
            rn__lte=4
        ).order_by('-flow_percentage')

        # Convert queryset to DataFrame
        data = list(main_query)
        df = pd.DataFrame(data)
        df = df.rename(columns={'seller_state_cleaned': 'seller_state'})

        return df

    def district_tree_chart(self, start_date, end_date, category=None, sub_category=None, domain_name=None, state=None, district=None):
        # Convert string to datetime object
        stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
        edate_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Extract month and year
        start_month = stdate_obj.month
        start_year = stdate_obj.year
        end_month = edate_obj.month
        end_year = edate_obj.year

        # Define base filters
        filters = (
                (Q(order_year__gt=start_year) | (Q(order_year=start_year) & Q(order_month__gte=start_month))) &
                (Q(order_year__lt=end_year) | (Q(order_year=end_year) & Q(order_month__lte=end_month)))
        )

        if state:
            filters &= Q(delivery_state__iexact=state.upper())  # Case-insensitive exact match for provided state
        if district:
            filters &= Q(delivery_district__iexact=district.upper())  # Case-insensitive exact match for provided state

        if domain_name:
            filters &= Q(domain_name=domain_name)

        # Subquery to calculate total orders per delivery state (Maharashtra)
        total_orders_subquery = DistrictWiseMonthlyAggregate.objects.filter(
            filters
        ).values('delivery_state', 'delivery_district').annotate(
            total_orders=Sum('total_orders_delivered')
        ).values('total_orders')

        # Main query to get top 5 seller states per delivery state
        main_query = DistrictWiseMonthlyAggregate.objects.filter(
            filters
        ).annotate(
            seller_district_cleaned=Coalesce(Trim(F('seller_district')), V('Missing'))
        ).values(
            'delivery_district', 'seller_district_cleaned'
        ).annotate(
            order_demand=Sum('total_orders_delivered'),
            flow_percentage=(Sum('total_orders_delivered') * 100.0) / Subquery(total_orders_subquery)
        ).annotate(
            rn=Window(
                expression=RowNumber(),
                partition_by=F('delivery_district'),
                order_by=F('flow_percentage').desc()
            )
        ).filter(
            rn__lte=4
        ).order_by('-flow_percentage')

        # Convert queryset to DataFrame
        data = list(main_query)
        df = pd.DataFrame(data)
        df = df.rename(columns={'seller_district_cleaned': 'seller_district'})

        return df


    # def district_tree_chart(self, start_date, end_date, category=None, sub_category=None,
    #                         domain_name=None, state=None, district=None):
    #     stdate_obj = datetime.strptime(start_date, '%Y-%m-%d')
    #     edate_obj = datetime.strptime(end_date, '%Y-%m-%d')
    #
    #     start_month = stdate_obj.month
    #     start_year = stdate_obj.year
    #     end_month = edate_obj.month
    #     end_year = edate_obj.year
    #
    #     # Construct date filters using month and year
    #     filters = (
    #             (Q(order_year__gt=start_year) | (Q(order_year=start_year) & Q(order_month__gte=start_month))) &
    #             (Q(order_year__lt=end_year) | (Q(order_year=end_year) & Q(order_month__lte=end_month)))
    #     )
    #
    #     if domain_name:
    #         filters &= Q(domain_name=domain_name)
    #
    #     if state:
    #         filters &= Q(delivery_state__iexact=state)
    #
    #     if district:
    #         filters &= Q(delivery_district__iexact=district)
    #
    #     # Subquery to calculate total orders per delivery district within the specified month and year range
    #     total_orders_subquery = (DistrictWiseMonthlyAggregate.objects
    #                              .filter(order_year__gte=start_year,
    #                                      order_month__gte=start_month,
    #                                      order_year__lte=end_year,
    #                                      order_month__lte=end_month,
    #                                      delivery_district__isnull=False)
    #                              .values('delivery_district')
    #                              .annotate(total_orders=Sum('total_orders_delivered'))
    #                              .values('total_orders'))
    #
    #     # Main query to get top 4 seller districts per delivery district
    #     main_query = (DistrictWiseMonthlyAggregate.objects
    #                   .filter(filters, delivery_district__isnull=False)
    #                   .annotate(seller_district_cleaned=Coalesce(Trim(F('seller_district')), V('Missing')))
    #                   .values('delivery_district', 'seller_district_cleaned')
    #                   .annotate(order_demand=Sum('total_orders_delivered'))
    #                   .annotate(total_orders_district=Subquery(total_orders_subquery))
    #                   .annotate(flow_percentage=100.0 * F('order_demand') / F('total_orders_district'))
    #                   .annotate(rn=Window(expression=RowNumber(), partition_by=F('delivery_district'),
    #                                       order_by=F('flow_percentage').desc()))
    #                   .filter(rn__lte=4)
    #                   .order_by('-flow_percentage'))
    #
    #     # Convert queryset to list of dictionaries
    #     data = list(main_query)
    #
    #     # Optionally, convert to DataFrame if needed
    #     import pandas as pd
    #     df = pd.DataFrame(data)
    #
    #     return df

    def district_tree_chartsdas(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                                            state=None, district=None):

        table_name = constant.LOGISTICS_DISTRICT_TABLE

        query = f"""
                SELECT
                    sub.delivery_district,
                    COALESCE(NULLIF(TRIM(sub.seller_district), ''), 'Missing') AS seller_district,
                    sub.order_demand,
                    ROUND(sub.flow_percentage, 2) AS flow_percentage
                FROM (
                    SELECT
                        om.delivery_district,
                        om.seller_district,
                        SUM(om.total_orders_delivered) AS order_demand,
                        (SUM(om.total_orders_delivered) * 100.0) / total.total_orders AS flow_percentage,
                        ROW_NUMBER() OVER (
                            PARTITION BY om.delivery_district
                            ORDER BY SUM(om.total_orders_delivered) DESC
                        ) AS rn
                    FROM
                        {table_name} om
                    INNER JOIN (
                        SELECT
                            swdlo.delivery_district,
                            SUM(swdlo.total_orders_delivered) AS total_orders
                        FROM {table_name} swdlo
                        WHERE swdlo.order_date BETWEEN %s AND %s
                          AND swdlo.delivery_district <> ''
            """

        parameters = [start_date, end_date]

        if state:
            query += constant.swdlo_delivery_st_sq
            parameters.append(state)

        query += """
                        GROUP BY swdlo.delivery_district
                    ) total ON upper(om.delivery_district) = upper(total.delivery_district)
                    WHERE om.order_date BETWEEN %s AND %s
            """

        parameters.extend([start_date, end_date])

        if state:
            query += constant.tdr_delivery_state_sub_query
            parameters.append(state)
        if district:
            query += " AND upper(om.delivery_district) = upper(%s)"
            parameters.append(district)

        query += """
                    GROUP BY
                        om.delivery_district, om.seller_district, total.total_orders
                ) sub
                WHERE sub.rn <= 4
                ORDER BY sub.delivery_district, sub.flow_percentage DESC;
            """

        df = self.db_utility.execute_query(query, parameters)
        return df
    #
    def state_tree_chart22(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                                 state=None):

        table_name = constant.LOGISTICS_DISTRICT_TABLE

        query = f"""
            SELECT
                sub.delivery_state,
                COALESCE(NULLIF(TRIM(sub.seller_state), ''), 'Missing') AS seller_state,
                sub.order_demand,
                ROUND(sub.flow_percentage,2) as flow_percentage
            FROM (
                SELECT
                    om.delivery_state,
                    om.seller_state,
                    SUM(om.total_orders_delivered) AS order_demand,
                    (SUM(om.total_orders_delivered) * 100.0) / total.total_orders AS flow_percentage,
                    ROW_NUMBER() OVER (
                        PARTITION BY om.delivery_state
                        ORDER BY SUM(om.total_orders_delivered) DESC
                    ) as rn
                FROM
                    {table_name} om
                INNER JOIN (
                    SELECT
                        swdlo.delivery_state,
                        SUM(swdlo.total_orders_delivered) AS total_orders
                    FROM {table_name} swdlo
                    WHERE swdlo.order_date BETWEEN %s AND %s
                      AND swdlo.delivery_state <> ''
        """

        parameters = [start_date, end_date]


        query += """
                    GROUP BY swdlo.delivery_state
                ) total ON om.delivery_state = total.delivery_state
                WHERE
                 om.order_date BETWEEN %s AND %s
        """

        parameters.extend([start_date, end_date])

        if state:
            query += constant.tdr_delivery_state_sub_query
            parameters.append(state)

        query += """
                GROUP BY
                    om.delivery_state, om.seller_state, total.total_orders
            ) sub
            WHERE sub.rn <= 4
            ORDER BY sub.delivery_state, sub.flow_percentage DESC;
        """

        df = self.db_utility.execute_query(query, parameters)
        return df

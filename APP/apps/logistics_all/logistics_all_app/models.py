from django.db import models

class MonthlyProvider(models.Model):
    provider_key = models.CharField(max_length=255, null=True, blank=True)
    seller_district = models.CharField(max_length=50, null=True, blank=True)
    seller_state = models.CharField(max_length=50, null=True, blank=True)
    seller_state_code = models.CharField(max_length=50, null=True, blank=True)
    order_month = models.FloatField(null=True, blank=True)
    order_year = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'monthly_providers'
        verbose_name = 'Monthly Provider'
        verbose_name_plural = 'Monthly Providers'

    def __str__(self):
        return f"{self.provider_key} - {self.seller_state_code}"


from django.db import models

from django.db import models

from django.db import models


class DistrictWiseMonthlyAggregate(models.Model):
    domain_name = models.CharField(max_length=100, null=True)
    sub_domain = models.CharField(max_length=100, null=True)
    order_month = models.IntegerField(null=True)
    order_year = models.IntegerField(null=True)
    delivery_district = models.CharField(max_length=50, null=True)
    delivery_state = models.CharField(max_length=50, null=True)
    delivery_state_code = models.CharField(max_length=50, null=True)
    seller_district = models.CharField(max_length=50, null=True)
    seller_state = models.CharField(max_length=50, null=True)
    seller_state_code = models.CharField(max_length=50, null=True)
    total_orders_delivered = models.IntegerField(null=True)
    intrastate_orders = models.IntegerField(null=True)
    intradistrict_orders = models.IntegerField(null=True)

    class Meta:
        db_table = 'district_wise_monthly_aggregates'
        unique_together = (('domain_name', 'sub_domain', 'order_month', 'order_year', 'delivery_district',
                            'delivery_state', 'delivery_state_code', 'seller_district', 'seller_state',
                            'seller_state_code'),)


from django.db import models

class ProviderMonthlyAggregation(models.Model):
    provider_key = models.TextField(null=True, blank=True)
    provider_key_id = models.IntegerField(null=True, blank=True)
    seller_district = models.CharField(max_length=100, null=True, blank=True)
    seller_state = models.CharField(max_length=100, null=True, blank=True)
    seller_state_code = models.CharField(max_length=100, null=True, blank=True)
    order_year = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    jan = models.IntegerField(null=True, blank=True)
    feb = models.IntegerField(null=True, blank=True)
    mar = models.IntegerField(null=True, blank=True)
    apr = models.IntegerField(null=True, blank=True)
    may = models.IntegerField(null=True, blank=True)
    jun = models.IntegerField(null=True, blank=True)
    jul = models.IntegerField(null=True, blank=True)
    aug = models.IntegerField(null=True, blank=True)
    sep = models.IntegerField(null=True, blank=True)
    oct = models.IntegerField(null=True, blank=True)
    nov = models.IntegerField(null=True, blank=True)
    dec = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'provider_monthly_aggregation'
        verbose_name = 'District Wise Monthly Aggregate'
        verbose_name_plural = 'District Wise Monthly Aggregates'

    # def __str__(self):
    #     return f"{self.delivery_district} - {self.delivery_state_code}"

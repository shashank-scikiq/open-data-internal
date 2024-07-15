from django.urls import include, re_path, path
from django.conf import settings

urlpatterns = [
    re_path(r'^', include('apps.dashboard.dashboard_app.urls')),
    re_path(r'^', include('apps.retail_b2b.retail_b2b_app.urls')),
    re_path(r'^', include('apps.summary.summary_app.urls')),
    re_path(r'^', include('apps.logistics.logistics_app.urls')),
    re_path(r'^', include('apps.logistics_all.logistics_all_app.urls')),
    re_path(r'^', include('apps.retail_all.retail_all_app.urls')),
    # re_path(r'^', include('apps.mobility.mobility_app.urls')),
    # re_path(r'^', include('apps.finance.finance_app.urls')),
    re_path(r'^', include('apps.misc.misc_app.urls')),
]

handler404 = 'apps.dashboard.dashboard_apps.views_dal.not_found'

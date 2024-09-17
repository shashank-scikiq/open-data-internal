from django.urls import include, re_path, path
from django.conf import settings

urlpatterns = [
    # re_path(r'^', include('apps.retail_all.retail_all_app.urls')),
    # re_path(r'^', include('apps.logistics_all.logistics_all_app.urls')),
    # re_path(r'^', include('apps.retail_b2b.retail_b2b_app.urls')),
    # re_path(r'^', include('apps.dashboard.dashboard_app.urls')),

    re_path(r'^', include('apps.retail_all.retail_all_app.urls')),
    re_path(r'^', include('apps.logistics_all.logistics_all_app.urls')),
    re_path(r'^', include('apps.retail_b2b.urls')),
    re_path(r'^', include('apps.retail_b2c.urls')),
    re_path(r'^', include('apps.logistics_search.urls')),
    re_path(r'^', include('apps.misc.misc_app.urls')),
]

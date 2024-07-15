from django.urls import include, re_path, path
from django.conf import settings

urlpatterns = [
    re_path(r'^', include('apps.retail_all.retail_all_app.urls')),
    re_path(r'^', include('apps.logistics_all.logistics_all_app.urls')),
    re_path(r'^', include('apps.misc.misc_app.urls')),
]

handler404 = 'apps.dashboard.dashboard_apps.views_dal.not_found'

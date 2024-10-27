"""scikiq URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to u rlpatterns:  re_path(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  re_path(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  re_path(r'^blog/', include('blog.urls'))
"""

from django.urls import include, re_path, path
import importlib
from django.conf import settings
from django.views.generic.base import RedirectView
from apps.retail_all.retail_all_app.views import angular_app
from .views import * 
from apps.key_data_insight.views import FetchActiveSellerData


urlpatterns = [
    re_path(r'^', include('apps.retail_all.retail_all_app.urls')),
    re_path(r'^', include('apps.logistics_all.logistics_all_app.urls')),
    re_path(r'^', include('apps.retail_b2b.urls')),
    re_path(r'^', include('apps.retail_b2c.urls')),
    re_path(r'^', include('apps.logistics_search.urls')),
    re_path(r'^', include('apps.misc.misc_app.urls')),
    re_path(r'^', include('apps.key_data_insight.urls')),
    # re_path(r'^.*$',RedirectView.as_view(url='/', permanent=False)),
    path('api/landing-page/echart/', landing_page_echart_data, name='landing_page_echart_data'),
    path('api/landing-page/cumulative_orders/', landing_page_cumulative_orders, name='landing_page_cumulative_orders'),
    re_path(r'^(?:.*)/?$', angular_app, name='angular_app'),
]

# handler404 = 'apps.dashboard.dashboard_app.views.custom_404'

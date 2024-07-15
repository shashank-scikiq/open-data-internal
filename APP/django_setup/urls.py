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
from django_setup.settings import ENV_PATH
from django.conf import settings
from django.views.generic.base import RedirectView
from apps.retail_all.retail_all_app.views import angular_app

env_mod_urls = importlib.import_module(f'{ENV_PATH}.urls')

urlpatterns = env_mod_urls.urlpatterns
urlpatterns +=[
    # re_path(r'^.*$',RedirectView.as_view(url='/', permanent=False)),
    re_path(r'^(?:.*)/?$', angular_app, name='angular_app'),
]

handler404 = 'apps.dashboard.dashboard_app.views.custom_404'

# retail_b2b/urls.py
 
from django.urls import path
from .views import (
    fetch_license, data_dictionary_page, data_dictionary, pincode, 
    domain, landing_page_echart_data
)

urlpatterns = [
    # path('data_dictionary/', data_dictionary_page, name='data_dictionary'),
    path('api/data_dictionary/', data_dictionary, name='data_dictionary'),
    path('api/pincode/', pincode, name='pincode'),
    path('api/domain/', domain, name='domain'),
    path('license/', fetch_license, name='license'),
    path('api/landing-page/echart/', landing_page_echart_data, name='landing_page_echart_data')

]

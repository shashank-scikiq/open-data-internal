 
from django.urls import path
from . import views

urlpatterns=[
    path('api/logistics/search/top_card_delta/', views.FetchTopCardDeltaData.as_view(), name='map_statewise_data'),
    path('api/logistics/search/city_wise_data/', views.FetchCityWiseData.as_view(), name='logitic_search_city_wise_data'),
    path('api/logistics/search/data_date_range/', views.FetchDateRange.as_view(), name='logistic_search_date_range'),
    path('api/logistics/search/state_wise_data/', views.FetchStateWiseData.as_view(), name='state_wise_data')
]

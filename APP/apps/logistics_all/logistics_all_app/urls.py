# retail_all/urls.py
 
from django.urls import path, re_path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path(r'api/logistics/overall/get-max-date/', views.FetchMaxDate.as_view(), name='get-max-date'),

    path('api/logistics/overall/map_state_data/', views.FetchMapStateData.as_view(), name='map_state_data'),
    path('api/logistics/overall/map_statewise_data/', views.FetchMapStateWiseData.as_view(), name='map_statewise_data'),
    path('api/logistics/overall/top_card_delta/', views.FetchTopCardDeltaData.as_view(), name='map_statewise_data'),


    path('api/logistics/overall/top_state_orders/', views.FetchTopStatesOrders.as_view(), name='top_state_orders'),
    path('api/logistics/overall/top_cummulative_orders/', views.FetchCumulativeOrders.as_view(), name='top_state_orders'),
    path('api/logistics/overall/top_district_orders/', views.FetchTopDistrictOrders.as_view(), name='top_district_orders'),

    path('api/logistics/overall/top_cummulative_sellers/', views.FetchCumulativeSellers.as_view(), name='top_state_orders'),
    path('api/logistics/overall/top_state_sellers/', views.FetchTopStatesSellers.as_view(), name='top_state_sellers'),
    path('api/logistics/overall/top_district_sellers/', views.FetchTopDistrictSellers.as_view(), name='top_district_sellers'),

    path('api/logistics/overall/top_state_hyperlocal/', views.FetchTopStatesHyperlocal.as_view(), name='top_state_hyperlocal'),
    path('api/logistics/overall/top_district_hyperlocal/', views.FetchTopDistrictHyperlocal.as_view(), name='top_district_hyperlocal'),

    path('api/logistics/overall/top_seller_states/', views.FetchTop5SellerStates.as_view(), name='top_seller_states'),
    path('api/logistics/overall/top_seller_districts/', views.FetchTop5SellersDistrict.as_view(), name='top_seller_districts'),

    path('api/logistics/overall/fetch_downloadable_data/', views.FetchDownloadableData.as_view(), name='fetch_downloadable_data'),
]





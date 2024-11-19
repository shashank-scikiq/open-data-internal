# retail_all/urls.py
 
from django.urls import path
from . import views

urlpatterns = [

    path(r'api/retail/overall/get-max-date/', views.FetchMaxDate.as_view(), name='get-max-date'),
    path(r'api/state_district_list/', views.FetchDistrictList.as_view(),
         name='state_district_list'),

    path('api/retail/overall/map_state_data/', views.FetchMapStateData.as_view(), name='map_state_data'),
    path('api/retail/overall/map_statewise_data/', views.FetchMapStateWiseData.as_view(), name='map_statewise_data'),
    path('api/retail/overall/top_card_delta/', views.FetchTopCardDeltaData.as_view(), name='map_statewise_data'),


    path('api/retail/overall/top_state_orders/', views.FetchTopStatesOrders.as_view(), name='top_state_orders'),
    path('api/retail/overall/top_cummulative_orders/', views.FetchCumulativeOrders.as_view(), name='top_state_orders'),
    path('api/retail/overall/top_district_orders/', views.FetchTopDistrictOrders.as_view(), name='top_district_orders'),

    path('api/retail/overall/top_cummulative_sellers/', views.FetchCumulativeSellers.as_view(), name='top_state_orders'),
    path('api/retail/overall/top_state_sellers/', views.FetchTopStatesSellers.as_view(), name='top_state_sellers'),
    path('api/retail/overall/top_district_sellers/', views.FetchTopDistrictSellers.as_view(), name='top_district_sellers'),

    path('api/retail/overall/top_state_hyperlocal/', views.FetchTopStatesHyperlocal.as_view(), name='top_state_hyperlocal'),
    path('api/retail/overall/top_district_hyperlocal/', views.FetchTopDistrictHyperlocal.as_view(), name='top_district_hyperlocal'),

    path('api/retail/overall/top_seller_states/', views.FetchTop5SellerStates.as_view(), name='top_seller_states'),
    path('api/retail/overall/top_seller_districts/', views.FetchTop5SellersDistrict.as_view(), name='top_seller_districts'),
    path('api/retail/overall/top_delivery_state/', views.FetchTop5DeliveryState.as_view(), name='top_delivery_state'),
    path('api/retail/overall/top_delivery_district/', views.FetchTop5DeliveryDistrict.as_view(), name='top_delivery_district'),
]





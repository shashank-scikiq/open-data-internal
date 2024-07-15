# retail_b2b/urls.py
 
from django.urls import path
from . import views

urlpatterns = [
#     path('', views.dashboard, name='dashboard'),
    path(r'api/retail/b2c/get-max-date/', views.FetchMaxDate.as_view(), name='get-max-date'),
    path(r'api/retail/b2c/categories/', views.FetchCategoryList.as_view(), name='categories'),
    path(r'api/retail/b2c/state_district_list/', views.FetchDistrictList.as_view(), name='state_district_list'),

    path('api/retail/b2c/map_state_data/', views.FetchMapStateData.as_view(), name='map_state_data'),
    path('api/retail/b2c/map_statewise_data/', views.FetchMapStateWiseData.as_view(), name='map_statewise_data'),
    path('api/retail/b2c/top_card_delta/', views.FetchTopCardDeltaData.as_view(), name='map_statewise_data'),

    path('api/retail/b2c/key_insights/', views.FetchKeyInsightsData.as_view(), name='api_data'),

    path('api/retail/b2c/top_state_orders/', views.FetchTopStatesOrders.as_view(), name='top_state_orders'),
    path('api/retail/b2c/top_cummulative_orders/', views.FetchCumulativeOrders.as_view(), name='top_state_orders'),
    path('api/retail/b2c/top_district_orders/', views.FetchTopDistrictOrders.as_view(), name='top_district_orders'),
    path('api/retail/b2c/category_penetration_orders/', views.FetchCategoryPenetrationOrders.as_view(),
         name='category_penetration_orders'),
    path('api/retail/b2c/orders_per_state/', views.FetchOrdersPerState.as_view(), name='order_per_state'),
    path('api/retail/b2c/max_orders/', views.FetchMaxOrdersAPI.as_view(), name='max_orders'),

    path('api/retail/b2c/top_cummulative_sellers/', views.FetchCumulativeSellers.as_view(), name='top_state_orders'),
    path('api/retail/b2c/top_state_sellers/', views.FetchTopStatesSellers.as_view(), name='top_state_sellers'),
    path('api/retail/b2c/top_district_sellers/', views.FetchTopDistrictSellers.as_view(), name='top_district_sellers'),
    path('api/retail/b2c/category_penetration_sellers/', views.FetchCategoryPenetrationSellers.as_view(),
         name='category_penetration_sellers'),
    path('api/retail/b2c/sellers_per_state/', views.FetchSellersPerState.as_view(), name='seller_per_state'),
    path('api/retail/b2c/max_sellers/', views.FetchMaxSellersAPI.as_view(), name='max_sellers'),

    path('api/retail/b2c/top_state_hyperlocal/', views.FetchTopStatesHyperlocal.as_view(), name='top_state_hyperlocal'),
    path('api/retail/b2c/top_district_hyperlocal/', views.FetchTopDistrictHyperlocal.as_view(), name='top_district_hyperlocal'),
    path('api/retail/b2c/top_seller_states/', views.FetchTop5SellerStates.as_view(), name='top_seller_states'),
    path('api/retail/b2c/top_seller_districts/', views.FetchTop5SellersDistrict.as_view(), name='top_seller_districts'),

    path('api/retail/b2c/fetch_downloadable_data/', views.FetchDownloadableData.as_view(), name='fetch_downloadable_data'),

    # path('retail_b2b/', views.retail_b2b, name='retail_b2b'),

]





# retail_b2b/urls.py
 
from django.urls import path
from .views import FetchMaxDate, retailb2b, FetchMapStateData, FetchMapStateWiseData, FetchTopCardDeltaData, FetchCategoryList, FetchDownloadableData

urlpatterns = [
    path('api/retail/b2b/get-max-date/', FetchMaxDate.as_view(), name='get-max-date'),
    path('api/retail/b2b/categories/', FetchCategoryList.as_view(), name='categories'),
    path('api/retail/b2b/map_state_data/', FetchMapStateData.as_view(), name='map_state_data'),
    path('api/retail/b2b/map_statewise_data/', FetchMapStateWiseData.as_view(), name='map_statewise_data'),
    path('api/retail/b2b/top_card_delta/', FetchTopCardDeltaData.as_view(), name='top_card_delta'),
    path('api/retail/b2b/fetch_downloadable_data/', FetchDownloadableData.as_view(), name='fetch_downloadable_data'),
    # path('retail_b2b/', retailb2b, name='retail_b2b'),
]
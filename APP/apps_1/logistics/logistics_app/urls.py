# retail_b2b/urls.py
 
from django.urls import path
from .views import *
urlpatterns = [
     path('logistics/get-max-date/', FetchMaxDate.as_view(), name='get-max-date'),
     path('logistics/categories/', FetchCategoryList.as_view(), name='categories'),
     path('logistics/map_state_data/', FetchMapStateData.as_view(), name='map_state_data'),
     path('logistics/map_statewise_data/', FetchMapStateWiseData.as_view(), name='map_statewise_data'),
     path('logistics/top_card_delta/', FetchTopCardDeltaData.as_view(), name='top_card_delta'),
     path('logistics/fetch_downloadable_data/', FetchDownloadableData.as_view(), name='fetch_downloadable_data'),
     path('logistics/', logistics, name='logistics'),
]
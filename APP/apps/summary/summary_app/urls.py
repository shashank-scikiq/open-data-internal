# retail_b2b/urls.py
 
from django.urls import path
from .views import *

urlpatterns = [
    path('summary/get-max-date/', FetchMaxDate.as_view(), name='get-max-date'),
    # path('mobility/categories/', FetchCategoryList.as_view(), name='categories'),
    path('summary/map_state_data/', FetchMapStateData.as_view(), name='map_state_data'),
    path('summary/map_statewise_data/', FetchMapStateWiseData.as_view(), name='map_statewise_data'),
    path('summary/top_card_delta/', FetchTopCardDeltaData.as_view(), name='top_card_delta'),
    path('summary/fetch_downloadable_data/', FetchDownloadableData.as_view(), name='fetch_downloadable_data'),
    path('summary/', summary, name='summary'),
]
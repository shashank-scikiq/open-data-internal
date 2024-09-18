
from django.urls import path
from . import views

urlpatterns = [
    path('api/retail/b2b/map_state_data/', views.FetchMapStateData.as_view(), name='map_state_data'),
    path('api/retail/b2b/map_statewise_data/', views.FetchMapStateWiseData.as_view(), name='map_statewise_data'),
    path('api/retail/b2b/top_card_delta/', views.FetchTopCardDeltaData.as_view(), name='map_statewise_data'),
]





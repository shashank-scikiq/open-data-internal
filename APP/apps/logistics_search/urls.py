 
from django.urls import path
from . import views

urlpatterns=[
    path('api/logistics/search/top_card_delta/', views.FetchTopCardDeltaData.as_view(), name='map_statewise_data'),

]

from django.urls import path
from . import views

urlpatterns= [
    path('key_data_insight/api/getsellerdata/', views.FetchActiveSellerData.as_view(), name='getsellerdata')
]
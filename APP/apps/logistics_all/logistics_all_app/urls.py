from rest_framework.routers import DefaultRouter
from django.urls import include, path
from . import views

router = DefaultRouter()
router.register(r'logistics/overall', views.LogisticsViewset, basename='logistics_overall')

urlpatterns = [
    path('api/', include(router.urls)),
]







from rest_framework.routers import DefaultRouter
from django.urls import include, path
from . import views

router = DefaultRouter()
router.register(r'retail/overall', views.RetailViewset, basename='retail_overall')

urlpatterns = [
    path('api/', include(router.urls)),
]







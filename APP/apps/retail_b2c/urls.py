from rest_framework.routers import DefaultRouter
from django.urls import include, path
from . import views

router = DefaultRouter()
router.register(r'retail/b2c', views.RetailB2CViewset, basename='retail_b2c')

urlpatterns = [
    path('api/', include(router.urls)),
]


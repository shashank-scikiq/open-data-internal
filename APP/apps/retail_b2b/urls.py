from rest_framework.routers import DefaultRouter
from django.urls import include, path
from . import views

router = DefaultRouter()
router.register(r'retail/b2b', views.RetailB2BViewset, basename='retail_b2b')

urlpatterns = [
    path('api/', include(router.urls)),
]


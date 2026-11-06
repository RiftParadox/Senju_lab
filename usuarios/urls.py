from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PerfilClienteViewSet, CuponDescuentoViewSet

router = DefaultRouter()
router.register(r'perfiles', PerfilClienteViewSet)
router.register(r'cupones', CuponDescuentoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
# encargos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SolicitudPedidoViewSet, EncargoViewSet

router = DefaultRouter()
router.register(r'solicitudes', SolicitudPedidoViewSet, basename='solicitudpedido')
router.register(r'encargos', EncargoViewSet, basename='encargo')

urlpatterns = [
    path('', include(router.urls)),
]
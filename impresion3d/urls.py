from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import EncargoViewSet, ResumenDashboardView, SolicitudPedidoViewSet

router = DefaultRouter()
router.register(r'solicitudes', SolicitudPedidoViewSet, basename='solicitudpedido')
router.register(r'encargos', EncargoViewSet, basename='encargo')

urlpatterns = [
    # Métricas para el Dashboard de Figma
    path('resumen/', ResumenDashboardView.as_view(), name='resumen-dashboard'),
    path('', include(router.urls)),
]
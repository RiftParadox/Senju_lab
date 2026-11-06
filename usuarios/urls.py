from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PerfilClienteViewSet, CuponDescuentoViewSet, RegistroView

router = DefaultRouter()
router.register(r'perfiles', PerfilClienteViewSet)
router.register(r'cupones', CuponDescuentoViewSet)

urlpatterns = [
    path('auth/register/', RegistroView.as_view(), name='auth_register'),
    path('', include(router.urls)),
]
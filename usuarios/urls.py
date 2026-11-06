from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CuponDescuentoViewSet, PerfilClienteViewSet, RegistroView

router = DefaultRouter()
router.register(r'perfiles', PerfilClienteViewSet, basename='perfil')
router.register(r'cupones', CuponDescuentoViewSet, basename='cupon')

urlpatterns = [
    path('auth/registro/', RegistroView.as_view(), name='registro'),
    path('', include(router.urls)),
]
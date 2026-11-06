# usuarios/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PerfilClienteViewSet, CuponDescuentoViewSet, RegistroView

router = DefaultRouter()
router.register(r'perfiles', PerfilClienteViewSet, basename='perfilcliente')      
router.register(r'cupones', CuponDescuentoViewSet, basename='cupones') 
urlpatterns = [
    path('auth/registro/', RegistroView.as_view(), name='registro'),
    path('', include(router.urls)),
]
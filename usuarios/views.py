from rest_framework import viewsets
from .models import PerfilCliente, CuponDescuento
from serializers import PerfilClienteSerializer, CuponDescuentoSerializer

class PerfilClienteViewSet(viewsets.ModelViewSet):
    queryset = PerfilCliente.objects.all()
    serializer_class = PerfilClienteSerializer

class CuponDescuentoViewSet(viewsets.ModelViewSet):
    queryset = CuponDescuento.objects.all()
    serializer_class = CuponDescuentoSerializer

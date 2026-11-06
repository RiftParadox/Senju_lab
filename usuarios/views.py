# usuarios/views.py
from rest_framework import viewsets, generics, mixins
from rest_framework.permissions import AllowAny
from .models import PerfilCliente, CuponDescuento
from .serializers import PerfilClienteSerializer, CuponDescuentoSerializer, RegistroSerializer
from senju_lab.permissions import EsAdminOEsPropietario  # Permiso global centralizado

class PerfilClienteViewSet(viewsets.GenericViewSet,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           mixins.DestroyModelMixin):
    serializer_class = PerfilClienteSerializer
    permission_classes = [EsAdminOEsPropietario]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return PerfilCliente.objects.all()
        return PerfilCliente.objects.filter(user=user)


class CuponDescuentoViewSet(viewsets.ModelViewSet):
    serializer_class = CuponDescuentoSerializer
    permission_classes = [EsAdminOEsPropietario]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return CuponDescuento.objects.all()
        return CuponDescuento.objects.filter(cliente__user=user)


class RegistroView(generics.CreateAPIView):
    serializer_class = RegistroSerializer
    permission_classes = [AllowAny]
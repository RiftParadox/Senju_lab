from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import SolicitudPedido, Encargo
from .serializers import SolicitudPedidoSerializer, EncargoSerializer
from senju_lab.permissions import EsAdminOEsPropietario

class SolicitudPedidoViewSet(viewsets.ModelViewSet):
    serializer_class = SolicitudPedidoSerializer
    permission_classes = [IsAuthenticated, EsAdminOEsPropietario]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return SolicitudPedido.objects.all()
        return SolicitudPedido.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EncargoViewSet(viewsets.ModelViewSet):
    serializer_class = EncargoSerializer
    permission_classes = [IsAuthenticated, EsAdminOEsPropietario]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Encargo.objects.all()
        return Encargo.objects.filter(solicitud__user=user)
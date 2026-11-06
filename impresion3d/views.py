from rest_framework import permissions, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from senju_lab.permissions import EsAdminOEsPropietario

from .models import Encargo, EstadoEncargo, EstadoSolicitud, SolicitudPedido
from .serializers import EncargoSerializer, SolicitudPedidoSerializer


class SolicitudPedidoViewSet(viewsets.ModelViewSet):
    serializer_class = SolicitudPedidoSerializer

    def get_permissions(self):
        # Solo el admin puede borrar solicitudes de la BD
        if self.action == 'destroy':
            return [permissions.IsAdminUser()]
        return [IsAuthenticated(), EsAdminOEsPropietario()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return SolicitudPedido.objects.all()
        return SolicitudPedido.objects.filter(user=user)

    def perform_create(self, serializer):
        # Asigna automáticamente al usuario autenticado y garantiza el estado PENDIENTE
        serializer.save(user=self.request.user, estado=EstadoSolicitud.PENDIENTE)


class EncargoViewSet(viewsets.ModelViewSet):
    serializer_class = EncargoSerializer

    def get_permissions(self):
        # REGLA CRUCIAL: Solo el administrador puede CREAR o ELIMINAR encargos
        if self.action in ['create', 'destroy']:
            return [permissions.IsAdminUser()]
        # Clientes y Admin pueden ver (list/retrieve) y actualizar (PATCH para aprobar/cancelar)
        return [IsAuthenticated(), EsAdminOEsPropietario()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Encargo.objects.all()
        return Encargo.objects.filter(solicitud__user=user)


class ResumenDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.is_staff:
            solicitudes_qs = SolicitudPedido.objects.all()
            encargos_qs = Encargo.objects.all()
        else:
            solicitudes_qs = SolicitudPedido.objects.filter(user=user)
            encargos_qs = Encargo.objects.filter(solicitud__user=user)

        # 1. Solicitudes abiertas (pendientes de revisión)
        solicitudes_abiertas = solicitudes_qs.filter(estado=EstadoSolicitud.PENDIENTE).count()

        # 2. Cotizaciones listas (el taller ya cotizó y espera al cliente)
        cotizaciones_listas = encargos_qs.filter(estado=EstadoEncargo.COTIZADO).count()

        # 3. Encargos activos (en cola o producción)
        estados_activos = [
            EstadoEncargo.APROBADO,
            EstadoEncargo.AGENDADO,
            EstadoEncargo.IMPRIMIENDO,
            EstadoEncargo.TERMINADO
        ]
        encargos_activos = encargos_qs.filter(estado__in=estados_activos).count()

        # 4. Piezas entregadas con éxito
        piezas_entregadas = encargos_qs.filter(estado=EstadoEncargo.ENTREGADO).count()

        return Response({
            "solicitudes_abiertas": solicitudes_abiertas,
            "cotizaciones_listas": cotizaciones_listas,
            "encargos_activos": encargos_activos,
            "piezas_entregadas": piezas_entregadas
        }, status=status.HTTP_200_OK)
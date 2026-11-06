from django.db import transaction
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
        if self.action == 'destroy':
            return [permissions.IsAdminUser()]
        return [IsAuthenticated(), EsAdminOEsPropietario()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return SolicitudPedido.objects.all()
        return SolicitudPedido.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, estado=EstadoSolicitud.PENDIENTE)

    def perform_update(self, serializer):
        # Transacción segura: Si el cliente acepta, se crea el Encargo automáticamente
        with transaction.atomic():
            solicitud_actualizada = serializer.save()

            if solicitud_actualizada.estado == EstadoSolicitud.ACEPTADA:
                # Evita duplicados con get_or_create
                Encargo.objects.get_or_create(
                    solicitud=solicitud_actualizada,
                    defaults={
                        'nombre_modelo': f"Modelo de {solicitud_actualizada.codigo}",
                        'estado': EstadoEncargo.AGENDADO
                    }
                )


class EncargoViewSet(viewsets.ModelViewSet):
    serializer_class = EncargoSerializer

    def get_permissions(self):
        # Solo el admin puede crear manualmente o eliminar órdenes de trabajo
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [permissions.IsAdminUser()]
        # El cliente puede consultar (list, retrieve) el estado de sus piezas
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

        # 1. Solicitudes abiertas: El cliente espera revisión
        solicitudes_abiertas = solicitudes_qs.filter(estado=EstadoSolicitud.PENDIENTE).count()

        # 2. Cotizaciones listas: El taller ya cotizó y el cliente tiene el botón de aceptar/cancelar
        cotizaciones_listas = solicitudes_qs.filter(estado=EstadoSolicitud.COTIZADA).count()

        # 3. Encargos activos: En cola, imprimiendo o terminados (sin entregar aún)
        estados_activos = [
            EstadoEncargo.AGENDADO,
            EstadoEncargo.IMPRIMIENDO,
            EstadoEncargo.TERMINADO
        ]
        encargos_activos = encargos_qs.filter(estado__in=estados_activos).count()

        # 4. Piezas entregadas
        piezas_entregadas = encargos_qs.filter(estado=EstadoEncargo.ENTREGADO).count()

        return Response({
            "solicitudes_abiertas": solicitudes_abiertas,
            "cotizaciones_listas": cotizaciones_listas,
            "encargos_activos": encargos_activos,
            "piezas_entregadas": piezas_entregadas
        }, status=status.HTTP_200_OK)
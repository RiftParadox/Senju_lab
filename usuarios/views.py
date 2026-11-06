from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CuponDescuento, PerfilCliente
from .serializers import (
    CuponDescuentoSerializer,
    PerfilClienteSerializer,
    RegistroSerializer,
)


class PerfilClienteViewSet(viewsets.ModelViewSet):
    serializer_class = PerfilClienteSerializer

    def get_permissions(self):
        """
        El endpoint /me está disponible para cualquier usuario autenticado.
        El listado general y el CRUD por ID son exclusivos de administradores.
        """
        if self.action == 'me':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        return PerfilCliente.objects.select_related('user').all()

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        """
        Acceso al perfil del usuario autenticado.
        GET: Consulta datos propios.
        PATCH: Actualización parcial (ej. teléfono).
        """
        perfil, _ = PerfilCliente.objects.get_or_create(user=request.user)

        if request.method == 'GET':
            serializer = self.get_serializer(perfil)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(perfil, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class CuponDescuentoViewSet(viewsets.ModelViewSet):
    serializer_class = CuponDescuentoSerializer

    def get_permissions(self):
        """
        Los clientes solo pueden leer sus cupones (list, retrieve).
        Solo los administradores pueden crearlos (create) o eliminarlos (destroy).
        """
        if self.action in ['create', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return CuponDescuento.objects.select_related('cliente__user').all()
        return CuponDescuento.objects.filter(cliente__user=user)


class RegistroView(generics.CreateAPIView):
    serializer_class = RegistroSerializer
    permission_classes = [permissions.AllowAny]
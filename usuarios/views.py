from rest_framework import viewsets, generics, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from .models import PerfilCliente, CuponDescuento
from .serializers import PerfilClienteSerializer, CuponDescuentoSerializer, RegistroSerializer

class EsAdminOEsPropietario(BasePermission):
    """
    Permiso personalizado:
    - Los administradores (staff) tienen acceso total (Lectura y Escritura).
    - Los usuarios normales solo pueden ver/editar sus propios recursos.
    """
    def has_permission(self, request, view):
        # Todos deben estar autenticados para entrar aquí
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Si es admin, pasa sin problema
        if request.user.is_staff:
            return True
        # Si es cliente, verificamos que el objeto le pertenezca
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'cliente'):
            return obj.cliente.user == request.user
        return False


class PerfilClienteViewSet(viewsets.GenericViewSet,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           mixins.DestroyModelMixin):
    """
    ViewSet de Perfiles:
    - Usa el permiso personalizado. Si es Admin, puede crear, borrar, listar todo.
    - Si es cliente normal, su get_queryset lo aísla solo a su perfil y 
      los mixins se encargan de restringir lo que puede hacer.
    """
    serializer_class = PerfilClienteSerializer
    permission_classes = [EsAdminOEsPropietario]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return PerfilCliente.objects.all()
        return PerfilCliente.objects.filter(user=user)


class CuponDescuentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet de Cupones:
    - Al usar ModelViewSet completo, el admin (is_staff) puede crear, editar y borrar cupones libremente.
    - El cliente normal, gracias a get_queryset y los permisos, solo verá sus propios cupones.
    """
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
# senju_lab/permissions.py
from rest_framework import permissions

class EsAdminOEsPropietario(permissions.BasePermission):
    """
    Permiso global y reutilizable para todo Senju Lab:
    - Staff (Admin): Acceso total.
    - Cliente: Solo accede si el recurso le pertenece directa o indirectamente.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        # Validación polimórfica según la entidad consultada
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'cliente'):
            return obj.cliente.user == request.user
        if hasattr(obj, 'solicitud'):  # Soporte para los Encargos 3D
            return obj.solicitud.user == request.user
            
        return False
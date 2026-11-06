# encargos/serializers.py
from rest_framework import serializers
from .models import SolicitudPedido, Encargo

class SolicitudPedidoSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = SolicitudPedido
        fields = ['id', 'user', 'user_username', 'descripcion', 'imagen_referencia', 'estado', 'fecha_creacion']
        read_only_fields = ['id', 'user', 'estado', 'fecha_creacion']


class EncargoSerializer(serializers.ModelSerializer):
    solicitud_detalle = SolicitudPedidoSerializer(source='solicitud', read_only=True)

    class Meta:
        model = Encargo
        fields = [
            'id', 'solicitud', 'solicitud_detalle', 'nombre_modelo',
            'peso_estimado_gramos', 'tiempo_estimado_horas', 'escala',
            'estado', 'precio_cotizado', 'fecha_creacion',
            'fecha_programada_inicio', 'fecha_completado'
        ]
        read_only_fields = ['id', 'fecha_creacion']

    def validate(self, data):
        request = self.context.get('request')
        
        # Si el usuario está autenticado y NO es staff (es un cliente normal)
        if request and request.user and not request.user.is_staff:
            
            # SOLO aplicamos estas restricciones si es una ACTUALIZACIÓN (self.instance no es None). 
            # Si se está creando (POST), permitimos que pase limpio.
            if self.instance is not None:
                
                # 1. Validar restricción de estado: El cliente solo puede aprobar (agendar) o cancelar
                if 'estado' in data:
                    nuevo_estado = data['estado']
                    estados_permitidos_cliente = ['AGENDADO', 'CANCELADO']
                    if nuevo_estado not in estados_permitidos_cliente:
                        raise serializers.ValidationError(
                            {"estado": "Como cliente, solo puedes aprobar la cotización o cancelarla."}
                        )
                
                # 2. Prohibir al cliente modificar campos técnicos o económicos del taller en edición
                campos_restringidos = [
                    'nombre_modelo', 'peso_estimado_gramos', 'tiempo_estimado_horas',
                    'escala', 'precio_cotizado', 'fecha_programada_inicio', 'fecha_completado'
                ]
                for campo in campos_restringidos:
                    if campo in data:
                        raise serializers.ValidationError(
                            {campo: f"No tienes permisos para modificar el campo '{campo}'. Esto lo gestiona el taller."}
                        )
                    
        return data
from rest_framework import serializers
from .models import Encargo, EstadoEncargo, EstadoSolicitud, SolicitudPedido


class SolicitudPedidoSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    codigo = serializers.ReadOnlyField()

    class Meta:
        model = SolicitudPedido
        fields = [
            'id', 'codigo', 'user', 'user_username',
            'descripcion', 'imagen_referencia', 'estado', 'fecha_creacion'
        ]
        read_only_fields = ['id', 'codigo', 'user', 'fecha_creacion']

    def validate(self, data):
        request = self.context.get('request')
        user = request.user if request else None

        # Si es un cliente regular (no staff/admin)
        if user and not user.is_staff:
            # Si está editando una solicitud existente (PATCH / PUT)
            if self.instance is not None:
                if 'estado' in data:
                    nuevo_estado = data['estado']
                    # El cliente SOLO puede cancelar su solicitud
                    if nuevo_estado != EstadoSolicitud.CANCELADA:
                        raise serializers.ValidationError({
                            "estado": "Como cliente, únicamente puedes cancelar la solicitud (estado CANCELADA)."
                        })

                # Si ya fue Aceptada, Rechazada o Cancelada, no puede editar la descripción ni la imagen
                if self.instance.estado != EstadoSolicitud.PENDIENTE:
                    if any(k in data for k in ['descripcion', 'imagen_referencia']):
                        raise serializers.ValidationError(
                            "No puedes modificar los datos de una solicitud que ya fue procesada por el taller."
                        )
            else:
                # Al crear una nueva, se asegura que no envíe un estado arbitrario
                if 'estado' in data and data['estado'] != EstadoSolicitud.PENDIENTE:
                    raise serializers.ValidationError({
                        "estado": "Toda nueva solicitud debe iniciar en estado PENDIENTE."
                    })

        return data


class EncargoSerializer(serializers.ModelSerializer):
    solicitud_detalle = SolicitudPedidoSerializer(source='solicitud', read_only=True)
    codigo = serializers.ReadOnlyField()

    class Meta:
        model = Encargo
        fields = [
            'id', 'codigo', 'solicitud', 'solicitud_detalle', 'nombre_modelo',
            'peso_estimado_gramos', 'tiempo_estimado_horas', 'escala',
            'estado', 'precio_cotizado', 'fecha_creacion',
            'fecha_programada_inicio', 'fecha_completado'
        ]
        read_only_fields = ['id', 'codigo', 'fecha_creacion']

    def validate(self, data):
        request = self.context.get('request')
        user = request.user if request else None

        # Restricciones para el cliente al interactuar con el encargo
        if user and not user.is_staff:
            if self.instance is not None:
                # 1. Bloqueo total de campos técnicos y económicos
                campos_prohibidos = [
                    'solicitud', 'nombre_modelo', 'peso_estimado_gramos',
                    'tiempo_estimado_horas', 'escala', 'precio_cotizado',
                    'fecha_programada_inicio', 'fecha_completado'
                ]
                for campo in campos_prohibidos:
                    if campo in data:
                        raise serializers.ValidationError({
                            campo: f"No tienes permisos para modificar '{campo}'. Solo el taller gestiona este valor."
                        })

                # 2. Control de la decisión sobre la cotización
                if 'estado' in data:
                    nuevo_estado = data['estado']

                    # Solo puede responder si el taller ya le cotizó
                    if self.instance.estado != EstadoEncargo.COTIZADO:
                        raise serializers.ValidationError({
                            "estado": f"No puedes modificar el estado mientras el encargo esté en '{self.instance.estado}'."
                        })

                    # Solo puede aceptar o declinar
                    if nuevo_estado not in [EstadoEncargo.APROBADO, EstadoEncargo.CANCELADO]:
                        raise serializers.ValidationError({
                            "estado": "Como cliente, solo puedes aceptar la cotización (APROBADO) o declinarla (CANCELADO)."
                        })

        return data
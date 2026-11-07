from rest_framework import serializers
from .models import Encargo, EstadoEncargo, EstadoSolicitud, SolicitudPedido


class SolicitudPedidoSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    codigo = serializers.ReadOnlyField()

    class Meta:
        model = SolicitudPedido
        fields = [
            'id', 'codigo', 'user', 'user_username',
            'descripcion', 'imagen_referencia',
            'precio_cotizado', 'peso_estimado_gramos', 'tiempo_estimado_horas',
            'estado', 'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'codigo', 'user', 'fecha_creacion', 'fecha_actualizacion']

    def validate(self, data):
        request = self.context.get('request')
        user = request.user if request else None

        # Si es un cliente regular (no staff)
        if user and not user.is_staff:
            # 1. Prohibir modificar campos de cotización
            campos_taller = ['precio_cotizado', 'peso_estimado_gramos', 'tiempo_estimado_horas']
            for campo in campos_taller:
                if campo in data:
                    raise serializers.ValidationError({
                        campo: "Solo el administrador puede establecer valores de cotización."
                    })

            # 2. Control de cambios de estado por parte del cliente
            if self.instance is not None and 'estado' in data:
                nuevo_estado = data['estado']
                estado_actual = self.instance.estado

                # El cliente puede cancelar en cualquier momento previo a producción
                if nuevo_estado == EstadoSolicitud.CANCELADA:
                    if estado_actual == EstadoSolicitud.ACEPTADA:
                        raise serializers.ValidationError({
                            "estado": "La solicitud ya está en producción. Contacta al taller directamente."
                        })
                    return data

                # El cliente solo puede aceptar si el taller ya la cotizó
                elif nuevo_estado == EstadoSolicitud.ACEPTADA:
                    if estado_actual != EstadoSolicitud.COTIZADA:
                        raise serializers.ValidationError({
                            "estado": "Solo puedes aceptar una solicitud que esté en estado COTIZADA."
                        })
                    return data

                else:
                    raise serializers.ValidationError({
                        "estado": "Acción no permitida. Solo puedes aceptar la cotización o cancelar la solicitud."
                    })

            # Al crear una solicitud, siempre inicia en PENDIENTE
            if self.instance is None and 'estado' in data:
                if data['estado'] != EstadoSolicitud.PENDIENTE:
                    raise serializers.ValidationError({
                        "estado": "Toda nueva solicitud debe iniciar en estado PENDIENTE."
                    })

        return data


class EncargoSerializer(serializers.ModelSerializer):
    codigo = serializers.ReadOnlyField()
    # Datos leídos directamente de la solicitud vinculada (sin duplicar en BD)
    precio_cotizado = serializers.ReadOnlyField(source='solicitud.precio_cotizado')
    cliente_username = serializers.ReadOnlyField(source='solicitud.user.username')

    class Meta:
        model = Encargo
        fields = [
            'id', 'codigo', 'solicitud', 'cliente_username',
            'nombre_modelo', 'escala', 'precio_cotizado',
            'estado', 'fecha_creacion',
            'fecha_programada_inicio', 'fecha_completado'
        ]
        read_only_fields = ['id', 'codigo', 'fecha_creacion']

    def validate(self, data):
        request = self.context.get('request')
        user = request.user if request else None

        solicitud = data.get('solicitud', self.instance.solicitud if self.instance else None)
        if self.instance is None:
            if solicitud is None:
                raise serializers.ValidationError({'solicitud': 'Selecciona la solicitud aceptada que origina este encargo.'})
            if solicitud.estado != EstadoSolicitud.ACEPTADA:
                raise serializers.ValidationError({'solicitud': 'Solo se pueden crear encargos para solicitudes aceptadas.'})
            if hasattr(solicitud, 'encargo'):
                raise serializers.ValidationError({'solicitud': 'Esta solicitud ya tiene un encargo asociado.'})
        elif 'solicitud' in data and solicitud.pk != self.instance.solicitud_id:
            raise serializers.ValidationError({'solicitud': 'No se puede cambiar la solicitud asociada a un encargo.'})

        # Solo el staff del taller puede cambiar los estados de fabricación
        if user and not user.is_staff:
            raise serializers.ValidationError(
                "Solo el personal del taller puede actualizar el avance de los encargos en producción."
            )
        return data
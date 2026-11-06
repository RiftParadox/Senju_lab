from django.contrib.auth.models import User
from django.db import models


class EstadoSolicitud(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente de cotización'
    COTIZADA = 'COTIZADA', 'Cotizada por el taller (Esperando respuesta)'
    ACEPTADA = 'ACEPTADA', 'Cotización aceptada (Pasa a producción)'
    RECHAZADA = 'RECHAZADA', 'Rechazada por el taller'
    CANCELADA = 'CANCELADA', 'Cancelada por el cliente'


class EstadoEncargo(models.TextChoices):
    AGENDADO = 'AGENDADO', 'En cola de impresión'
    IMPRIMIENDO = 'IMPRIMIENDO', 'Imprimiendo en taller'
    TERMINADO = 'TERMINADO', 'Terminado (Listo para entrega)'
    ENTREGADO = 'ENTREGADO', 'Entregado al cliente'
    CANCELADO = 'CANCELADO', 'Cancelado en producción'


class SolicitudPedido(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="solicitudes")
    descripcion = models.TextField(blank=True, null=True)
    imagen_referencia = models.ImageField(upload_to='solicitudes/', blank=True, null=True)
    
    # Datos de la cotización (los llena el taller al revisar)
    precio_cotizado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    peso_estimado_gramos = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    tiempo_estimado_horas = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    estado = models.CharField(
        max_length=20,
        choices=EstadoSolicitud.choices,
        default=EstadoSolicitud.PENDIENTE
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    @property
    def codigo(self):
        return f"SL-{self.id:04d}" if self.id else None

    def __str__(self):
        return f"{self.codigo} de {self.user.username} [{self.estado}]"


class Encargo(models.Model):
    # Relación 1 a 1: Una solicitud aceptada produce exactamente una orden de producción
    solicitud = models.OneToOneField(
        SolicitudPedido, on_delete=models.CASCADE, related_name="encargo"
    )
    nombre_modelo = models.CharField(max_length=100)
    escala = models.CharField(max_length=20, blank=True, null=True, default="1:1")
    
    estado = models.CharField(
        max_length=20,
        choices=EstadoEncargo.choices,
        default=EstadoEncargo.AGENDADO
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_programada_inicio = models.DateTimeField(blank=True, null=True)
    fecha_completado = models.DateTimeField(blank=True, null=True)

    @property
    def codigo(self):
        return f"ENC-{self.id:04d}" if self.id else None

    def __str__(self):
        return f"{self.codigo} - {self.nombre_modelo} [{self.estado}]"
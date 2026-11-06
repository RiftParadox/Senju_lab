from django.db import models
from django.contrib.auth.models import User

class EstadoSolicitud(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente de revisión'
    ACEPTADO = 'ACEPTADO', 'Aceptado por el taller'
    RECHAZADO = 'RECHAZADO', 'Rechazado'

class EstadoEncargo(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente de cotización'
    COTIZADO = 'COTIZADO', 'Cotización lista (Esperando aprobación)'
    APROBADO = 'APROBADO', 'Cotizacion aprobada'
    AGENDADO = 'AGENDADO', 'Agendado para impresión'
    IMPRIMIENDO = 'IMPRIENDO', 'Imprimiendo modelo'
    TERMINADO = 'TERMINADO', 'Terminado listo para entrega'
    ENTREGADO = 'ENTREGADO', 'Entregado al cliente'
    CANCELADO = 'CANCELADO', 'Cancelado (Sin acuerdo / Declinado)'
    

class SolicitudPedido(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="solicitudes")
    descripcion = models.TextField(blank=True, null=True)
    imagen_referencia = models.ImageField(upload_to='solicitudes/', blank=True, null=True)
    estado = models.CharField(
        max_length=20,
        choices=EstadoSolicitud.choices,
        default=EstadoSolicitud.PENDIENTE
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Solicitud #{self.id} de {self.user.username} [{self.estado}]"


class Encargo(models.Model):
    solicitud = models.ForeignKey(SolicitudPedido, on_delete=models.CASCADE, related_name="encargos")
    nombre_modelo = models.CharField(max_length=100)              
    
    peso_estimado_gramos = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    
    tiempo_estimado_horas = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    escala = models.CharField(max_length=20, blank=True, null=True) 
    
    estado = models.CharField(
        max_length=20,
        choices=EstadoEncargo.choices,
        default=EstadoEncargo.PENDIENTE
    )          
    
    precio_cotizado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)    
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    fecha_programada_inicio = models.DateTimeField(blank=True, null=True)
    fecha_completado = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Encargo #{self.id} - {self.nombre_modelo} [{self.estado}]"
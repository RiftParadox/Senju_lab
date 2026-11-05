from django.db import models
from django.contrib.auth.models import User

from django.contrib.auth.models import User
from django.db import models


class PerfilCliente(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="perfil"
    )
    telefono = models.CharField(max_length=20, blank=True, null=True)
    sellos_tarjeta = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Perfil de {self.user.username} - Sellos: {self.sellos_tarjeta}/5"


class CuponDescuento(models.Model):
    # Relación de Uno a Muchos: Un cliente puede tener MUCHOS cupones acumulados
    cliente = models.ForeignKey(
        PerfilCliente, on_delete=models.CASCADE, related_name="cupones"
    )

    # Código único del cupón (ej: SENJU-XYZ789)
    codigo = models.CharField(max_length=50, unique=True)

    # Valor del descuento (puede ser un porcentaje o un monto fijo, usaremos porcentaje por ejemplo)
    porcentaje_descuento = models.PositiveIntegerField(default=10)

    # Para saber si ya fue gastado o sigue disponible en la UI bonita
    usado = models.BooleanField(default=False)

    # Fechas para control
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_uso = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        estado = "Usado" if self.usado else "Disponible"
        return f"Cupón {self.porcentaje_descuento}% de {self.cliente.user.username} ({estado})"
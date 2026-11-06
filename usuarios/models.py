from django.contrib.auth.models import User
from django.db import models


class PerfilCliente(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="perfil"
    )
    telefono = models.CharField(max_length=20, blank=True, null=True)
    sellos_tarjeta = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Perfil de Cliente"
        verbose_name_plural = "Perfiles de Clientes"

    def __str__(self):
        return f"Perfil de {self.user.username} - Sellos: {self.sellos_tarjeta}/5"


class CuponDescuento(models.Model):
    cliente = models.ForeignKey(
        PerfilCliente, on_delete=models.CASCADE, related_name="cupones"
    )
    codigo = models.CharField(max_length=50, unique=True)
    porcentaje_descuento = models.PositiveIntegerField(default=10)
    usado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_uso = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Cupón de Descuento"
        verbose_name_plural = "Cupones de Descuento"

    def __str__(self):
        estado = "Usado" if self.usado else "Disponible"
        return f"Cupón {self.porcentaje_descuento}% de {self.cliente.user.username} ({estado})"
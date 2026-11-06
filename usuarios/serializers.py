from rest_framework import serializers
from .models import PerfilCliente, CuponDescuento

class PerfilClienteSerializer(serializers.ModelSerializer):
    class meta:
        model: PerfilCliente
        fields: '__all__'

class CuponDescuentoSerializer(serializers.ModelSerializer):
    class meta:
        model: CuponDescuento
        fields: '__all__'
from rest_framework import serializers
from .models import PerfilCliente, CuponDescuento
from django.contrib.auth.models import User


class RegistroSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = PerfilCliente
        # Listamos explícitamente los campos del perfil y los de autenticación que aceptamos
        fields = ['username', 'email', 'password', 'telefono', 'sellos_tarjeta']  

    def create(self, validated_data):
        # 1. Extraemos los datos de usuario y limpiamos validated_data
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        # 2. Creamos el usuario base de Django (esto hace el hash seguro de la contraseña)
        user = User.objects.create_user(username=username, email=email, password=password)

        # 3. Creamos el perfil del cliente enlazándolo al usuario recién creado
        perfil = PerfilCliente.objects.create(user=user, **validated_data)
        
        return perfil

class PerfilClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilCliente
        fields = '__all__'

class CuponDescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuponDescuento
        fields = '__all__'
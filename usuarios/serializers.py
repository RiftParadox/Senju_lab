from django.contrib.auth.models import User
from rest_framework import serializers
from .models import CuponDescuento, PerfilCliente


class RegistroSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = PerfilCliente
        fields = ['id', 'username', 'email', 'password', 'telefono', 'sellos_tarjeta']
        # SEGURIDAD: El cliente no puede autoasignarse sellos al registrarse
        read_only_fields = ['id', 'sellos_tarjeta']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Este nombre de usuario ya está en uso.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Este correo electrónico ya está registrado.')
        return value

    def create(self, validated_data):
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        user = User.objects.create_user(username=username, email=email, password=password)
        perfil = PerfilCliente.objects.create(user=user, **validated_data)
        return perfil

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['username'] = instance.user.username
        representation['email'] = instance.user.email
        return representation


class PerfilClienteSerializer(serializers.ModelSerializer):
    # Exponemos datos del User directamente en el perfil
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    is_staff = serializers.BooleanField(source='user.is_staff', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)

    class Meta:
        model = PerfilCliente
        fields = ['id', 'user', 'username', 'email', 'telefono', 'sellos_tarjeta', 'is_staff', 'is_active']
        read_only_fields = ['id', 'user', 'username', 'email', 'is_staff', 'is_active']

    def validate(self, data):
        request = self.context.get('request')
        # Solo los administradores pueden alterar los sellos
        if request and request.user and not request.user.is_staff:
            if 'sellos_tarjeta' in data:
                raise serializers.ValidationError(
                    {'sellos_tarjeta': 'No tienes permisos para modificar tus sellos de tarjeta.'}
                )
        return data


class CuponDescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuponDescuento
        fields = '__all__'
        read_only_fields = ['id', 'fecha_creacion']
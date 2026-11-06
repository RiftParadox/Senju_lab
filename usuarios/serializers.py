from rest_framework import serializers
from .models import PerfilCliente, CuponDescuento
from django.contrib.auth.models import User

class RegistroSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = PerfilCliente
        fields = ['id', 'username', 'email', 'password', 'telefono', 'sellos_tarjeta']
        read_only_fields = ['id']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Este nombre de usuario ya esta en uso.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Este correo electronico ya esta registrado.')
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
    class Meta:
        model = PerfilCliente
        fields = '__all__'
        read_only_fields = ['id', 'user']

    def validate(self, data):
        request = self.context.get('request')
        if request and request.user and not request.user.is_staff:
            if 'sellos_tarjeta' in data:
                raise serializers.ValidationError(
                    {'sellos_tarjeta': 'No tienes permisos para modificar directamente tus sellos de tarjeta.'}
                )
        return data


class CuponDescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuponDescuento
        fields = '__all__'

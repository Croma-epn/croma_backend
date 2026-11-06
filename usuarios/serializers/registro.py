from rest_framework import serializers
from usuarios.models import Usuario

class RegistroUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['nombre', 'correo', 'contrasena']
        extra_kwargs = {
            'contrasena': {'write_only': True}
        }
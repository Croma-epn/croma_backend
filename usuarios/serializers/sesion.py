from rest_framework import serializers

from .comunes import UsuarioSerializer

# Estos serializers solo documentan la forma del JSON en Swagger:
# las views arman la respuesta a mano.


class LoginExitosoSerializer(serializers.Serializer):
    """Respuesta al iniciar sesión."""

    mensaje = serializers.CharField(help_text='Mensaje de confirmación.')
    usuario = UsuarioSerializer(help_text='Datos del usuario que inició sesión.')
    access = serializers.CharField(
        help_text='Token de acceso, de corta duración. Se envía en la cabecera '
                  '`Authorization: Bearer <access>`.',
    )


class RenovarSesionExitosoSerializer(serializers.Serializer):
    """Respuesta al renovar la sesión."""

    access = serializers.CharField(help_text='Nuevo token de acceso.')


class CierreSesionExitosoSerializer(serializers.Serializer):
    """Respuesta al cerrar la sesión."""

    mensaje = serializers.CharField(help_text='Mensaje de confirmación.')
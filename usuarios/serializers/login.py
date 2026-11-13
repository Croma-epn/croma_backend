from rest_framework import serializers

from usuarios import mensajes

from .comunes import CORREO_MAX_LENGTH, mensajes_campo_vacio


class LoginSerializer(serializers.Serializer):
    """Credenciales para iniciar sesión."""

    # Solo valida el FORMATO (HU02 CC2, CC3, CC4).
    # Comprobar que la cuenta existe y que la contraseña es correcta (CC5) lo hace el servicio.
    # A propósito NO hay longitud mínima en la contraseña: eso es una regla para crearla
    # (registro). Al iniciar sesión basta con que no esté vacía; si es incorrecta, responde 401.

    correo = serializers.EmailField(
        max_length=CORREO_MAX_LENGTH,
        help_text='Correo electrónico con el que se registró la cuenta.',
        error_messages={
            'required': mensajes.CORREO_OBLIGATORIO,
            'null': mensajes.CORREO_OBLIGATORIO,
            'blank': mensajes.CORREO_OBLIGATORIO,
            'invalid': mensajes.CORREO_INVALIDO,
            'max_length': mensajes.CORREO_INVALIDO,
        },
    )

    contrasena = serializers.CharField(
        write_only=True,
        trim_whitespace=False,  # Los espacios pueden ser parte de la contraseña: no se tocan
        style={'input_type': 'password'},
        help_text='Contraseña de la cuenta.',
        error_messages=mensajes_campo_vacio(mensajes.CONTRASENA_OBLIGATORIA),
    )

    def validate_correo(self, value):
        # Mismo criterio que el modelo y el registro: en minúsculas.
        return value.lower()
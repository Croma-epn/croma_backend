from rest_framework import serializers

from usuarios import mensajes

NOMBRE_MAX_LENGTH = 100      # Debe coincidir con Usuario.nombre (max_length del modelo)
CORREO_MAX_LENGTH = 254      # Debe coincidir con Usuario.correo
CONTRASENA_MIN_LENGTH = 6    # Regla del CC7


# IMPORTANTE: el docstring de cada serializer, los help_text y los ejemplos se publican
# en Swagger. Ahí solo va texto pensado para quien consume la API. Las notas internas
# (criterios de aceptación, decisiones del equipo) van en comentarios con "#".


def _mensajes_campo_vacio(mensaje):
    """
    Un campo puede venir "vacío" de cuatro maneras: no enviado (required),
    null, cadena vacía o solo espacios (blank), o con un tipo raro (invalid).
    Todas devuelven el mismo mensaje del CC.
    """
    return {
        'required': mensaje,
        'null': mensaje,
        'blank': mensaje,
        'invalid': mensaje,
    }


class RegistroUsuarioSerializer(serializers.Serializer):
    """Datos para crear una cuenta."""

    # Solo valida el FORMATO (CC3, CC4, CC5, CC7, CC9).
    # Las reglas de negocio (correo ya registrado, CC6) las resuelve el servicio.

    nombre = serializers.CharField(
        max_length=NOMBRE_MAX_LENGTH,
        help_text='Nombre completo. Máximo 100 caracteres.',
        error_messages={
            **_mensajes_campo_vacio(mensajes.NOMBRE_OBLIGATORIO),
            'max_length': mensajes.NOMBRE_MUY_LARGO,
        },
    )

    correo = serializers.EmailField(
        max_length=CORREO_MAX_LENGTH,
        help_text='Correo electrónico. Se guarda en minúsculas.',
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
        min_length=CONTRASENA_MIN_LENGTH,
        style={'input_type': 'password'},
        help_text='Contraseña de al menos 6 caracteres.',
        error_messages={
            **_mensajes_campo_vacio(mensajes.CONTRASENA_CORTA),
            'min_length': mensajes.CONTRASENA_CORTA,
        },
    )

    def validate_correo(self, value):
        # Mismo criterio que el modelo: sin espacios (ya recortados por DRF) y en minúsculas.
        return value.lower()


class UsuarioRegistradoSerializer(serializers.Serializer):
    """Datos del usuario creado."""

    # Nunca incluye la contraseña.

    id = serializers.IntegerField(read_only=True, help_text='Identificador del usuario.')
    nombre = serializers.CharField(read_only=True, help_text='Nombre completo.')
    correo = serializers.EmailField(read_only=True, help_text='Correo electrónico, en minúsculas.')


class RegistroExitosoSerializer(serializers.Serializer):
    """Respuesta al crear la cuenta."""

    # Solo documenta la forma del JSON en Swagger: la view arma la respuesta a mano.

    mensaje = serializers.CharField(help_text='Mensaje de confirmación.')
    usuario = UsuarioRegistradoSerializer(help_text='Datos del usuario creado.')
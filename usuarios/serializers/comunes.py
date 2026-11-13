from rest_framework import serializers

CORREO_MAX_LENGTH = 254  # Debe coincidir con Usuario.correo


# IMPORTANTE: el docstring de cada serializer, los help_text y los ejemplos se publican
# en Swagger. Ahí solo va texto pensado para quien consume la API. Las notas internas
# (criterios de aceptación, decisiones del equipo) van en comentarios con "#".


def mensajes_campo_vacio(mensaje):
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


class UsuarioSerializer(serializers.Serializer):
    """Datos públicos del usuario."""

    # Nunca incluye la contraseña.

    id = serializers.IntegerField(read_only=True, help_text='Identificador del usuario.')
    nombre = serializers.CharField(read_only=True, help_text='Nombre completo.')
    correo = serializers.EmailField(read_only=True, help_text='Correo electrónico, en minúsculas.')
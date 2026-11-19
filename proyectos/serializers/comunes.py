from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

# IMPORTANTE: el docstring de cada serializer, los help_text y los ejemplos se publican
# en Swagger. Ahí solo va texto pensado para quien consume la API. Las notas internas
# (criterios de aceptación, decisiones del equipo) van en comentarios con "#".


class ProyectoSerializer(serializers.Serializer):
    """Datos de un proyecto."""

    id = serializers.IntegerField(read_only=True, help_text='Identificador del proyecto.')
    nombre = serializers.CharField(read_only=True, help_text='Nombre del proyecto.')
    descripcion = serializers.CharField(read_only=True, help_text='Descripción del proyecto. Vacía si no se escribió.')
    portada = serializers.SerializerMethodField(
        help_text='Dirección (URL) de la imagen de portada, o null si el proyecto no tiene portada.',
    )
    creado_en = serializers.DateTimeField(read_only=True, help_text='Fecha y hora de creación (ISO 8601).')

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_portada(self, proyecto):
        # En la base de datos "sin portada" es un texto vacío; hacia afuera se informa null.
        return proyecto.portada_url or None
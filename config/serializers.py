from rest_framework import serializers


class ErrorSerializer(serializers.Serializer):
    """Forma de todas las respuestas de error."""

    # Solo documenta en Swagger: no valida ni genera nada en tiempo de ejecución.
    # La respuesta real la arma config/exceptions.py; si ese formato cambia,
    # este serializer debe actualizarse.

    mensaje = serializers.CharField(help_text='Texto general del error.')
    errores = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField()),
        help_text='Mensajes agrupados por campo. Queda vacío si el error no pertenece a un campo.',
    )
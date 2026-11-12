from rest_framework import status
from rest_framework.exceptions import APIException

from usuarios import mensajes


class CorreoYaRegistrado(APIException):
    """El correo ya tiene una cuenta (CC6). DRF la convierte automáticamente en una respuesta 409."""

    status_code = status.HTTP_409_CONFLICT
    # Diccionario con el campo: así el front muestra el mensaje bajo el input del correo.
    default_detail = {'correo': [mensajes.CORREO_YA_REGISTRADO]}
    default_code = 'correo_ya_registrado'
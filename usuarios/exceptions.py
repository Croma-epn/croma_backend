from rest_framework import status
from rest_framework.exceptions import APIException

from usuarios import mensajes


class CorreoYaRegistrado(APIException):
    """El correo ya tiene una cuenta (CC6). DRF la convierte automáticamente en una respuesta 409."""

    status_code = status.HTTP_409_CONFLICT
    # Con forma de diccionario para que el error quede asociado al campo "correo".
    default_detail = {'correo': [mensajes.CORREO_YA_REGISTRADO]}
    default_code = 'correo_ya_registrado'


class CredencialesIncorrectas(APIException):
    """
    Correo no registrado, contraseña incorrecta o cuenta inactiva (HU02 CC5).
    DRF la convierte automáticamente en una respuesta 401.
    """

    # Un solo error para los tres casos: así la API no revela qué correos tienen cuenta.
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = mensajes.CREDENCIALES_INCORRECTAS
    default_code = 'credenciales_incorrectas'


class SesionExpirada(APIException):
    """El refresh token falta, venció, fue alterado o ya se usó. Responde 401."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = mensajes.SESION_EXPIRADA
    default_code = 'sesion_expirada'
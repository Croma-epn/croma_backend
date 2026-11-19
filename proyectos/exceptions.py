from rest_framework import status
from rest_framework.exceptions import APIException

from proyectos import mensajes


class ImagenNoGuardada(APIException):
    """
    El almacén de imágenes no respondió. DRF la convierte automáticamente en una respuesta 503.
    No se crea el proyecto: el estudiante puede reintentar sin que quede nada a medias.
    """

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = mensajes.IMAGEN_NO_GUARDADA
    default_code = 'imagen_no_guardada'
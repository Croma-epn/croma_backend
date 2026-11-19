from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.exceptions import MENSAJE_DATOS_INVALIDOS
from config.serializers import ErrorSerializer
from proyectos import mensajes
from proyectos.serializers import CreacionExitosaSerializer, CrearProyectoSerializer, ProyectoSerializer
from proyectos.services import crear_proyecto

# Todo lo que se pasa a @extend_schema (descripción, respuestas, ejemplos) se publica
# en Swagger: debe ser comprensible para quien consume la API, sin referencias internas.

DESCRIPCION = (
    'Crea un proyecto de modelado a nombre del usuario que tiene la sesión iniciada.\n\n'
    'Se envía como `multipart/form-data`: el nombre, la descripción (opcional) y la portada '
    '(opcional) viajan juntos en una sola petición. Para crear el proyecto sin portada, '
    'simplemente no se envía el campo `portada`. Si algo falla, no se crea nada.\n\n'
    'Requiere el token `access` en la cabecera `Authorization: Bearer <access>`.'
)


def _ejemplo_400(nombre, campo, mensaje):
    """Ejemplo de respuesta 400 para un campo con error."""
    return OpenApiExample(
        nombre,
        value={'mensaje': MENSAJE_DATOS_INVALIDOS, 'errores': {campo: [mensaje]}},
        response_only=True,
        status_codes=['400'],
    )


EJEMPLOS = [
    OpenApiExample(
        'Proyecto creado',
        value={
            'mensaje': mensajes.PROYECTO_CREADO,
            'proyecto': {
                'id': 7,
                'nombre': 'App de delivery',
                'descripcion': 'Pantallas para pedir comida',
                'portada': 'https://res.cloudinary.com/ejemplo/image/upload/proyectos/portadas/abc123.jpg',
                'creado_en': '2026-11-15T19:02:11Z',
            },
        },
        response_only=True,
        status_codes=['201'],
    ),
    OpenApiExample(
        'Proyecto creado sin portada',
        value={
            'mensaje': mensajes.PROYECTO_CREADO,
            'proyecto': {
                'id': 8,
                'nombre': 'App de delivery',
                'descripcion': '',
                'portada': None,
                'creado_en': '2026-11-15T19:05:40Z',
            },
        },
        response_only=True,
        status_codes=['201'],
    ),
    _ejemplo_400('Nombre vacío', 'nombre', mensajes.NOMBRE_OBLIGATORIO),
    _ejemplo_400('Nombre demasiado largo', 'nombre', mensajes.NOMBRE_MUY_LARGO),
    _ejemplo_400('Descripción demasiado larga', 'descripcion', mensajes.DESCRIPCION_MUY_LARGA),
    _ejemplo_400('Portada demasiado pesada', 'portada', mensajes.PORTADA_MUY_PESADA),
    _ejemplo_400('Portada que no es una imagen', 'portada', mensajes.PORTADA_NO_ES_IMAGEN),
    OpenApiExample(
        'No se pudo guardar la imagen',
        value={'mensaje': mensajes.IMAGEN_NO_GUARDADA, 'errores': {}},
        response_only=True,
        status_codes=['503'],
    ),
]


class CrearProyectoView(GenericAPIView):
    # POST /proyectos/: crea un proyecto del usuario con la sesión iniciada.

    serializer_class = CrearProyectoSerializer

    # Endpoint protegido. La autenticación (JWT) es la global de settings.py;
    # el permiso se declara aquí para que se lea sin tener que abrir ese archivo.
    permission_classes = [IsAuthenticated]

    # Esta API habla JSON, pero aquí viaja un archivo: se acepta multipart/form-data.
    parser_classes = [MultiPartParser]

    @extend_schema(
        operation_id='crear_proyecto',
        tags=['Proyectos'],
        summary='Crear proyecto',
        description=DESCRIPCION,
        request={'multipart/form-data': CrearProyectoSerializer},
        responses={
            201: OpenApiResponse(
                response=CreacionExitosaSerializer,
                description='Proyecto creado correctamente.',
            ),
            400: OpenApiResponse(
                response=ErrorSerializer,
                description='Datos inválidos. El detalle por campo viene en `errores`.',
            ),
            401: OpenApiResponse(
                response=ErrorSerializer,
                description='Falta el access token o no es válido.',
            ),
            503: OpenApiResponse(
                response=ErrorSerializer,
                description='No se pudo guardar la imagen. No se creó el proyecto; se puede reintentar.',
            ),
        },
        examples=EJEMPLOS,
    )
    def post(self, request):
        # 1) Formato de los datos. Si falla, DRF responde 400 con los mensajes de los CC.
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2) Crear el proyecto. El propietario es quien tiene la sesión, nunca lo que venga en la petición.
        proyecto = crear_proyecto(propietario=request.user, **serializer.validated_data)

        # 3) Respuesta de éxito.
        return Response(
            {
                'mensaje': mensajes.PROYECTO_CREADO,
                'proyecto': ProyectoSerializer(proyecto).data,
            },
            status=status.HTTP_201_CREATED,
        )
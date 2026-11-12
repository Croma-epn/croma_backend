from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from config.exceptions import MENSAJE_DATOS_INVALIDOS
from config.serializers import ErrorSerializer
from usuarios import mensajes
from usuarios.serializers import (
    RegistroExitosoSerializer,
    RegistroUsuarioSerializer,
    UsuarioRegistradoSerializer,
)
from usuarios.services import registrar_usuario

# Todo lo que se pasa a @extend_schema (descripción, respuestas, ejemplos) se publica
# en Swagger: debe ser comprensible para quien consume la API, sin referencias internas.

DESCRIPCION = (
    'Crea una cuenta nueva con nombre, correo electrónico y contraseña. '
    'El correo no puede estar registrado previamente.'
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
        'Registro válido',
        value={'nombre': 'Ana Pérez', 'correo': 'ana@ejemplo.com', 'contrasena': 'abc123'},
        request_only=True,
    ),
    OpenApiExample(
        'Cuenta creada',
        value={
            'mensaje': mensajes.CUENTA_CREADA,
            'usuario': {'id': 1, 'nombre': 'Ana Pérez', 'correo': 'ana@ejemplo.com'},
        },
        response_only=True,
        status_codes=['201'],
    ),
    _ejemplo_400('Nombre vacío', 'nombre', mensajes.NOMBRE_OBLIGATORIO),
    _ejemplo_400('Correo vacío', 'correo', mensajes.CORREO_OBLIGATORIO),
    _ejemplo_400('Correo con formato inválido', 'correo', mensajes.CORREO_INVALIDO),
    _ejemplo_400('Contraseña demasiado corta', 'contrasena', mensajes.CONTRASENA_CORTA),
    _ejemplo_400('Nombre demasiado largo', 'nombre', mensajes.NOMBRE_MUY_LARGO),
    OpenApiExample(
        'Correo ya registrado',
        value={
            'mensaje': mensajes.CORREO_YA_REGISTRADO,
            'errores': {'correo': [mensajes.CORREO_YA_REGISTRADO]},
        },
        response_only=True,
        status_codes=['409'],
    ),
]


class RegistroUsuarioView(GenericAPIView):
    # POST /usuarios/registro/: crea una cuenta nueva.

    serializer_class = RegistroUsuarioSerializer

    # Endpoint público: cualquiera puede registrarse, sin sesión ni token.
    # Se declara de forma explícita para que no cambie cuando el login (otra HU)
    # defina permisos o autenticación globales.
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        operation_id='registrar_usuario',
        tags=['Usuarios'],
        summary='Registrar usuario',
        description=DESCRIPCION,
        request=RegistroUsuarioSerializer,
        responses={
            201: OpenApiResponse(
                response=RegistroExitosoSerializer,
                description='Cuenta creada correctamente.',
            ),
            400: OpenApiResponse(
                response=ErrorSerializer,
                description='Datos inválidos. El detalle por campo viene en `errores`.',
            ),
            409: OpenApiResponse(
                response=ErrorSerializer,
                description='Ya existe una cuenta con ese correo.',
            ),
        },
        examples=EJEMPLOS,
    )
    def post(self, request):
        # 1) Formato de los datos. Si falla, DRF responde 400 con los mensajes de los CC.
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2) Regla de negocio. Si el correo ya existe, lanza CorreoYaRegistrado (409).
        usuario = registrar_usuario(**serializer.validated_data)

        # 3) Respuesta de éxito.
        return Response(
            {
                'mensaje': mensajes.CUENTA_CREADA,
                'usuario': UsuarioRegistradoSerializer(usuario).data,
            },
            status=status.HTTP_201_CREATED,
        )
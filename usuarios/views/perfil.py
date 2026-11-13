from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from config.serializers import ErrorSerializer
from usuarios import mensajes
from usuarios.serializers import UsuarioSerializer

# Todo lo que se pasa a @extend_schema (descripción, respuestas, ejemplos) se publica
# en Swagger: debe ser comprensible para quien consume la API, sin referencias internas.

DESCRIPCION = (
    'Devuelve los datos del usuario que tiene la sesión iniciada.\n\n'
    'Requiere el token `access` en la cabecera `Authorization: Bearer <access>`. '
    'Si el token falta, venció o fue alterado, responde 401: el front debe intentar '
    'renovar la sesión y, si eso también falla, llevar al usuario a iniciar sesión.'
)


class PerfilView(APIView):
    # GET /usuarios/yo/: datos del usuario autenticado.

    # Endpoint protegido. La autenticación (JWT) es la global de settings.py;
    # el permiso se declara aquí para que se lea sin tener que abrir ese archivo.
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id='consultar_perfil',
        tags=['Usuarios'],
        summary='Consultar perfil',
        description=DESCRIPCION,
        responses={
            200: OpenApiResponse(
                response=UsuarioSerializer,
                description='Datos del usuario autenticado.',
            ),
            401: OpenApiResponse(
                response=ErrorSerializer,
                description='Falta el access token o no es válido.',
            ),
        },
        examples=[
            OpenApiExample(
                'Perfil',
                value={'id': 1, 'nombre': 'Ana Pérez', 'correo': 'ana@ejemplo.com'},
                response_only=True,
                status_codes=['200'],
            ),
            OpenApiExample(
                'Sin sesión',
                value={'mensaje': mensajes.SESION_EXPIRADA, 'errores': {}},
                response_only=True,
                status_codes=['401'],
            ),
        ],
    )
    def get(self, request):
        # request.user ya es el usuario dueño del token: lo resolvió JWTAuthentication.
        return Response(UsuarioSerializer(request.user).data)
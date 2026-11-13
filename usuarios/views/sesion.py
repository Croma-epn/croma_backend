from django.conf import settings
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from config.exceptions import MENSAJE_DATOS_INVALIDOS
from config.serializers import ErrorSerializer
from usuarios import mensajes
from usuarios.serializers import (
    CierreSesionExitosoSerializer,
    LoginExitosoSerializer,
    LoginSerializer,
    RenovarSesionExitosoSerializer,
    UsuarioSerializer,
)
from usuarios.services import cerrar_sesion, iniciar_sesion, renovar_sesion

from .cookies import borrar_cookie_refresh, leer_cookie_refresh, poner_cookie_refresh

# Todo lo que se pasa a @extend_schema (descripción, respuestas, ejemplos) se publica
# en Swagger: debe ser comprensible para quien consume la API, sin referencias internas.

TAG = 'Autenticación'
COOKIE = settings.REFRESH_COOKIE_NAME

ACCESS_EJEMPLO = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.firma'


def _ejemplo_400(nombre, campo, mensaje):
    """Ejemplo de respuesta 400 para un campo con error."""
    return OpenApiExample(
        nombre,
        value={'mensaje': MENSAJE_DATOS_INVALIDOS, 'errores': {campo: [mensaje]}},
        response_only=True,
        status_codes=['400'],
    )


# ---------------------------------------------------------------------------
# Inicio de sesión
# ---------------------------------------------------------------------------

DESCRIPCION_LOGIN = (
    'Inicia sesión con correo y contraseña.\n\n'
    'Devuelve los datos del usuario y un token `access` de corta duración, que se envía '
    'en la cabecera `Authorization: Bearer <access>` de las peticiones que requieren sesión.\n\n'
    f'El token de renovación (refresh) **no** viaja en el cuerpo: se entrega en la cookie '
    f'`{COOKIE}` (HttpOnly, inaccesible para JavaScript). Por eso el front debe enviar las '
    'peticiones con `credentials: "include"`.\n\n'
    'El error 401 es el mismo si el correo no está registrado, la contraseña es incorrecta '
    'o la cuenta está inactiva.'
)

EJEMPLOS_LOGIN = [
    OpenApiExample(
        'Inicio de sesión válido',
        value={'correo': 'ana@ejemplo.com', 'contrasena': 'abc123'},
        request_only=True,
    ),
    OpenApiExample(
        'Sesión iniciada',
        value={
            'mensaje': mensajes.SESION_INICIADA,
            'usuario': {'id': 1, 'nombre': 'Ana Pérez', 'correo': 'ana@ejemplo.com'},
            'access': ACCESS_EJEMPLO,
        },
        response_only=True,
        status_codes=['200'],
    ),
    _ejemplo_400('Correo vacío', 'correo', mensajes.CORREO_OBLIGATORIO),
    _ejemplo_400('Correo con formato inválido', 'correo', mensajes.CORREO_INVALIDO),
    _ejemplo_400('Contraseña vacía', 'contrasena', mensajes.CONTRASENA_OBLIGATORIA),
    OpenApiExample(
        'Credenciales incorrectas',
        value={'mensaje': mensajes.CREDENCIALES_INCORRECTAS, 'errores': {}},
        response_only=True,
        status_codes=['401'],
    ),
]


class LoginView(GenericAPIView):
    # POST /usuarios/login/: inicia sesión.

    serializer_class = LoginSerializer

    # Endpoint público: se llama justamente para obtener una sesión.
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        operation_id='iniciar_sesion',
        tags=[TAG],
        summary='Iniciar sesión',
        description=DESCRIPCION_LOGIN,
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                response=LoginExitosoSerializer,
                description='Sesión iniciada. El refresh token llega en una cookie HttpOnly.',
            ),
            400: OpenApiResponse(
                response=ErrorSerializer,
                description='Datos inválidos. El detalle por campo viene en `errores`.',
            ),
            401: OpenApiResponse(
                response=ErrorSerializer,
                description='No existe una cuenta con esos datos o la contraseña es incorrecta.',
            ),
        },
        examples=EJEMPLOS_LOGIN,
    )
    def post(self, request):
        # 1) Formato de los datos. Si falla, DRF responde 400 con los mensajes de los CC.
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2) Regla de negocio. Si las credenciales no coinciden, lanza CredencialesIncorrectas (401).
        sesion = iniciar_sesion(**serializer.validated_data)

        # 3) Respuesta: el access va en el cuerpo y el refresh en una cookie HttpOnly.
        response = Response(
            {
                'mensaje': mensajes.SESION_INICIADA,
                'usuario': UsuarioSerializer(sesion.usuario).data,
                'access': sesion.access,
            }
        )
        poner_cookie_refresh(response, sesion.refresh)
        return response


# ---------------------------------------------------------------------------
# Renovación de la sesión
# ---------------------------------------------------------------------------

DESCRIPCION_RENOVAR = (
    'Renueva la sesión usando el refresh token de la cookie '
    f'`{COOKIE}`, sin que el usuario vuelva a escribir su contraseña.\n\n'
    'Devuelve un `access` nuevo y establece una cookie nueva: el refresh token es de un '
    'solo uso, así que el anterior deja de servir.\n\n'
    'Responde 401 si la cookie no existe, venció, fue alterada o ya se usó. En ese caso el '
    'usuario debe iniciar sesión de nuevo.'
)


class RenovarSesionView(APIView):
    # POST /usuarios/token/refresh/: cambia el refresh token por un par de tokens nuevo.

    # No se pide access token (justamente venció): la credencial es la cookie,
    # que valida el servicio.
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        operation_id='renovar_sesion',
        tags=[TAG],
        summary='Renovar sesión',
        description=DESCRIPCION_RENOVAR,
        request=None,
        responses={
            200: OpenApiResponse(
                response=RenovarSesionExitosoSerializer,
                description='Access token nuevo. El refresh token nuevo llega en la cookie.',
            ),
            401: OpenApiResponse(
                response=ErrorSerializer,
                description='La sesión expiró o el refresh token no es válido.',
            ),
        },
        examples=[
            OpenApiExample(
                'Sesión renovada',
                value={'access': ACCESS_EJEMPLO},
                response_only=True,
                status_codes=['200'],
            ),
            OpenApiExample(
                'Sesión expirada',
                value={'mensaje': mensajes.SESION_EXPIRADA, 'errores': {}},
                response_only=True,
                status_codes=['401'],
            ),
        ],
    )
    def post(self, request):
        # Si el refresh falta o no sirve, el servicio lanza SesionExpirada (401).
        sesion = renovar_sesion(refresh_token=leer_cookie_refresh(request))

        response = Response({'access': sesion.access})
        poner_cookie_refresh(response, sesion.refresh)  # Reemplaza la cookie anterior
        return response


# ---------------------------------------------------------------------------
# Cierre de sesión
# ---------------------------------------------------------------------------

DESCRIPCION_LOGOUT = (
    'Cierra la sesión: invalida el refresh token de la cookie '
    f'`{COOKIE}` y la elimina del navegador.\n\n'
    'Siempre responde 200, incluso si no había una sesión iniciada. Después de cerrar '
    'sesión, el front debe descartar el access token que tenga en memoria.'
)


class LogoutView(APIView):
    # POST /usuarios/logout/: cierra la sesión.

    # Cerrar sesión es idempotente: sin sesión activa también responde 200.
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        operation_id='cerrar_sesion',
        tags=[TAG],
        summary='Cerrar sesión',
        description=DESCRIPCION_LOGOUT,
        request=None,
        responses={
            200: OpenApiResponse(
                response=CierreSesionExitosoSerializer,
                description='Sesión cerrada. La cookie del refresh token se elimina.',
            ),
        },
        examples=[
            OpenApiExample(
                'Sesión cerrada',
                value={'mensaje': mensajes.SESION_CERRADA},
                response_only=True,
                status_codes=['200'],
            ),
        ],
    )
    def post(self, request):
        cerrar_sesion(refresh_token=leer_cookie_refresh(request))

        response = Response({'mensaje': mensajes.SESION_CERRADA})
        borrar_cookie_refresh(response)
        return response
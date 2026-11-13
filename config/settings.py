"""
Configuración de Django para el backend de Croma.
"""

import os
from datetime import timedelta
from importlib.util import find_spec
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Carga las variables del archivo .env (si existe) dentro de os.environ.
load_dotenv(BASE_DIR / '.env')


def required_env(name):
    """Devuelve la variable de entorno o detiene el arranque con un mensaje claro."""
    value = os.environ.get(name)
    if not value:
        raise ImproperlyConfigured(
            f'Falta la variable de entorno {name}. Revisa tu archivo .env.'
        )
    return value


def env_list(name, default=''):
    """Lee una variable separada por comas y la devuelve como lista."""
    return [item.strip() for item in os.environ.get(name, default).split(',') if item.strip()]


# ---------------------------------------------------------------------------
# Seguridad
# ---------------------------------------------------------------------------

# Sin valor por defecto: si falta, Django no arranca (mejor eso que arrancar inseguro).
SECRET_KEY = required_env('SECRET_KEY')

# Por defecto False: DEBUG solo se activa de forma explícita (DEBUG=True en tu .env local).
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', 'localhost,127.0.0.1')

# Orígenes (con https://) desde los que se aceptan formularios, por ejemplo el login del admin.
# Normalmente no hace falta, porque Django ya acepta el propio host. Es una red de seguridad.
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')

# Con DEBUG=False (producción) se exige HTTPS en todo.
if not DEBUG:
    # Heroku termina el HTTPS en su balanceador y reenvía la petición a Django por HTTP,
    # avisando con esta cabecera. Sin esto Django creería que todo es HTTP y entraría
    # en un bucle de redirecciones.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True           # http:// redirige a https://
    SESSION_COOKIE_SECURE = True         # Las cookies solo viajan por HTTPS
    CSRF_COOKIE_SECURE = True
    # HSTS: el navegador recuerda usar siempre HTTPS. Se empieza con 1 hora para poder
    # corregir errores; cuando todo funcione se sube (por ejemplo a 31536000 = 1 año).
    SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '3600'))


# ---------------------------------------------------------------------------
# Aplicaciones
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Terceros
    'rest_framework',     # Construcción de la API
    'corsheaders',        # Peticiones desde el front (otro origen)
    'drf_spectacular',    # Documentación OpenAPI / Swagger
    'rest_framework_simplejwt.token_blacklist',  # Lista negra de refresh tokens (cierre de sesión)
    # Propias
    'usuarios',
]

# behave-django solo está en requirements-dev.txt (no se instala en producción).
# Se activa únicamente si el paquete existe en el entorno.
if find_spec('behave_django') is not None:
    INSTALLED_APPS.append('behave_django')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Debe ir antes de WhiteNoise y CommonMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# El admin de Django necesita el motor de plantillas, aunque la API no use plantillas.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# ---------------------------------------------------------------------------
# Base de datos (PostgreSQL)
# ---------------------------------------------------------------------------

if os.environ.get('DATABASE_URL'):
    # Producción (Heroku): el add-on de Postgres entrega toda la conexión en DATABASE_URL.
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,         # Reutiliza conexiones 10 minutos (el plan permite pocas)
            conn_health_checks=True,  # Descarta una conexión cortada antes de usarla
            ssl_require=True,         # Heroku Postgres exige conexión cifrada
        )
    }
else:
    # Local: variables DB_* del archivo .env.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': required_env('DB_NAME'),
            'USER': os.environ.get('DB_USER') or 'postgres',
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            # "or" (y no get con default): si la variable existe pero está vacía,
            # get() devolvería '' y el default nunca se aplicaría.
            'HOST': os.environ.get('DB_HOST') or 'localhost',
            'PORT': os.environ.get('DB_PORT') or '5432',
        }
    }


# ---------------------------------------------------------------------------
# Contraseñas
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = []
AUTH_USER_MODEL = 'usuarios.Usuario'


# ---------------------------------------------------------------------------
# Internacionalización
# ---------------------------------------------------------------------------

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True  # La BD guarda las fechas en UTC; TIME_ZONE solo afecta cómo se muestran.


# ---------------------------------------------------------------------------
# Archivos estáticos
# ---------------------------------------------------------------------------

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------------------------------------------------------------------
# CORS (peticiones desde el front)
# ---------------------------------------------------------------------------

# En desarrollo (DEBUG=True) se permite cualquier origen.
# En producción solo los listados en CORS_ALLOWED_ORIGINS (separados por comas).
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = env_list('CORS_ALLOWED_ORIGINS')

# Permite que el navegador envíe y reciba cookies en peticiones desde el front
# (el refresh token viaja en una cookie). El front debe usar credentials: 'include'.
CORS_ALLOW_CREDENTIALS = True


# ---------------------------------------------------------------------------
# Django REST Framework y Swagger
# ---------------------------------------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_PARSER_CLASSES': ['rest_framework.parsers.JSONParser'],
    'EXCEPTION_HANDLER': 'config.exceptions.manejador_de_errores',
    # Quién eres: se lee el access token de la cabecera "Authorization: Bearer <token>".
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    # Qué puedes hacer: por defecto TODO endpoint exige sesión iniciada.
    # Los públicos (registro, login...) lo declaran explícitamente con AllowAny.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


# ---------------------------------------------------------------------------
# Tokens de sesión (JWT)
# ---------------------------------------------------------------------------

SIMPLE_JWT = {
    # Access token: se envía en cada petición. Dura poco para limitar el daño si se filtra.
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    # Refresh token: solo sirve para pedir un access nuevo. Define cuánto dura la sesión
    # sin volver a escribir la contraseña.
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    # La rotación (un refresh de un solo uso, con lista negra) la hace el servicio
    # usuarios/services/sesion.py de forma explícita.
}

# Cookie que transporta el refresh token. La crea y la borra el back; el front no la toca
# (JavaScript no puede leerla porque es HttpOnly).
REFRESH_COOKIE_NAME = 'croma_refresh'
REFRESH_COOKIE_PATH = '/usuarios/'      # Solo se envía a las rutas de /usuarios/
REFRESH_COOKIE_SECURE = not DEBUG       # En producción solo viaja por HTTPS
REFRESH_COOKIE_SAMESITE = 'Lax'         # No se envía desde otros sitios: protege contra CSRF

SPECTACULAR_SETTINGS = {
    'TITLE': 'Croma API',
    'DESCRIPTION': (
        'Documentación oficial del backend del proyecto Croma.\n\n'
        # '**Formato de errores.** Toda respuesta de error tiene la forma '
        # '`{"mensaje": "...", "errores": {"campo": ["..."]}}`. '
        # '`errores` siempre existe y queda vacío cuando el error no pertenece a un campo.'
    ),
    'VERSION': '1.0.0',
    # Sin 'SERVERS': Swagger usa el mismo host desde el que se abre la documentación,
    # así que "Try it out" funciona en local y en producción sin editar nada.
    'SERVE_INCLUDE_SCHEMA': False,  # Quita el enlace /schema/ dentro del propio esquema

}
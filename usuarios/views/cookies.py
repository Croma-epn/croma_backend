from django.conf import settings
from rest_framework_simplejwt.settings import api_settings


def poner_cookie_refresh(response, refresh_token):
    """Guarda el refresh token en una cookie que JavaScript no puede leer (HttpOnly)."""
    response.set_cookie(
        settings.REFRESH_COOKIE_NAME,
        refresh_token,
        # La cookie vive lo mismo que el refresh token.
        max_age=int(api_settings.REFRESH_TOKEN_LIFETIME.total_seconds()),
        path=settings.REFRESH_COOKIE_PATH,
        secure=settings.REFRESH_COOKIE_SECURE,
        httponly=True,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
    )


def borrar_cookie_refresh(response):
    """Pide al navegador que elimine la cookie. Debe usar el mismo path con el que se creó."""
    response.delete_cookie(
        settings.REFRESH_COOKIE_NAME,
        path=settings.REFRESH_COOKIE_PATH,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
    )


def leer_cookie_refresh(request):
    """Devuelve el refresh token que envió el navegador, o None si no hay."""
    return request.COOKIES.get(settings.REFRESH_COOKIE_NAME)
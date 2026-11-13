from typing import NamedTuple

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from usuarios.exceptions import CredencialesIncorrectas, SesionExpirada
from usuarios.models import Usuario


class Sesion(NamedTuple):
    """Resultado de iniciar o renovar una sesión: el usuario y su par de tokens."""

    usuario: Usuario
    access: str
    refresh: str


def _emitir_tokens(usuario):
    """Crea un par de tokens nuevo para el usuario."""
    refresh = RefreshToken.for_user(usuario)  # Además lo registra como "vigente" en la BD
    return Sesion(usuario, str(refresh.access_token), str(refresh))


def iniciar_sesion(*, correo, contrasena):
    """
    Verifica las credenciales (HU02 CC1) y devuelve la Sesion con sus tokens.
    Lanza CredencialesIncorrectas si algo no coincide (CC5).

    No valida formato (eso es del serializer) ni sabe nada de HTTP ni de cookies.
    """
    # No se confía en que quien llame ya normalizó el correo.
    correo = correo.strip().lower()

    # authenticate() busca al usuario por correo y compara la contraseña con el hash.
    # Devuelve None si el correo no existe, la contraseña no coincide o la cuenta está
    # inactiva. Los tres casos terminan igual a propósito.
    usuario = authenticate(correo=correo, password=contrasena)
    if usuario is None:
        raise CredencialesIncorrectas()

    update_last_login(None, usuario)  # Guarda la fecha de este inicio de sesión
    return _emitir_tokens(usuario)


def renovar_sesion(*, refresh_token):
    """
    Cambia un refresh token válido por un par de tokens nuevo.
    Lanza SesionExpirada si el token falta o ya no sirve.

    El refresh token es de UN SOLO USO: al renovar, el anterior queda invalidado
    (lista negra). Así, un refresh robado deja de servir en cuanto el dueño legítimo
    renueva su sesión.
    """
    if not refresh_token:
        raise SesionExpirada()

    try:
        # Al crear el objeto, la librería comprueba: firma, vencimiento, que sea de tipo
        # refresh (no un access) y que no esté en la lista negra.
        token = RefreshToken(refresh_token)
    except TokenError:
        raise SesionExpirada()

    # El usuario pudo desactivarse o borrarse después de emitirse el token.
    usuario = Usuario.objects.filter(
        pk=token.payload.get(api_settings.USER_ID_CLAIM),
        is_active=True,
    ).first()
    if usuario is None:
        raise SesionExpirada()

    token.blacklist()  # El refresh usado deja de servir
    return _emitir_tokens(usuario)


def cerrar_sesion(*, refresh_token):
    """
    Invalida el refresh token (HU02 CC8). No devuelve nada.

    Es idempotente: si no hay token, o ya venció, o ya estaba invalidado, no hay nada
    que cerrar y termina igual, sin error. Así el front siempre puede limpiar su estado.
    """
    if not refresh_token:
        return
    try:
        RefreshToken(refresh_token).blacklist()
    except TokenError:
        pass
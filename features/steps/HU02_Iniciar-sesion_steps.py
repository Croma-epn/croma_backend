from behave import given, then, when
from rest_framework.test import APIClient

from usuarios.models import Usuario

# El contrato de la API (rutas y nombre de la cookie) queda fijado aquí, en las pruebas.
URL_LOGIN = '/usuarios/login/'
URL_RENOVAR = '/usuarios/token/refresh/'
URL_LOGOUT = '/usuarios/logout/'
URL_PERFIL = '/usuarios/yo/'
COOKIE_REFRESH = 'croma_refresh'

CLAVE = 'Password123'


# ---------------------------------------------------------------------------
# Apoyo
# ---------------------------------------------------------------------------

def navegador(context):
    """
    Un cliente por escenario. Guarda las cookies entre peticiones, igual que el navegador:
    la cookie del refresh token que entrega el login se reenvía sola en la siguiente petición.
    """
    if 'navegador' not in context:
        context.navegador = APIClient()
    return context.navegador


def cuerpo(context):
    return context.response.json()


def recordar_sesion(context):
    """Guarda los tokens de una respuesta exitosa para los pasos que los necesiten."""
    datos = cuerpo(context)
    context.access = datos.get('access')
    cookie = context.response.cookies.get(COOKIE_REFRESH)
    if cookie is not None and cookie.value:
        context.refresh_actual = cookie.value


def enviar_login(context, payload):
    context.payload = payload
    context.response = navegador(context).post(URL_LOGIN, payload, format='json')
    if context.response.status_code == 200:
        recordar_sesion(context)
        # El refresh con el que se inició sesión: sirve para probar que, tras
        # renovar o cerrar sesión, esa copia anterior queda inválida.
        context.refresh_de_login = context.refresh_actual


# ---------------------------------------------------------------------------
# Dado
# ---------------------------------------------------------------------------

@given('que existe una cuenta registrada con el correo "{correo}" y la contraseña "{contrasena}"')
def paso_cuenta_con_clave(context, correo, contrasena):
    Usuario.objects.create_user(correo=correo, password=contrasena, nombre='Usuario de Prueba')


@given('que existe una cuenta inactiva con el correo "{correo}" y la contraseña "{contrasena}"')
def paso_cuenta_inactiva(context, correo, contrasena):
    Usuario.objects.create_user(
        correo=correo, password=contrasena, nombre='Usuario Inactivo', is_active=False,
    )


@given('que el estudiante tiene una sesión iniciada con el correo "{correo}"')
def paso_sesion_iniciada(context, correo):
    Usuario.objects.create_user(correo=correo, password=CLAVE, nombre='Usuario de Prueba')
    enviar_login(context, {'correo': correo, 'contrasena': CLAVE})
    assert context.response.status_code == 200, (
        f'No se pudo iniciar sesión en el paso previo: {context.response.content.decode()}'
    )


# ---------------------------------------------------------------------------
# Cuando
# ---------------------------------------------------------------------------

@when('envía una petición de inicio de sesión con el correo "{correo}" y la contraseña "{contrasena}"')
def paso_login_con_datos(context, correo, contrasena):
    enviar_login(context, {'correo': correo, 'contrasena': contrasena})


@when('envía una petición de inicio de sesión con los siguientes datos:')
def paso_login_con_tabla(context):
    # Cada columna de la tabla es un campo del JSON. Si una columna no está,
    # el campo no se envía (sirve para probar campos ausentes).
    fila = context.table[0]
    enviar_login(context, dict(zip(context.table.headings, fila.cells)))


@when('consulta su perfil con el access token')
def paso_perfil_con_token(context):
    context.response = navegador(context).get(
        URL_PERFIL, HTTP_AUTHORIZATION=f'Bearer {context.access}',
    )


@when('consulta su perfil sin enviar un access token')
def paso_perfil_sin_token(context):
    context.response = navegador(context).get(URL_PERFIL)


@when('consulta su perfil con un access token alterado')
def paso_perfil_token_alterado(context):
    cabecera, contenido, firma = context.access.split('.')
    # Se cambia el primer carácter de la firma: así deja de coincidir con el contenido.
    firma = ('A' if firma[0] != 'A' else 'B') + firma[1:]
    alterado = '.'.join([cabecera, contenido, firma])
    context.response = navegador(context).get(URL_PERFIL, HTTP_AUTHORIZATION=f'Bearer {alterado}')


@when('solicita renovar la sesión')
def paso_renovar(context):
    context.access_previo = context.access
    context.response = navegador(context).post(URL_RENOVAR, {}, format='json')
    if context.response.status_code == 200:
        recordar_sesion(context)


@when('solicita renovar la sesión sin tener una sesión iniciada')
def paso_renovar_sin_sesion(context):
    context.response = APIClient().post(URL_RENOVAR, {}, format='json')


@when('solicita renovar la sesión con el refresh token anterior')
def paso_renovar_con_refresh_anterior(context):
    # Un navegador distinto que presenta el refresh token con el que se inició sesión.
    otro = APIClient()
    otro.cookies[COOKIE_REFRESH] = context.refresh_de_login
    context.response = otro.post(URL_RENOVAR, {}, format='json')


@when('cierra sesión')
def paso_cerrar_sesion(context):
    context.response = navegador(context).post(URL_LOGOUT, {}, format='json')


@when('cierra sesión sin tener una sesión iniciada')
def paso_cerrar_sesion_sin_sesion(context):
    context.response = APIClient().post(URL_LOGOUT, {}, format='json')


# ---------------------------------------------------------------------------
# Entonces
# ---------------------------------------------------------------------------
# Los pasos de código HTTP, mensaje y error por campo se reutilizan de la HU01.

@then('la respuesta incluye el id, el nombre y el correo del usuario')
def paso_datos_usuario(context):
    usuario = cuerpo(context).get('usuario')
    assert isinstance(usuario, dict), f'Falta el objeto "usuario": {cuerpo(context)}'
    faltan = {'id', 'nombre', 'correo'} - set(usuario)
    assert not faltan, f'Al usuario le faltan campos: {faltan}'


@then('la respuesta no incluye la contraseña del usuario')
def paso_sin_contrasena(context):
    texto = context.response.content.decode('utf-8').lower()
    for prohibido in ('password', 'contrasena', 'pbkdf2'):
        assert prohibido not in texto, f'La respuesta expone "{prohibido}": {texto}'


@then('la respuesta incluye un access token')
def paso_access_token(context):
    access = cuerpo(context).get('access')
    assert isinstance(access, str) and access.count('.') == 2, (
        f'Se esperaba un access token (JWT) y se recibió: {access}'
    )


@then('el refresh token no viaja en el cuerpo de la respuesta')
def paso_refresh_fuera_del_cuerpo(context):
    assert 'refresh' not in cuerpo(context), 'El refresh token no debe ir en el cuerpo.'


@then('el refresh token se entrega en una cookie HttpOnly')
def paso_cookie_httponly(context):
    cookie = context.response.cookies.get(COOKIE_REFRESH)
    assert cookie is not None and cookie.value, f'No llegó la cookie "{COOKIE_REFRESH}".'
    assert cookie['httponly'], 'La cookie debe ser HttpOnly (inaccesible para JavaScript).'
    assert cookie['samesite'] == 'Lax', 'La cookie debe ser SameSite=Lax.'
    assert cookie['path'] == '/usuarios/', 'La cookie solo debe enviarse a /usuarios/.'


@then('no se entrega ningún token ni cookie de sesión')
def paso_sin_tokens(context):
    assert 'access' not in cuerpo(context), 'No debía entregarse un access token.'
    assert COOKIE_REFRESH not in context.response.cookies, 'No debía entregarse la cookie.'


@then('la respuesta identifica al usuario con el correo "{correo}"')
def paso_perfil_correo(context, correo):
    recibido = cuerpo(context).get('correo')
    assert recibido == correo, f'Se esperaba el correo "{correo}" y se recibió "{recibido}".'


@then('la cookie del refresh token se elimina')
def paso_cookie_eliminada(context):
    cookie = context.response.cookies.get(COOKIE_REFRESH)
    assert cookie is not None, 'La respuesta debía indicar que se borra la cookie.'
    assert cookie.value == '', 'La cookie debía quedar vacía.'
    assert str(cookie['max-age']) == '0', 'La cookie debía expirar de inmediato.'


@then('la respuesta incluye un access token nuevo')
def paso_access_nuevo(context):
    nuevo = cuerpo(context).get('access')
    assert nuevo and nuevo != context.access_previo, 'Se esperaba un access token distinto al anterior.'


@then('el refresh token se renueva')
def paso_refresh_rotado(context):
    cookie = context.response.cookies.get(COOKIE_REFRESH)
    assert cookie is not None and cookie.value, 'No llegó un refresh token nuevo.'
    assert cookie.value != context.refresh_de_login, 'El refresh token debía cambiar al renovar.'


@then('la respuesta tiene el formato de error de la API')
def paso_formato_error(context):
    datos = cuerpo(context)
    assert set(datos) == {'mensaje', 'errores'}, f'Formato inesperado: {datos}'
    assert isinstance(datos['mensaje'], str) and isinstance(datos['errores'], dict)

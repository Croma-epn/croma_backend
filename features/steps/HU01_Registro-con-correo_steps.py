from behave import given, then, when
from rest_framework.test import APIClient

from usuarios.models import Usuario

URL_REGISTRO = '/usuarios/registro/'

# Datos válidos por defecto: cada paso cambia solo lo que el escenario necesita probar.
DATOS_VALIDOS = {
    'nombre': 'Fernando',
    'correo': 'fernando.huilca@epn.edu.ec',
    'contrasena': 'Password123',
}


# ---------------------------------------------------------------------------
# Apoyo
# ---------------------------------------------------------------------------

def enviar_registro(context, payload):
    """
    Envía el registro a la API y deja en el contexto lo que necesitan los pasos
    "Entonces": el payload, la respuesta y cuántas cuentas había antes de enviarlo.
    """
    context.payload = payload
    context.cuentas_antes = Usuario.objects.count()
    context.response = APIClient().post(URL_REGISTRO, payload, format='json')


def texto_respuesta(context):
    return context.response.content.decode('utf-8')


def usuario_enviado(context):
    """Usuario creado con el correo del último payload (sin distinguir mayúsculas)."""
    return Usuario.objects.get(correo__iexact=context.payload['correo'].strip())


# ---------------------------------------------------------------------------
# Dado
# ---------------------------------------------------------------------------

@given('que el estudiante no tiene una cuenta registrada en el sistema')
def paso_sin_cuentas(context):
    # behave-django entrega una BD de pruebas limpia en cada escenario.
    assert Usuario.objects.count() == 0, 'Se esperaba una base de datos sin usuarios.'


@given('que ya existe una cuenta registrada con el correo "{correo}"')
def paso_cuenta_existente(context, correo):
    Usuario.objects.create_user(
        correo=correo,
        password='ClaveExistente1',
        nombre='Usuario Existente',
    )


# ---------------------------------------------------------------------------
# Cuando
# ---------------------------------------------------------------------------

@when('envía una petición de registro con el nombre "{nombre}", el correo "{correo}" y la contraseña "{contrasena}"')
def paso_registro_con_datos(context, nombre, correo, contrasena):
    enviar_registro(context, {'nombre': nombre, 'correo': correo, 'contrasena': contrasena})


@when('envía una petición de registro con los siguientes datos:')
def paso_registro_con_tabla(context):
    # Cada columna de la tabla es un campo del JSON. Si una columna no está en la
    # tabla, el campo no se envía (sirve para probar campos ausentes).
    fila = context.table[0]
    enviar_registro(context, dict(zip(context.table.headings, fila.cells)))


@when('envía una petición de registro con el correo "{correo}"')
def paso_registro_solo_correo(context, correo):
    enviar_registro(context, {**DATOS_VALIDOS, 'nombre': 'Nuevo Intento', 'correo': correo})


@when('envía una petición de registro con un nombre de {cantidad:d} caracteres')
def paso_registro_nombre_largo(context, cantidad):
    enviar_registro(context, {**DATOS_VALIDOS, 'nombre': 'a' * cantidad})


# ---------------------------------------------------------------------------
# Entonces
# ---------------------------------------------------------------------------

@then('la API debe responder con el código de estado HTTP {codigo:d}')
def paso_codigo_http(context, codigo):
    recibido = context.response.status_code
    assert recibido == codigo, (
        f'Se esperaba {codigo} pero se recibió {recibido}. Respuesta: {texto_respuesta(context)}'
    )


@then('la respuesta contiene el mensaje "{mensaje}"')
def paso_mensaje_respuesta(context, mensaje):
    recibido = context.response.json().get('mensaje')
    assert recibido == mensaje, f'Se esperaba el mensaje "{mensaje}" pero se recibió "{recibido}".'


@then('la API debe reportar en el campo "{campo}" el mensaje "{mensaje}"')
def paso_error_en_campo(context, campo, mensaje):
    errores = context.response.json().get('errores', {})
    assert campo in errores, (
        f'No hay error en el campo "{campo}". Errores recibidos: {errores}'
    )
    assert mensaje in errores[campo], (
        f'En "{campo}" se esperaba "{mensaje}" pero se recibió {errores[campo]}'
    )


@then('la cuenta se crea exitosamente')
def paso_cuenta_creada(context):
    assert Usuario.objects.count() == context.cuentas_antes + 1, (
        f'Se esperaba una cuenta nueva. Respuesta: {texto_respuesta(context)}'
    )
    assert usuario_enviado(context) is not None


@then('la cuenta queda registrada con el correo "{correo}"')
def paso_cuenta_con_correo_exacto(context, correo):
    # Búsqueda exacta (sin iexact): comprueba que el correo se guardó tal cual, en minúsculas.
    assert Usuario.objects.filter(correo=correo).exists(), (
        f'No existe una cuenta con el correo exacto "{correo}".'
    )


@then('la contraseña no se guarda en texto plano')
def paso_contrasena_con_hash(context):
    usuario = usuario_enviado(context)
    contrasena = context.payload['contrasena']
    assert usuario.password != contrasena, 'La contraseña se guardó en texto plano.'
    assert usuario.check_password(contrasena), 'El hash guardado no corresponde a la contraseña.'


@then('la cuenta no se registra en el sistema')
def paso_cuenta_no_creada(context):
    assert Usuario.objects.count() == context.cuentas_antes, (
        'Se creó una cuenta cuando no debía crearse.'
    )
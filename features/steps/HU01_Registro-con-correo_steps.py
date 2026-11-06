from behave import given, when, then
from rest_framework.test import APIClient
# Importaremos el modelo más adelante cuando lo creemos
from usuarios.models import Usuario

@given('que el estudiante no tiene una cuenta registrada en el sistema')
def step_impl(context):
    context.client = APIClient()
    # Limpiamos la base de datos de pruebas para asegurar un estado inicial limpio
    Usuario.objects.all().delete()

@when('envía una petición de registro con el nombre "{nombre}", el correo "{correo}" y la contraseña "{contrasena}"')
def step_impl(context, nombre, correo, contrasena):
    payload = {
        "nombre": nombre,
        "correo": correo,
        "contrasena": contrasena # Respetando el esquema OpenAPI de Mateo
    }
    # Simulamos el POST al endpoint que crearemos
    context.response = context.client.post('/api/v1/usuarios/registro/', payload, format='json')

@then('la cuenta se crea exitosamente')
def step_impl(context):
    pass
    # Verificaremos en la base de datos real
    assert Usuario.objects.filter(correo="fernando.huilca@epn.edu.ec").exists()

@then('la API debe responder con el código de estado HTTP {status_code:d}')
def step_impl(context, status_code):
    assert context.response.status_code == status_code, \
        f"Se esperaba {status_code} pero se recibió {context.response.status_code}. Respuesta: {context.response.data}"

@given('que ya existe una cuenta registrada con el correo "{correo}"')
def step_impl(context, correo):
    context.client = APIClient()
    # Inyectamos un usuario directamente en la base de datos de prueba
    Usuario.objects.create(nombre="Usuario Existente", correo=correo, contrasena="hashed_password")

@when('se envía una petición de registro con el correo "{correo}"')
def step_impl(context, correo):
    payload = {
        "nombre": "Nuevo Intento",
        "correo": correo,
        "contrasena": "OtraClave123"
    }
    context.response = context.client.post('/api/v1/usuarios/registro/', payload, format='json')

@then('la API debe rechazar la creación')
def step_impl(context):
    pass
    # Verificaremos que no se haya duplicado en la base de datos
    assert Usuario.objects.count() == 1
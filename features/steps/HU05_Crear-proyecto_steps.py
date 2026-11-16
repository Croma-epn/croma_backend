from io import BytesIO

import parse
from behave import given, register_type, then, when
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from rest_framework.test import APIClient
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken

from config.almacenamiento.falso import AlmacenFalso
from proyectos.models import Proyecto
from usuarios.models import Usuario

# El contrato de la API (la ruta) queda fijado aquí, en las pruebas.
URL_PROYECTOS = '/proyectos/'


# ---------------------------------------------------------------------------
# Un tipo de texto propio para los pasos
# ---------------------------------------------------------------------------

# "{nombre}" a secas acepta cualquier cosa, incluidas comillas, y eso hace que un paso
# corto como  crea un proyecto con el nombre "{nombre}"  también coincida con uno largo
# como  ... con el nombre "{nombre}" y una portada en formato "{formato}"  (behave
# lo rechaza por ambiguo). Con {nombre:Texto} el texto no puede contener comillas, así
# que cada frase coincide con un solo paso. También permite textos vacíos o de solo espacios.
@parse.with_pattern(r'[^"]*')
def _texto(valor):
    return valor


register_type(Texto=_texto)


# ---------------------------------------------------------------------------
# Apoyo
# ---------------------------------------------------------------------------

def cliente(context):
    """El mismo cliente que dejó el paso de iniciar sesión (o uno nuevo si no hubo sesión)."""
    if 'navegador' not in context:
        context.navegador = APIClient()
    return context.navegador


def cuerpo(context):
    return context.response.json()


def usuario_con_sesion(context):
    """El usuario dueño del access token con el que se está trabajando."""
    return Usuario.objects.get(pk=AccessToken(context.access)[api_settings.USER_ID_CLAIM])


def crear_proyecto(context, datos, portada=None, con_token=True):
    """
    Envía la petición de crear un proyecto igual que lo hace el front: un solo
    envío multipart/form-data con los textos y, si hay, el archivo de la portada.
    """
    if portada is not None:
        datos = {**datos, 'portada': portada}
    extra = {'HTTP_AUTHORIZATION': f'Bearer {context.access}'} if con_token else {}
    context.response = cliente(context).post(URL_PROYECTOS, datos, format='multipart', **extra)


def imagen_en_formato(formato):
    """Una imagen pequeña y válida. Devuelve (archivo, contenido en bytes)."""
    pillow, nombre, tipo = {
        'JPG': ('JPEG', 'portada.jpg', 'image/jpeg'),
        'PNG': ('PNG', 'portada.png', 'image/png'),
        'WebP': ('WEBP', 'portada.webp', 'image/webp'),
    }[formato]
    memoria = BytesIO()
    Image.new('RGB', (40, 40), (109, 79, 194)).save(memoria, pillow)
    contenido = memoria.getvalue()
    return SimpleUploadedFile(nombre, contenido, content_type=tipo), contenido


def png_con_tamano(total_bytes):
    """
    Una imagen PNG válida que pesa EXACTAMENTE `total_bytes`. Así la prueba de los 4 MB
    comprueba el límite y no otra cosa (la imagen sigue siendo una imagen correcta).
    El peso se completa con un bloque de texto, que los PNG permiten.
    """
    base = BytesIO()
    Image.new('RGB', (40, 40), (109, 79, 194)).save(base, 'PNG')
    # Un bloque de texto añade 12 bytes de estructura + el nombre del bloque + 1 + el texto.
    relleno = total_bytes - len(base.getvalue()) - 12 - len('relleno') - 1

    memoria = BytesIO()
    info = PngInfo()
    info.add_text('relleno', 'a' * relleno)
    Image.new('RGB', (40, 40), (109, 79, 194)).save(memoria, 'PNG', pnginfo=info)
    contenido = memoria.getvalue()
    assert len(contenido) == total_bytes, f'La imagen de prueba pesa {len(contenido)}, no {total_bytes}'
    return SimpleUploadedFile('portada.png', contenido, content_type='image/png'), contenido


def archivo_que_no_es_imagen_valida(tipo):
    """Archivos que NO se deben aceptar como portada. Devuelve (archivo, contenido)."""
    if tipo == 'una imagen GIF':
        # Es una imagen de verdad, pero el formato no está entre los admitidos.
        memoria = BytesIO()
        Image.new('P', (10, 10)).save(memoria, 'GIF')
        contenido, nombre, tipo_mime = memoria.getvalue(), 'animacion.gif', 'image/gif'
    elif tipo == 'un documento PDF':
        contenido = b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n'
        nombre, tipo_mime = 'documento.pdf', 'application/pdf'
    elif tipo == 'un archivo de texto':
        contenido, nombre, tipo_mime = b'Esto no es una imagen.', 'notas.txt', 'text/plain'
    elif tipo == 'un archivo de texto llamado .png':
        # El nombre y el tipo declarado dicen "png", pero el contenido es solo texto.
        contenido, nombre, tipo_mime = b'Esto no es una imagen.', 'falsa-imagen.png', 'image/png'
    else:
        raise ValueError(f'Tipo de archivo desconocido en la prueba: {tipo}')
    return SimpleUploadedFile(nombre, contenido, content_type=tipo_mime), contenido


# ---------------------------------------------------------------------------
# Dado
# ---------------------------------------------------------------------------

@given('que el estudiante ya tiene un proyecto llamado "{nombre:Texto}"')
def paso_proyecto_existente(context, nombre):
    Proyecto.objects.create(propietario=usuario_con_sesion(context), nombre=nombre)


@given('que el almacén de imágenes no está disponible')
def paso_almacen_caido(context):
    AlmacenFalso.disponible = False


# ---------------------------------------------------------------------------
# Cuando
# ---------------------------------------------------------------------------

@when('crea un proyecto con el nombre "{nombre:Texto}"')
def paso_crear_con_nombre(context, nombre):
    crear_proyecto(context, {'nombre': nombre})


@when('crea un proyecto con los siguientes datos:')
def paso_crear_con_tabla(context):
    # Cada columna de la tabla es un campo del envío. Si una columna no está,
    # el campo no se envía (sirve para probar campos ausentes).
    fila = context.table[0]
    crear_proyecto(context, dict(zip(context.table.headings, fila.cells)))


@when('crea un proyecto con un nombre de {cantidad:d} caracteres')
def paso_crear_con_nombre_largo(context, cantidad):
    crear_proyecto(context, {'nombre': 'n' * cantidad})


@when('crea un proyecto con el nombre "{nombre:Texto}" y una descripción de {cantidad:d} caracteres')
def paso_crear_con_descripcion_larga(context, nombre, cantidad):
    crear_proyecto(context, {'nombre': nombre, 'descripcion': 'd' * cantidad})


@when('crea un proyecto con el nombre "{nombre:Texto}" intentando asignarlo a la cuenta "{correo:Texto}"')
def paso_crear_a_nombre_de_otro(context, nombre, correo):
    otro = Usuario.objects.get(correo=correo)
    # El front (o quien llame a la API) intenta decidir quién es el dueño: debe ignorarse.
    crear_proyecto(context, {'nombre': nombre, 'propietario': otro.pk, 'propietario_id': otro.pk})


@when('crea un proyecto con el nombre "{nombre:Texto}" y una portada en formato "{formato:Texto}"')
def paso_crear_con_portada(context, nombre, formato):
    archivo, context.contenido_portada = imagen_en_formato(formato)
    crear_proyecto(context, {'nombre': nombre}, portada=archivo)


@when('crea un proyecto con el nombre "{nombre:Texto}" y una portada de {peso:d} bytes')
def paso_crear_con_portada_de_peso(context, nombre, peso):
    archivo, context.contenido_portada = png_con_tamano(peso)
    crear_proyecto(context, {'nombre': nombre}, portada=archivo)


@when('crea un proyecto con el nombre "{nombre:Texto}" y como portada "{tipo:Texto}"')
def paso_crear_con_portada_invalida(context, nombre, tipo):
    archivo, context.contenido_portada = archivo_que_no_es_imagen_valida(tipo)
    crear_proyecto(context, {'nombre': nombre}, portada=archivo)


@when('crea un proyecto con el nombre "{nombre:Texto}" sin enviar un access token')
def paso_crear_sin_token(context, nombre):
    crear_proyecto(context, {'nombre': nombre}, con_token=False)


# ---------------------------------------------------------------------------
# Entonces
# ---------------------------------------------------------------------------
# Los pasos de HU01 y HU02 también se usan aquí:
#   la API debe responder con el código de estado HTTP {codigo}
#   la respuesta contiene el mensaje "{mensaje}"
#   la API debe reportar en el campo "{campo}" el mensaje "{mensaje}"
#   la respuesta tiene el formato de error de la API

@then('la respuesta incluye el id, el nombre y la fecha de creación del proyecto')
def paso_respuesta_con_datos(context):
    proyecto = cuerpo(context)['proyecto']
    assert isinstance(proyecto.get('id'), int), f'Falta el id: {proyecto}'
    assert proyecto.get('nombre'), f'Falta el nombre: {proyecto}'
    assert proyecto.get('creado_en'), f'Falta la fecha de creación: {proyecto}'


@then('la respuesta indica que el proyecto no tiene portada')
def paso_respuesta_sin_portada(context):
    proyecto = cuerpo(context)['proyecto']
    assert 'portada' in proyecto and proyecto['portada'] is None, f'Se esperaba portada null: {proyecto}'


@then('la respuesta incluye la descripción "{descripcion:Texto}"')
def paso_respuesta_con_descripcion(context, descripcion):
    proyecto = cuerpo(context)['proyecto']
    assert proyecto.get('descripcion') == descripcion, f'Descripción recibida: {proyecto.get("descripcion")!r}'


@then('la respuesta incluye la dirección (URL) de la portada')
def paso_respuesta_con_portada(context):
    proyecto = cuerpo(context)['proyecto']
    portada = proyecto.get('portada')
    assert isinstance(portada, str) and portada.startswith('https://'), f'Portada recibida: {portada!r}'
    guardado = Proyecto.objects.get(pk=proyecto['id'])
    assert guardado.portada_url == portada, 'La dirección de la respuesta no coincide con la guardada'


@then('el proyecto "{nombre:Texto}" queda guardado a nombre de "{correo:Texto}"')
def paso_proyecto_de_usuario(context, nombre, correo):
    proyectos = Proyecto.objects.filter(nombre=nombre, propietario__correo=correo)
    assert proyectos.count() == 1, (
        f'Se esperaba 1 proyecto "{nombre}" de {correo} y hay {proyectos.count()}. '
        f'Proyectos existentes: {list(Proyecto.objects.values_list("nombre", "propietario__correo"))}'
    )
    assert cuerpo(context)['proyecto']['id'] == proyectos[0].pk, 'El id de la respuesta no es el del proyecto guardado'


@then('el estudiante "{correo:Texto}" tiene {cantidad:d} proyectos llamados "{nombre:Texto}"')
def paso_cantidad_de_proyectos(context, correo, cantidad, nombre):
    total = Proyecto.objects.filter(nombre=nombre, propietario__correo=correo).count()
    assert total == cantidad, f'Se esperaban {cantidad} proyectos "{nombre}" y hay {total}'


@then('la cuenta "{correo:Texto}" no tiene ningún proyecto')
def paso_cuenta_sin_proyectos(context, correo):
    total = Proyecto.objects.filter(propietario__correo=correo).count()
    assert total == 0, f'La cuenta {correo} tiene {total} proyecto(s) y no debería tener ninguno'


@then('no se crea ningún proyecto')
def paso_ningun_proyecto(context):
    total = Proyecto.objects.count()
    assert total == 0, f'Se esperaban 0 proyectos y hay {total}'


@then('la portada del proyecto "{nombre:Texto}" queda guardada en el almacén de imágenes')
def paso_portada_guardada(context, nombre):
    proyecto = Proyecto.objects.get(nombre=nombre)
    assert proyecto.portada_id, 'El proyecto no guardó el identificador de su portada'
    assert proyecto.portada_id in AlmacenFalso.guardadas, 'La imagen no llegó al almacén de imágenes'
    # La imagen guardada es, byte por byte, la que se envió.
    assert AlmacenFalso.guardadas[proyecto.portada_id] == context.contenido_portada, (
        'La imagen guardada no es igual a la enviada'
    )


@then('no se guarda ninguna imagen en el almacén de imágenes')
def paso_almacen_vacio(context):
    assert AlmacenFalso.guardadas == {}, f'El almacén no debería tener imágenes: {list(AlmacenFalso.guardadas)}'
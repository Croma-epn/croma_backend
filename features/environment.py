from django.test.utils import override_settings

from config.almacenamiento.falso import AlmacenFalso

# Las pruebas nunca hablan con el servicio real de imágenes (Cloudinary): usan el almacén
# falso, que guarda en memoria. Así corren sin internet, sin cuenta y sin gastar cuota.
ALMACEN_DE_PRUEBAS = 'config.almacenamiento.falso.AlmacenFalso'


def before_all(context):
    context.cambio_almacen = override_settings(ALMACEN_IMAGENES=ALMACEN_DE_PRUEBAS)
    context.cambio_almacen.enable()


def before_scenario(context, scenario):
    # Cada escenario empieza con el almacén vacío y disponible.
    AlmacenFalso.reiniciar()


def after_all(context):
    context.cambio_almacen.disable()
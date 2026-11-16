from config.almacenamiento import AlmacenNoDisponible, obtener_almacen
from proyectos.exceptions import ImagenNoGuardada
from proyectos.models import Proyecto

CARPETA_PORTADAS = 'proyectos/portadas'  # Dónde se agrupan las portadas dentro del almacén


def crear_proyecto(*, propietario, nombre, descripcion='', portada=None):
    """
    Crea un proyecto (CC2), con su portada si se envió (CC6).

    No valida formato (eso es del serializer) ni sabe nada de HTTP. Si el almacén de imágenes
    falla lanza ImagenNoGuardada y no queda ningún proyecto creado.
    Devuelve el Proyecto creado.
    """
    # 1) La imagen va primero: si el almacén falla, todavía no se ha guardado nada.
    #    El almacén solo se pide cuando hay portada: un proyecto sin imagen no lo necesita.
    almacen = None
    imagen = None
    if portada is not None:
        almacen = obtener_almacen()
        try:
            imagen = almacen.subir(portada, CARPETA_PORTADAS)
        except AlmacenNoDisponible:
            raise ImagenNoGuardada()

    # 2) El proyecto. Si esto falla, la imagen ya subida quedaría huérfana: se borra.
    try:
        return Proyecto.objects.create(
            propietario=propietario,
            nombre=nombre,
            descripcion=descripcion,
            portada_url=imagen.url if imagen else '',
            portada_id=imagen.identificador if imagen else '',
        )
    except Exception:
        if imagen:
            try:
                almacen.eliminar(imagen.identificador)
            except AlmacenNoDisponible:
                pass  # No se pudo limpiar; se prioriza informar el error original
        raise
from uuid import uuid4

from config.almacenamiento import AlmacenImagenes, AlmacenNoDisponible, ImagenGuardada


class AlmacenFalso(AlmacenImagenes):
    """
    Almacén de mentira para pruebas: guarda las imágenes en memoria, sin internet ni cuenta.

    El estado es de la clase (no de cada instancia) porque obtener_almacen() crea una
    instancia nueva en cada llamada y las pruebas necesitan ver lo mismo que vio el servicio.
    """

    guardadas: dict[str, bytes] = {}  # identificador -> contenido de la imagen
    disponible = True                 # Con False, simula que el servicio está caído

    @classmethod
    def reiniciar(cls):
        """Lo deja como nuevo: sin imágenes y disponible. Se llama antes de cada escenario."""
        cls.guardadas = {}
        cls.disponible = True

    def subir(self, archivo, carpeta):
        if not type(self).disponible:
            raise AlmacenNoDisponible('El almacén falso está configurado como no disponible.')
        identificador = f'{carpeta}/{uuid4().hex}'
        type(self).guardadas[identificador] = archivo.read()
        return ImagenGuardada(identificador, f'https://almacen-falso.test/{identificador}')

    def eliminar(self, identificador):
        if not type(self).disponible:
            raise AlmacenNoDisponible('El almacén falso está configurado como no disponible.')
        type(self).guardadas.pop(identificador, None)
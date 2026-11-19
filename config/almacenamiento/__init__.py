"""
Almacén de imágenes: el contrato que cumple cualquier servicio donde se guarden las imágenes.

El resto del código (servicios, vistas) pide el almacén con obtener_almacen() y solo conoce
este contrato: nunca importa Cloudinary directamente. Qué servicio se usa lo decide una línea
de settings.py:

    ALMACEN_IMAGENES = 'config.almacenamiento.cloudinary.AlmacenCloudinary'

Para cambiar de proveedor basta escribir otra clase que cumpla AlmacenImagenes y apuntar ahí.
Las pruebas usan config.almacenamiento.falso.AlmacenFalso, que no necesita internet.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from django.conf import settings
from django.utils.module_loading import import_string


class AlmacenNoDisponible(Exception):
    """El servicio de imágenes no respondió o rechazó la operación."""


@dataclass(frozen=True)
class ImagenGuardada:
    """Lo que devuelve el almacén al guardar una imagen."""

    identificador: str  # Sirve para eliminarla después
    url: str            # Dirección pública con la que el front la muestra


class AlmacenImagenes(ABC):
    @abstractmethod
    def subir(self, archivo, carpeta: str) -> ImagenGuardada:
        """
        Guarda la imagen y devuelve su identificador y su dirección.

        `archivo` es el archivo recibido (se lee con archivo.read()); `carpeta` agrupa las
        imágenes dentro del almacén, por ejemplo 'proyectos/portadas'.
        Lanza AlmacenNoDisponible si el servicio falla.
        """

    @abstractmethod
    def eliminar(self, identificador: str) -> None:
        """Borra la imagen. Si ya no existe, no hace nada. Lanza AlmacenNoDisponible si el servicio falla."""


def obtener_almacen() -> AlmacenImagenes:
    """Crea el almacén que indica la configuración ALMACEN_IMAGENES."""
    return import_string(settings.ALMACEN_IMAGENES)()
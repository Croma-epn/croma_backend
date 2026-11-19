import logging

import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error as ErrorDeCloudinary
from django.core.exceptions import ImproperlyConfigured

from config.almacenamiento import AlmacenImagenes, AlmacenNoDisponible, ImagenGuardada

registro = logging.getLogger(__name__)

# Segundos que se espera a Cloudinary antes de darlo por caído. Debe ser menor que los
# 30 segundos que Heroku le da a cada petición.
TIEMPO_MAXIMO = 20


class AlmacenCloudinary(AlmacenImagenes):
    """
    Guarda las imágenes en Cloudinary.

    La cuenta se toma de la variable de entorno CLOUDINARY_URL
    (cloudinary://API_KEY:API_SECRET@CLOUD_NAME). El paquete `cloudinary` la lee solo.
    """

    def __init__(self):
        if not cloudinary.config().cloud_name:
            # Error de configuración, no del servicio: debe verse claro en los registros.
            raise ImproperlyConfigured(
                'Falta la variable de entorno CLOUDINARY_URL. Para trabajar sin Cloudinary '
                'usa ALMACEN_IMAGENES=config.almacenamiento.falso.AlmacenFalso'
            )

    def subir(self, archivo, carpeta):
        try:
            resultado = cloudinary.uploader.upload(
                archivo,
                folder=carpeta,
                resource_type='image',  # Cloudinary también rechaza lo que no sea una imagen
                timeout=TIEMPO_MAXIMO,
            )
        except ErrorDeCloudinary as error:
            # El detalle queda en los registros del servidor; quien usa la API solo ve el mensaje general.
            registro.exception('Cloudinary no pudo guardar la imagen')
            raise AlmacenNoDisponible(str(error)) from error
        # public_id es el identificador de Cloudinary; secure_url, la dirección con https.
        return ImagenGuardada(identificador=resultado['public_id'], url=resultado['secure_url'])

    def eliminar(self, identificador):
        try:
            # Si la imagen ya no existe, Cloudinary responde "not found" sin dar error.
            cloudinary.uploader.destroy(
                identificador,
                resource_type='image',
                invalidate=True,  # Borra también las copias de la red de distribución
                timeout=TIEMPO_MAXIMO,
            )
        except ErrorDeCloudinary as error:
            registro.exception('Cloudinary no pudo eliminar la imagen')
            raise AlmacenNoDisponible(str(error)) from error
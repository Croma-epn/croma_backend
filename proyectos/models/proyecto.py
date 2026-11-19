from django.conf import settings
from django.db import models

from proyectos.limites import DESCRIPCION_MAX_CARACTERES, NOMBRE_MAX_CARACTERES


class Proyecto(models.Model):
    """
    Proyecto de modelado de un estudiante: agrupa el diseño de una aplicación.

    La portada no se guarda en la base de datos sino en el almacén de imágenes
    (hoy Cloudinary). Aquí quedan solo dos textos que la identifican.
    """

    # Quien creó el proyecto. Siempre sale de la sesión iniciada, nunca de lo que envíe el front.
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='proyectos',
    )
    nombre = models.CharField(max_length=NOMBRE_MAX_CARACTERES)
    descripcion = models.CharField(max_length=DESCRIPCION_MAX_CARACTERES, blank=True)

    # Vacíos cuando el proyecto no tiene portada.
    portada_url = models.URLField('dirección de la portada', max_length=500, blank=True)
    # Identificador de la imagen en el almacén: sin él no se puede borrar de allí.
    portada_id = models.CharField('identificador de la portada', max_length=255, blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado_en']  # Los más recientes primero, como en "Mis proyectos"

    def __str__(self):
        return self.nombre
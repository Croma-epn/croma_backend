from PIL import Image
from rest_framework import serializers

from proyectos import mensajes
from proyectos.limites import (
    DESCRIPCION_MAX_CARACTERES,
    FORMATOS_PORTADA,
    NOMBRE_MAX_CARACTERES,
    PORTADA_MAX_BYTES,
    PORTADA_MAX_MB,
)
from usuarios.serializers.comunes import mensajes_campo_vacio

from .comunes import ProyectoSerializer


def formato_de_imagen(archivo):
    """
    Devuelve el formato real de la imagen ('JPEG', 'PNG', 'WEBP', 'GIF'...) o None si el
    archivo no es una imagen. Mira el CONTENIDO del archivo: el nombre, la extensión y el
    tipo que declara quien lo envía se pueden falsear con facilidad.
    """
    try:
        archivo.seek(0)
        with Image.open(archivo) as imagen:
            imagen.verify()  # Comprueba la estructura sin cargar toda la imagen en memoria
            return imagen.format
    except Exception:  # noqa: BLE001
        # Pillow lanza distintos errores según cómo esté dañado el archivo
        # (no reconocido, truncado, demasiado grande...). Para la API es lo mismo: no es una imagen válida.
        return None
    finally:
        archivo.seek(0)  # Se deja listo para que el almacén lo lea desde el principio


class CrearProyectoSerializer(serializers.Serializer):
    """Datos para crear un proyecto. Se envían como multipart/form-data."""

    # Solo valida el FORMATO (CC3, CC5, CC8, CC9). Guardar el proyecto y la imagen
    # lo hace el servicio. El propietario no se pide: sale siempre de la sesión.

    nombre = serializers.CharField(
        max_length=NOMBRE_MAX_CARACTERES,
        help_text=f'Nombre del proyecto. Obligatorio, máximo {NOMBRE_MAX_CARACTERES} caracteres.',
        error_messages={
            **mensajes_campo_vacio(mensajes.NOMBRE_OBLIGATORIO),
            'max_length': mensajes.NOMBRE_MUY_LARGO,
        },
    )

    descripcion = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=DESCRIPCION_MAX_CARACTERES,
        help_text=f'Descripción del proyecto. Opcional, máximo {DESCRIPCION_MAX_CARACTERES} caracteres.',
        error_messages={'max_length': mensajes.DESCRIPCION_MUY_LARGA},
    )

    portada = serializers.FileField(
        required=False,
        write_only=True,
        help_text=f'Imagen de portada. Opcional. JPG, PNG o WebP, de hasta {PORTADA_MAX_MB} MB.',
        error_messages={
            'invalid': mensajes.PORTADA_NO_ES_IMAGEN,   # Llegó un texto en lugar de un archivo
            'empty': mensajes.PORTADA_NO_ES_IMAGEN,     # Archivo vacío
            'no_name': mensajes.PORTADA_NO_ES_IMAGEN,
        },
    )

    def validate_portada(self, archivo):
        # Primero el peso (es lo más barato de comprobar) y después el contenido.
        if archivo.size > PORTADA_MAX_BYTES:
            raise serializers.ValidationError(mensajes.PORTADA_MUY_PESADA)
        if formato_de_imagen(archivo) not in FORMATOS_PORTADA:
            raise serializers.ValidationError(mensajes.PORTADA_NO_ES_IMAGEN)
        return archivo


class CreacionExitosaSerializer(serializers.Serializer):
    """Respuesta al crear el proyecto."""

    # Solo documenta la forma del JSON en Swagger: la view arma la respuesta a mano.

    mensaje = serializers.CharField(help_text='Mensaje de confirmación.')
    proyecto = ProyectoSerializer(help_text='Datos del proyecto creado.')
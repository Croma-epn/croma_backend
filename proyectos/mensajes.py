"""
Mensajes de la API de proyectos, tal como están escritos en los criterios de aceptación (CC) de la HU05.

Centralizados aquí para que el serializer, el servicio y la documentación usen
exactamente el mismo texto. Si un CC cambia, se modifica en un solo lugar.
"""

from proyectos.limites import DESCRIPCION_MAX_CARACTERES, NOMBRE_MAX_CARACTERES, PORTADA_MAX_MB

# Validación de formato (HTTP 400)
NOMBRE_OBLIGATORIO = 'El nombre del proyecto es obligatorio.'                              # HU05 CC3
NOMBRE_MUY_LARGO = f'Alcanzaste el máximo de {NOMBRE_MAX_CARACTERES} caracteres.'           # HU05 CC5
DESCRIPCION_MUY_LARGA = f'Alcanzaste el máximo de {DESCRIPCION_MAX_CARACTERES} caracteres.'  # HU05 CC5

# Los CC 8 y 9 terminan con "El proyecto se creará sin portada." porque lo dice el front,
# que descarta la imagen y crea el proyecto igual. La API, en cambio, no crea el proyecto,
# así que no repite esa frase.
PORTADA_MUY_PESADA = f'La imagen supera los {PORTADA_MAX_MB} MB. Usa una más ligera.'        # HU05 CC8 (adaptado)
PORTADA_NO_ES_IMAGEN = 'El archivo debe ser una imagen (JPG, PNG o WebP).'                  # HU05 CC9 (adaptado)

# Servicio externo (HTTP 503)
IMAGEN_NO_GUARDADA = 'No pudimos guardar la imagen. Inténtalo de nuevo.'                    # No viene de un CC

# Éxito (HTTP 201)
PROYECTO_CREADO = 'Proyecto creado. Agrega tu primera pantalla.'                            # HU05 CC2
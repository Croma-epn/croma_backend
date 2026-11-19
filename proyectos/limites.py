"""
Límites de un proyecto, tal como están escritos en los criterios de aceptación (CC) de la HU05.

Se definen una sola vez para que el modelo, el serializer, los mensajes y las pruebas usen
exactamente los mismos números. Si un CC cambia, se modifica solo aquí.
"""

NOMBRE_MAX_CARACTERES = 30        # HU05 CC5
DESCRIPCION_MAX_CARACTERES = 150  # HU05 CC5

PORTADA_MAX_MB = 4                                  # HU05 CC6 y CC8
PORTADA_MAX_BYTES = PORTADA_MAX_MB * 1024 * 1024    # 4 MB = 4 × 1024 × 1024 = 4194304 bytes

# Formatos de imagen admitidos como portada. La clave es el nombre que Pillow
# da al formato; el valor, el tipo de archivo (MIME) que se informa al guardarla.
FORMATOS_PORTADA = {
    'JPEG': 'image/jpeg',
    'PNG': 'image/png',
    'WEBP': 'image/webp',
}
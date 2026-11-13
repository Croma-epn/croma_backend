"""
Mensajes de la API, tal como están escritos en los criterios de aceptación (CC) de la HU01 y la HU02.

Centralizados aquí para que el serializer, el servicio y la documentación usen
exactamente el mismo texto. Si un CC cambia, se modifica en un solo lugar.
"""

# Validación de formato (HTTP 400)
NOMBRE_OBLIGATORIO = 'Escribe tu nombre completo.'              # HU01 CC3
CORREO_OBLIGATORIO = 'Ingresa tu correo.'                       # HU01 CC4 / HU02 CC2
CORREO_INVALIDO = 'Ingresa un correo válido.'                   # HU01 CC5 / HU02 CC3
CONTRASENA_CORTA = 'Usa al menos 6 caracteres.'                 # HU01 CC7
NOMBRE_MUY_LARGO = 'Alcanzaste el máximo de 100 caracteres.'    # HU01 CC9
CONTRASENA_OBLIGATORIA = 'Ingresa tu contraseña.'               # HU02 CC4

# Reglas de negocio (HTTP 409)
CORREO_YA_REGISTRADO = 'Este correo ya tiene una cuenta.'       # HU01 CC6

# Autenticación (HTTP 401)
# Un solo mensaje para correo inexistente, contraseña incorrecta o cuenta inactiva:
# así la API no revela qué correos tienen cuenta.
CREDENCIALES_INCORRECTAS = (
    'No encontramos una cuenta con esos datos. '
    'Revisa tus credenciales o crea una cuenta.'
)                                                               # HU02 CC5
SESION_EXPIRADA = 'Tu sesión expiró. Inicia sesión de nuevo.'   # No viene de un CC

# Éxito (HTTP 201 y 200)
CUENTA_CREADA = 'Cuenta creada correctamente.'                  # HU01 CC2 (201)
SESION_INICIADA = 'Sesión iniciada correctamente.'              # HU02 CC1 (200)
SESION_CERRADA = 'Sesión cerrada.'                              # HU02 CC8 (200)
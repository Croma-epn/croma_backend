"""
Mensajes de la API, tal como están escritos en los criterios de aceptación (CC) de la HU01.

Centralizados aquí para que el serializer, el servicio y la documentación usen
exactamente el mismo texto. Si un CC cambia, se modifica en un solo lugar.
"""

# Validación de formato (HTTP 400)
NOMBRE_OBLIGATORIO = 'Escribe tu nombre completo.'              # CC3
CORREO_OBLIGATORIO = 'Ingresa tu correo.'                       # CC4
CORREO_INVALIDO = 'Ingresa un correo válido.'                   # CC5
CONTRASENA_CORTA = 'Usa al menos 6 caracteres.'                 # CC7
NOMBRE_MUY_LARGO = 'Alcanzaste el máximo de 100 caracteres.'    # CC9

# Reglas de negocio (HTTP 409)
CORREO_YA_REGISTRADO = 'Este correo ya tiene una cuenta.'       # CC6

# Éxito (HTTP 201)
CUENTA_CREADA = 'Cuenta creada correctamente.'                  # CC2
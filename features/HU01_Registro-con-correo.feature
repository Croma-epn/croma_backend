# language: es
@HU01
Característica: Registro de estudiante con correo institucional
  Como estudiante
  Quiero registrarme con mi correo institucional
  Para guardar mis modelos en una cuenta propia


  # Criterio de aceptación 2 - Registro exitoso
  # Dado que un usuario se encuentra en la página “Crea tu cuenta”
  # Cuando escribe su nombre completo
  # Y escribe un correo electrónico válido de cualquier dominio
  # Y escribe una contraseña de al menos 6 caracteres
  # Y repite la contraseña en “Confirmar contraseña”
  # Y pulsa el botón “Crear cuenta”
  # Entonces el sistema muestra la página “Iniciar sesión” con su correo ya escrito
  # Y muestra el mensaje “Cuenta creada correctamente.”
  #
  # Equivalente backend: la API responde 201, la cuenta queda registrada con la
  # contraseña protegida (hash) y el correo se guarda en minúsculas.
  @HU01 @CC2 @api @registro_exitoso
  Escenario: Registro exitoso de un nuevo estudiante
    Dado que el estudiante no tiene una cuenta registrada en el sistema
    Cuando envía una petición de registro con el nombre "Fernando", el correo "fernando.huilca@epn.edu.ec" y la contraseña "Password123"
    Entonces la cuenta se crea exitosamente
    Y la API debe responder con el código de estado HTTP 201
    Y la respuesta contiene el mensaje "Cuenta creada correctamente."
    Y la contraseña no se guarda en texto plano

  @HU01 @CC2 @api @correo_minusculas
  Escenario: El correo se guarda en minúsculas
    Dado que el estudiante no tiene una cuenta registrada en el sistema
    Cuando envía una petición de registro con el nombre "Fernando", el correo "Fernando.Huilca@EPN.edu.ec" y la contraseña "Password123"
    Entonces la API debe responder con el código de estado HTTP 201
    Y la cuenta queda registrada con el correo "fernando.huilca@epn.edu.ec"

  @HU01 @CC2 @api @dominios
  Esquema del escenario: Registro exitoso con correos de cualquier dominio
    Dado que el estudiante no tiene una cuenta registrada en el sistema
    Cuando envía una petición de registro con el nombre "Fernando", el correo "<correo>" y la contraseña "Password123"
    Entonces la cuenta se crea exitosamente
    Y la API debe responder con el código de estado HTTP 201

    Ejemplos:
      | correo                 |
      | usuario@gmail.com      |
      | usuario@empresa.com.ec |
      | usuario@dominio.io     |

  # Criterio de aceptación 3 - Error por nombre vacío
  # Dado que un usuario se encuentra en la página “Crea tu cuenta”
  # Cuando deja vacío el campo “Nombre completo”
  # Entonces el sistema muestra el mensaje “Escribe tu nombre completo.”
  # Y pulsar el botón "Crear cuenta" no envía el formulario.
  #
  # Equivalente backend: la API responde 400 y reporta el error en "nombre".
  @HU01 @CC3 @api @validacion @nombre_vacio
  Escenario: Error al registrar con el nombre vacío
    Dado que el estudiante no tiene una cuenta registrada en el sistema
    Cuando envía una petición de registro con los siguientes datos:
      | nombre | correo                     | contrasena  |
      |        | fernando.huilca@epn.edu.ec | Password123 |
    Entonces la API debe responder con el código de estado HTTP 400
    Y la API debe reportar en el campo "nombre" el mensaje "Escribe tu nombre completo."
    Y la cuenta no se registra en el sistema

  @HU01 @CC3 @api @validacion @nombre_ausente
  Escenario: Error al registrar sin enviar el campo nombre
    Dado que el estudiante no tiene una cuenta registrada en el sistema
    Cuando envía una petición de registro con los siguientes datos:
      | correo                     | contrasena  |
      | fernando.huilca@epn.edu.ec | Password123 |
    Entonces la API debe responder con el código de estado HTTP 400
    Y la API debe reportar en el campo "nombre" el mensaje "Escribe tu nombre completo."
    Y la cuenta no se registra en el sistema

  # Criterio de aceptación 4 - Error por Correo vacío
  # Dado que un usuario se encuentra en la página “Crea tu cuenta”
  # Cuando deja vacío el campo “Correo electrónico”
  # Entonces el sistema muestra el mensaje “Ingresa tu correo.”
  # Y pulsar el botón "Crear cuenta" no envía el formulario.
  #
  # Equivalente backend: la API responde 400 y reporta el error en "correo".
  @HU01 @CC4 @api @validacion @correo_vacio
  Escenario: Error al registrar con el correo vacío
    Dado que el estudiante no tiene una cuenta registrada en el sistema
    Cuando envía una petición de registro con los siguientes datos:
      | nombre   | correo | contrasena  |
      | Fernando |        | Password123 |
    Entonces la API debe responder con el código de estado HTTP 400
    Y la API debe reportar en el campo "correo" el mensaje "Ingresa tu correo."
    Y la cuenta no se registra en el sistema

  # Criterio de aceptación 5 - Error por correo con formato inválido
  # Dado que un usuario se encuentra en la página “Crea tu cuenta”
  # Cuando escribe un correo sin el formato nombre@dominio
  # Entonces el sistema muestra el mensaje “Ingresa un correo válido.”
  # Y pulsar el botón "Crear cuenta" no envía el formulario.
  #
  # Equivalente backend: la API responde 400 y reporta el error en "correo".
  @HU01 @CC5 @api @validacion @correo_invalido
  Esquema del escenario: Error al registrar con un correo con formato inválido
    Dado que el estudiante no tiene una cuenta registrada en el sistema
    Cuando envía una petición de registro con los siguientes datos:
      | nombre   | correo   | contrasena  |
      | Fernando | <correo> | Password123 |
    Entonces la API debe responder con el código de estado HTTP 400
    Y la API debe reportar en el campo "correo" el mensaje "Ingresa un correo válido."
    Y la cuenta no se registra en el sistema

    Ejemplos:
      | correo          |
      | correo-invalido |
      | ana@            |
      | @ejemplo.com    |
      | ana@ejemplo     |

  # Criterio de aceptación 6 - Error por correo ya registrado
  # Dado que un usuario se encuentra en la página “Crea tu cuenta”
  # Cuando escribe un correo que ya tiene una cuenta
  # Y pulsa el botón “Crear cuenta”
  # Entonces el sistema muestra el mensaje “Este correo ya tiene una cuenta.”
  #
  # Equivalente backend: la API responde 409, reporta el error en "correo"
  # y no duplica la cuenta.
  @HU01 @CC6 @api @validacion @correo_duplicado
  Escenario: Error al intentar registrar un correo ya existente
    Dado que ya existe una cuenta registrada con el correo "fernando.huilca@epn.edu.ec"
    Cuando envía una petición de registro con el correo "fernando.huilca@epn.edu.ec"
    Entonces la API debe responder con el código de estado HTTP 409
    Y la API debe reportar en el campo "correo" el mensaje "Este correo ya tiene una cuenta."
    Y la cuenta no se registra en el sistema

  @HU01 @CC6 @api @validacion @correo_duplicado_mayusculas
  Escenario: Error al registrar un correo ya existente escrito con otras mayúsculas
    Dado que ya existe una cuenta registrada con el correo "fernando.huilca@epn.edu.ec"
    Cuando envía una petición de registro con el correo "FERNANDO.HUILCA@EPN.EDU.EC"
    Entonces la API debe responder con el código de estado HTTP 409
    Y la API debe reportar en el campo "correo" el mensaje "Este correo ya tiene una cuenta."
    Y la cuenta no se registra en el sistema

  # Criterio de aceptación 7 - Error por contraseña corta
  # Dado que un usuario se encuentra en la página “Crea tu cuenta”
  # Cuando escribe una contraseña de menos de 6 caracteres
  # Entonces el sistema muestra el mensaje “Usa al menos 6 caracteres.”
  # Y pulsar el botón "Crear cuenta" no envía el formulario.
  #
  # Equivalente backend: la API también valida la longitud mínima (el front se
  # puede saltar); con menos de 6 caracteres responde 400 y reporta el error en
  # "contrasena". Una contraseña vacía o no enviada recibe el mismo mensaje.
  @HU01 @CC7 @api @validacion @contrasena_corta
  Esquema del escenario: Error al registrar con una contraseña de menos de 6 caracteres
    Dado que el estudiante no tiene una cuenta registrada en el sistema
    Cuando envía una petición de registro con los siguientes datos:
      | nombre   | correo                     | contrasena   |
      | Fernando | fernando.huilca@epn.edu.ec | <contrasena> |
    Entonces la API debe responder con el código de estado HTTP 400
    Y la API debe reportar en el campo "contrasena" el mensaje "Usa al menos 6 caracteres."
    Y la cuenta no se registra en el sistema

    Ejemplos:
      | contrasena |
      | abc12      |
      | a          |

  @HU01 @CC7 @api @validacion @contrasena_vacia
  Escenario: Error al registrar con la contraseña vacía
    Dado que el estudiante no tiene una cuenta registrada en el sistema
    Cuando envía una petición de registro con los siguientes datos:
      | nombre   | correo                     | contrasena |
      | Fernando | fernando.huilca@epn.edu.ec |            |
    Entonces la API debe responder con el código de estado HTTP 400
    Y la API debe reportar en el campo "contrasena" el mensaje "Usa al menos 6 caracteres."
    Y la cuenta no se registra en el sistema

  @HU01 @CC7 @api @limite @contrasena_limite
  Escenario: Una contraseña de exactamente 6 caracteres es aceptada
    Dado que el estudiante no tiene una cuenta registrada en el sistema
    Cuando envía una petición de registro con el nombre "Fernando", el correo "fernando.huilca@epn.edu.ec" y la contraseña "abc123"
    Entonces la cuenta se crea exitosamente
    Y la API debe responder con el código de estado HTTP 201

  # Criterio de aceptación 9 - Límite por nombre demasiado largo
  # Dado que un usuario se encuentra en la página “Crea tu cuenta”
  # Cuando escribe 100 caracteres en “Nombre completo”
  # Entonces el sistema no permite escribir más caracteres
  # Y muestra el mensaje “Alcanzaste el máximo de 100 caracteres.”
  #
  # Equivalente backend: el campo "nombre" admite máximo 100 caracteres;
  # una petición con 101 caracteres responde 400.
  @HU01 @CC9 @api @validacion @nombre_largo
  Escenario: Error al registrar un nombre de más de 100 caracteres
    Dado que el estudiante no tiene una cuenta registrada en el sistema
    Cuando envía una petición de registro con un nombre de 101 caracteres
    Entonces la API debe responder con el código de estado HTTP 400
    Y la API debe reportar en el campo "nombre" el mensaje "Alcanzaste el máximo de 100 caracteres."
    Y la cuenta no se registra en el sistema

  @HU01 @CC9 @api @limite @nombre_limite
  Escenario: Un nombre de exactamente 100 caracteres es aceptado
    Dado que el estudiante no tiene una cuenta registrada en el sistema
    Cuando envía una petición de registro con un nombre de 100 caracteres
    Entonces la cuenta se crea exitosamente
    Y la API debe responder con el código de estado HTTP 201




# COBERTURA FUNCIONAL: qué historias de usuario / criterios de aceptación tienen escenarios
#
# Criterios que NO pueden ser testeados desde el backend:
#
# Criterio de aceptación 1 - Acceso exitoso al formulario de registro
# Dado que un usuario se encuentra en la página “Iniciar sesión”
# Cuando pulsa el botón “Crear una cuenta”
# Entonces el sistema muestra el formulario “Crea tu cuenta”.
# Motivo: es un comportamiento de navegación del frontend.
#
# Criterio de aceptación 8 - Error por contraseñas distintas
# Dado que un usuario se encuentra en la página “Crea tu cuenta”
# Cuando escribe en “Confirmar contraseña” un valor distinto a la contraseña o deja el campo vacío
# Entonces el sistema muestra el mensaje “Las contraseñas deben coincidir.”
# Y pulsar el botón "Crear cuenta" no envía el formulario.
# Motivo: la API no recibe el campo “Confirmar contraseña”; la comparación
# se realiza únicamente en el frontend.
#
# Criterio de aceptación 10 - Mostrar u ocultar la contraseña
# Dado que un usuario se encuentra en la página “Crea tu cuenta”
# Cuando pulsa el ícono del ojo de un campo de contraseña
# Entonces el sistema muestra u oculta la contraseña escrita.
# Motivo: es un comportamiento visual del frontend.
#
# Criterio de aceptación 11 - Volver a iniciar sesión
# Dado que un usuario se encuentra en la página “Crea tu cuenta”
# Cuando pulsa el botón “Iniciar sesión”
# Entonces el sistema muestra la página “Iniciar sesión”.
# Motivo: es un comportamiento de navegación del frontend.

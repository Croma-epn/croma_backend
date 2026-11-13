# language: es
@HU02
Característica: Iniciar sesión
  Como usuario
  Quiero iniciar y cerrar sesión
  Para acceder de forma segura a mis proyectos


  # Criterio de aceptación 1 - Inicio de sesión exitoso
  # Dado que un usuario registrado se encuentra en la página “Iniciar sesión”
  # Cuando escribe su correo y su contraseña
  # Y pulsa el botón “Iniciar sesión”
  # Entonces el sistema muestra la página “Mis proyectos”
  # Y muestra el mensaje “Sesión iniciada correctamente.”
  #
  # Equivalente backend: la API responde 200 con el mensaje, los datos del usuario y un
  # access token en el cuerpo. El refresh token NO viaja en el cuerpo: se entrega en una
  # cookie HttpOnly. El correo no distingue mayúsculas. Con el access token se puede
  # consultar el perfil del usuario autenticado.
  @HU02 @CC1 @api @login_exitoso
  Escenario: Inicio de sesión exitoso
    Dado que existe una cuenta registrada con el correo "fernando.huilca@epn.edu.ec" y la contraseña "Password123"
    Cuando envía una petición de inicio de sesión con el correo "fernando.huilca@epn.edu.ec" y la contraseña "Password123"
    Entonces la API debe responder con el código de estado HTTP 200
    Y la respuesta contiene el mensaje "Sesión iniciada correctamente."
    Y la respuesta incluye el id, el nombre y el correo del usuario
    Y la respuesta no incluye la contraseña del usuario
    Y la respuesta incluye un access token
    Y el refresh token no viaja en el cuerpo de la respuesta
    Y el refresh token se entrega en una cookie HttpOnly

  @HU02 @CC1 @api @login_mayusculas
  Escenario: El inicio de sesión no distingue mayúsculas en el correo
    Dado que existe una cuenta registrada con el correo "fernando.huilca@epn.edu.ec" y la contraseña "Password123"
    Cuando envía una petición de inicio de sesión con el correo "FERNANDO.HUILCA@EPN.EDU.EC" y la contraseña "Password123"
    Entonces la API debe responder con el código de estado HTTP 200
    Y la respuesta contiene el mensaje "Sesión iniciada correctamente."

  @HU02 @CC1 @api @acceso_con_token
  Escenario: El access token permite consultar el perfil del usuario autenticado
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando consulta su perfil con el access token
    Entonces la API debe responder con el código de estado HTTP 200
    Y la respuesta identifica al usuario con el correo "fernando.huilca@epn.edu.ec"

  # Criterio de aceptación 2 - Error por correo vacío
  # Dado que un usuario se encuentra en la página “Iniciar sesión”
  # Cuando deja vacío el campo “Correo electrónico”
  # Entonces el sistema muestra el mensaje “Ingresa tu correo.”
  # Y pulsar el botón "Iniciar sesión" no envía el formulario.
  #
  # Equivalente backend: la API también valida (el front se puede saltar); responde 400,
  # reporta el error en "correo" y no entrega ningún token.
  @HU02 @CC2 @api @validacion @correo_vacio
  Escenario: Error al iniciar sesión con el correo vacío
    Dado que existe una cuenta registrada con el correo "fernando.huilca@epn.edu.ec" y la contraseña "Password123"
    Cuando envía una petición de inicio de sesión con los siguientes datos:
      | correo | contrasena  |
      |        | Password123 |
    Entonces la API debe responder con el código de estado HTTP 400
    Y la API debe reportar en el campo "correo" el mensaje "Ingresa tu correo."
    Y no se entrega ningún token ni cookie de sesión

  @HU02 @CC2 @api @validacion @correo_ausente
  Escenario: Error al iniciar sesión sin enviar el campo correo
    Dado que existe una cuenta registrada con el correo "fernando.huilca@epn.edu.ec" y la contraseña "Password123"
    Cuando envía una petición de inicio de sesión con los siguientes datos:
      | contrasena  |
      | Password123 |
    Entonces la API debe responder con el código de estado HTTP 400
    Y la API debe reportar en el campo "correo" el mensaje "Ingresa tu correo."
    Y no se entrega ningún token ni cookie de sesión

  # Criterio de aceptación 3 - Error por correo con formato inválido
  # Dado que un usuario se encuentra en la página “Iniciar sesión”
  # Cuando escribe un correo sin el formato nombre@dominio
  # Entonces el sistema muestra el mensaje “Ingresa un correo válido.”
  # Y pulsar el botón "Iniciar sesión" no envía el formulario.
  #
  # Equivalente backend: la API responde 400 y reporta el error en "correo".
  @HU02 @CC3 @api @validacion @correo_invalido
  Esquema del escenario: Error al iniciar sesión con un correo con formato inválido
    Dado que existe una cuenta registrada con el correo "fernando.huilca@epn.edu.ec" y la contraseña "Password123"
    Cuando envía una petición de inicio de sesión con el correo "<correo>" y la contraseña "Password123"
    Entonces la API debe responder con el código de estado HTTP 400
    Y la API debe reportar en el campo "correo" el mensaje "Ingresa un correo válido."
    Y no se entrega ningún token ni cookie de sesión

    Ejemplos:
      | correo          |
      | correo-invalido |
      | ana@            |
      | @ejemplo.com    |
      | ana@ejemplo     |

  # Criterio de aceptación 4 - Error por contraseña vacía
  # Dado que un usuario se encuentra en la página “Iniciar sesión”
  # Cuando deja el campo de contraseña vacío
  # Entonces el sistema muestra el mensaje “Ingresa tu contraseña.”
  # Y pulsar el botón "Iniciar sesión" no envía el formulario.
  #
  # Equivalente backend: la API responde 400 y reporta el error en "contrasena".
  @HU02 @CC4 @api @validacion @contrasena_vacia
  Escenario: Error al iniciar sesión con la contraseña vacía
    Dado que existe una cuenta registrada con el correo "fernando.huilca@epn.edu.ec" y la contraseña "Password123"
    Cuando envía una petición de inicio de sesión con los siguientes datos:
      | correo                     | contrasena |
      | fernando.huilca@epn.edu.ec |            |
    Entonces la API debe responder con el código de estado HTTP 400
    Y la API debe reportar en el campo "contrasena" el mensaje "Ingresa tu contraseña."
    Y no se entrega ningún token ni cookie de sesión

  @HU02 @CC4 @api @validacion @contrasena_ausente
  Escenario: Error al iniciar sesión sin enviar el campo contraseña
    Dado que existe una cuenta registrada con el correo "fernando.huilca@epn.edu.ec" y la contraseña "Password123"
    Cuando envía una petición de inicio de sesión con los siguientes datos:
      | correo                     |
      | fernando.huilca@epn.edu.ec |
    Entonces la API debe responder con el código de estado HTTP 400
    Y la API debe reportar en el campo "contrasena" el mensaje "Ingresa tu contraseña."
    Y no se entrega ningún token ni cookie de sesión

  # Criterio de aceptación 5 - Error por credenciales incorrectas
  # Dado que un usuario se encuentra en la página “Iniciar sesión”
  # Cuando escribe un correo que no está registrado o una contraseña incorrecta
  # Y pulsa el botón “Iniciar sesión”
  # Entonces el sistema muestra el mensaje “No encontramos una cuenta con esos datos. Revisa tus credenciales o crea una cuenta.”
  # Y pulsar el botón "Iniciar sesión" no envía el formulario.
  #
  # Equivalente backend: la API responde 401 con el mensaje y no entrega ningún token.
  # El mensaje es el MISMO para correo inexistente, contraseña incorrecta o cuenta
  # inactiva: así la API no revela qué correos tienen cuenta.
  @HU02 @CC5 @api @credenciales @correo_no_registrado
  Escenario: Error al iniciar sesión con un correo que no está registrado
    Dado que existe una cuenta registrada con el correo "fernando.huilca@epn.edu.ec" y la contraseña "Password123"
    Cuando envía una petición de inicio de sesión con el correo "otra.persona@epn.edu.ec" y la contraseña "Password123"
    Entonces la API debe responder con el código de estado HTTP 401
    Y la respuesta contiene el mensaje "No encontramos una cuenta con esos datos. Revisa tus credenciales o crea una cuenta."
    Y no se entrega ningún token ni cookie de sesión

  @HU02 @CC5 @api @credenciales @contrasena_incorrecta
  Escenario: Error al iniciar sesión con una contraseña incorrecta
    Dado que existe una cuenta registrada con el correo "fernando.huilca@epn.edu.ec" y la contraseña "Password123"
    Cuando envía una petición de inicio de sesión con el correo "fernando.huilca@epn.edu.ec" y la contraseña "OtraClave999"
    Entonces la API debe responder con el código de estado HTTP 401
    Y la respuesta contiene el mensaje "No encontramos una cuenta con esos datos. Revisa tus credenciales o crea una cuenta."
    Y no se entrega ningún token ni cookie de sesión

  @HU02 @CC5 @api @credenciales @cuenta_inactiva
  Escenario: Una cuenta inactiva no puede iniciar sesión
    Dado que existe una cuenta inactiva con el correo "fernando.huilca@epn.edu.ec" y la contraseña "Password123"
    Cuando envía una petición de inicio de sesión con el correo "fernando.huilca@epn.edu.ec" y la contraseña "Password123"
    Entonces la API debe responder con el código de estado HTTP 401
    Y la respuesta contiene el mensaje "No encontramos una cuenta con esos datos. Revisa tus credenciales o crea una cuenta."
    Y no se entrega ningún token ni cookie de sesión

  # Criterio de aceptación 8 - Cierre de sesión exitoso
  # Dado que un usuario ve el diálogo “¿Cerrar sesión?”
  # Cuando pulsa el botón “Cerrar sesión”
  # Entonces el sistema muestra la página “Iniciar sesión”
  # Y muestra el mensaje “Sesión cerrada.”
  #
  # Equivalente backend: la API responde 200 con el mensaje, borra la cookie del refresh
  # token y lo invalida (lista negra), de modo que ya no sirve para renovar la sesión.
  # Cerrar sesión es idempotente: sin sesión activa también responde 200.
  @HU02 @CC8 @api @logout_exitoso
  Escenario: Cierre de sesión exitoso
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando cierra sesión
    Entonces la API debe responder con el código de estado HTTP 200
    Y la respuesta contiene el mensaje "Sesión cerrada."
    Y la cookie del refresh token se elimina

  @HU02 @CC8 @api @logout_invalida_refresh
  Escenario: Después de cerrar sesión el refresh token ya no sirve
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando cierra sesión
    Y solicita renovar la sesión con el refresh token anterior
    Entonces la API debe responder con el código de estado HTTP 401
    Y la respuesta contiene el mensaje "Tu sesión expiró. Inicia sesión de nuevo."

  @HU02 @CC8 @api @logout_sin_sesion
  Escenario: Cerrar sesión sin tener una sesión iniciada también responde éxito
    Cuando cierra sesión sin tener una sesión iniciada
    Entonces la API debe responder con el código de estado HTTP 200
    Y la respuesta contiene el mensaje "Sesión cerrada."

  # Renovación de la sesión (no corresponde a un criterio de aceptación)
  # El access token dura poco; el front usa el refresh token (cookie) para pedir uno nuevo
  # sin que el usuario vuelva a escribir su contraseña. Cada renovación entrega un refresh
  # token nuevo y el anterior queda inválido.
  @HU02 @api @sesion @renovar_sesion
  Escenario: Renovar la sesión entrega un access token nuevo y rota el refresh token
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando solicita renovar la sesión
    Entonces la API debe responder con el código de estado HTTP 200
    Y la respuesta incluye un access token nuevo
    Y el refresh token se renueva

  @HU02 @api @sesion @renovar_sin_cookie
  Escenario: No se puede renovar la sesión sin refresh token
    Cuando solicita renovar la sesión sin tener una sesión iniciada
    Entonces la API debe responder con el código de estado HTTP 401
    Y la respuesta contiene el mensaje "Tu sesión expiró. Inicia sesión de nuevo."

  @HU02 @api @sesion @refresh_reutilizado
  Escenario: Un refresh token ya utilizado no sirve de nuevo
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando solicita renovar la sesión
    Y solicita renovar la sesión con el refresh token anterior
    Entonces la API debe responder con el código de estado HTTP 401
    Y la respuesta contiene el mensaje "Tu sesión expiró. Inicia sesión de nuevo."

  # Protección de los endpoints (no corresponde a un criterio de aceptación)
  @HU02 @api @sesion @sin_token
  Escenario: Un endpoint protegido rechaza peticiones sin access token
    Cuando consulta su perfil sin enviar un access token
    Entonces la API debe responder con el código de estado HTTP 401
    Y la respuesta tiene el formato de error de la API

  @HU02 @api @sesion @token_alterado
  Escenario: Un endpoint protegido rechaza un access token alterado
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando consulta su perfil con un access token alterado
    Entonces la API debe responder con el código de estado HTTP 401
    Y la respuesta tiene el formato de error de la API




# COBERTURA FUNCIONAL: qué criterios de aceptación tienen escenarios
#
# Criterios que NO pueden ser testeados desde el backend:
#
# Criterio de aceptación 6 - Mostrar u ocultar la contraseña
# Dado que un usuario se encuentra en la página “Iniciar sesión”
# Cuando pulsa el ícono del ojo del campo “Contraseña”
# Entonces el sistema muestra u oculta la contraseña escrita.
# Motivo: es un comportamiento visual del frontend.
#
# Criterio de aceptación 7 - Solicitud de cierre de sesión
# Dado que un usuario inició sesión
# Cuando pulsa su avatar en la barra superior
# Y pulsa la opción “Cerrar sesión”
# Entonces el sistema muestra la ventana de confirmación “¿Cerrar sesión? Tus proyectos se mantienen guardados.”.
# Motivo: el diálogo de confirmación es un comportamiento del frontend.
#
# Criterio de aceptación 9 - Cancelar el cierre de sesión
# Dado que un usuario ve el diálogo “¿Cerrar sesión?”
# Cuando pulsa el botón “Seguir aquí”, la tecla Esc o fuera del diálogo
# Entonces el sistema cierra el diálogo
# Y el usuario sigue en la misma pantalla.
# Motivo: cancelar no envía ninguna petición a la API; es comportamiento del frontend.

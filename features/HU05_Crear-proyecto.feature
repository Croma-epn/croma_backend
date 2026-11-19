# language: es
@HU05
Característica: Crear un proyecto de modelado
  Como estudiante
  Quiero crear un proyecto de modelado con nombre y descripción
  Para organizar el diseño de cada aplicación


  # Criterio de aceptación 2 - Creación exitosa de un proyecto
  # Dado que un estudiante se encuentra en el formulario “Crear proyecto”
  # Cuando escribe un nombre de proyecto
  # Y pulsa el botón “Crear proyecto”
  # Entonces el sistema muestra el lienzo vacío del proyecto
  # Y muestra el mensaje “Proyecto creado. Agrega tu primera pantalla.”
  #
  # Equivalente backend: la API responde 201 con el mensaje y los datos del proyecto
  # (con su id, el front lleva al estudiante al lienzo). El proyecto queda a nombre de
  # quien tiene la sesión iniciada. La descripción y la portada son opcionales; el nombre
  # se guarda sin espacios al inicio ni al final. Un estudiante puede tener varios
  # proyectos con el mismo nombre.
  @HU05 @CC2 @api @proyecto_creado
  Escenario: Creación exitosa de un proyecto solo con nombre
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando crea un proyecto con el nombre "App de delivery"
    Entonces la API debe responder con el código de estado HTTP 201
    Y la respuesta contiene el mensaje "Proyecto creado. Agrega tu primera pantalla."
    Y la respuesta incluye el id, el nombre y la fecha de creación del proyecto
    Y la respuesta indica que el proyecto no tiene portada
    Y el proyecto "App de delivery" queda guardado a nombre de "fernando.huilca@epn.edu.ec"

  @HU05 @CC2 @api @proyecto_con_descripcion
  Escenario: Creación exitosa de un proyecto con nombre y descripción
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando crea un proyecto con los siguientes datos:
      | nombre          | descripcion                 |
      | App de delivery | Pantallas para pedir comida |
    Entonces la API debe responder con el código de estado HTTP 201
    Y la respuesta incluye la descripción "Pantallas para pedir comida"
    Y el proyecto "App de delivery" queda guardado a nombre de "fernando.huilca@epn.edu.ec"

  @HU05 @CC2 @api @nombre_con_espacios_sobrantes
  Escenario: El nombre del proyecto se guarda sin espacios al inicio ni al final
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando crea un proyecto con el nombre "   App de delivery   "
    Entonces la API debe responder con el código de estado HTTP 201
    Y el proyecto "App de delivery" queda guardado a nombre de "fernando.huilca@epn.edu.ec"

  @HU05 @CC2 @api @nombre_repetido
  Escenario: Un estudiante puede crear dos proyectos con el mismo nombre
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Y que el estudiante ya tiene un proyecto llamado "App de delivery"
    Cuando crea un proyecto con el nombre "App de delivery"
    Entonces la API debe responder con el código de estado HTTP 201
    Y el estudiante "fernando.huilca@epn.edu.ec" tiene 2 proyectos llamados "App de delivery"

  @HU05 @CC2 @api @propietario_ajeno
  Escenario: El proyecto siempre queda a nombre de quien tiene la sesión iniciada
    Dado que existe una cuenta registrada con el correo "otra.persona@epn.edu.ec" y la contraseña "Password123"
    Y que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando crea un proyecto con el nombre "App de delivery" intentando asignarlo a la cuenta "otra.persona@epn.edu.ec"
    Entonces la API debe responder con el código de estado HTTP 201
    Y el proyecto "App de delivery" queda guardado a nombre de "fernando.huilca@epn.edu.ec"
    Y la cuenta "otra.persona@epn.edu.ec" no tiene ningún proyecto

  # Criterio de aceptación 3 - Nombre vacío
  # Dado que un estudiante se encuentra en el formulario “Crear proyecto”
  # Cuando borra el nombre, sale del campo “Nombre del proyecto” sin escribirlo o pulsa el botón “Crear proyecto” sin nombre
  # Entonces el sistema muestra al instante el mensaje “El nombre del proyecto es obligatorio.” bajo el campo
  # Y no crea el proyecto mientras el nombre esté vacío.
  #
  # Equivalente backend: la API también valida (el front se puede saltar); responde 400,
  # reporta el error en "nombre" y no crea el proyecto. Un nombre de solo espacios cuenta
  # como vacío.
  @HU05 @CC3 @api @validacion @nombre_vacio
  Escenario: Error al crear un proyecto con el nombre vacío
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando crea un proyecto con los siguientes datos:
      | nombre | descripcion                 |
      |        | Pantallas para pedir comida |
    Entonces la API debe responder con el código de estado HTTP 400
    Y la API debe reportar en el campo "nombre" el mensaje "El nombre del proyecto es obligatorio."
    Y no se crea ningún proyecto

  @HU05 @CC3 @api @validacion @nombre_ausente
  Escenario: Error al crear un proyecto sin enviar el campo nombre
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando crea un proyecto con los siguientes datos:
      | descripcion                 |
      | Pantallas para pedir comida |
    Entonces la API debe responder con el código de estado HTTP 400
    Y la API debe reportar en el campo "nombre" el mensaje "El nombre del proyecto es obligatorio."
    Y no se crea ningún proyecto

  @HU05 @CC3 @api @validacion @nombre_solo_espacios
  Escenario: Error al crear un proyecto con un nombre de solo espacios
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando crea un proyecto con el nombre "     "
    Entonces la API debe responder con el código de estado HTTP 400
    Y la API debe reportar en el campo "nombre" el mensaje "El nombre del proyecto es obligatorio."
    Y no se crea ningún proyecto

  # Criterio de aceptación 5 - Límite de caracteres
  # Dado que un estudiante se encuentra en el formulario “Crear proyecto”
  # Cuando llega a 30 caracteres en el nombre o a 150 en la descripción
  # Entonces el sistema no permite escribir más caracteres
  # Y muestra el mensaje de advertencia “Alcanzaste el máximo de N caracteres.”
  #
  # Equivalente backend: el front impide escribir más, pero la API también valida el
  # límite. Con exactamente 30 (nombre) o 150 (descripción) caracteres el proyecto se
  # crea; con uno más responde 400, reporta el error en el campo y no crea el proyecto.
  @HU05 @CC5 @api @limite_nombre_exacto
  Escenario: Se acepta un nombre de exactamente 30 caracteres
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando crea un proyecto con un nombre de 30 caracteres
    Entonces la API debe responder con el código de estado HTTP 201

  @HU05 @CC5 @api @validacion @limite_nombre_excedido
  Escenario: Error al crear un proyecto con un nombre de más de 30 caracteres
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando crea un proyecto con un nombre de 31 caracteres
    Entonces la API debe responder con el código de estado HTTP 400
    Y la API debe reportar en el campo "nombre" el mensaje "Alcanzaste el máximo de 30 caracteres."
    Y no se crea ningún proyecto

  @HU05 @CC5 @api @limite_descripcion_exacto
  Escenario: Se acepta una descripción de exactamente 150 caracteres
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando crea un proyecto con el nombre "App de delivery" y una descripción de 150 caracteres
    Entonces la API debe responder con el código de estado HTTP 201

  @HU05 @CC5 @api @validacion @limite_descripcion_excedido
  Escenario: Error al crear un proyecto con una descripción de más de 150 caracteres
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando crea un proyecto con el nombre "App de delivery" y una descripción de 151 caracteres
    Entonces la API debe responder con el código de estado HTTP 400
    Y la API debe reportar en el campo "descripcion" el mensaje "Alcanzaste el máximo de 150 caracteres."
    Y no se crea ningún proyecto

  # Criterio de aceptación 6 - Carga de la portada
  # Dado que un estudiante se encuentra en el formulario “Crear proyecto”
  # Cuando pulsa el botón “Subir imagen”
  # Y elige una imagen de hasta 4 MB
  # Entonces el sistema muestra la vista previa de la portada
  # Y muestra el botón “Quitar imagen”.
  #
  # Equivalente backend: la portada viaja junto con el nombre y la descripción en una sola
  # petición. La API la guarda en el almacén de imágenes y devuelve su dirección (URL).
  # Formatos admitidos: JPG, PNG y WebP. Tamaño máximo: 4 MB = 4 × 1024 × 1024 bytes
  # (4194304); una imagen de exactamente ese tamaño se acepta.
  @HU05 @CC6 @api @portada_valida
  Esquema del escenario: Creación exitosa de un proyecto con una portada en formato <formato>
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando crea un proyecto con el nombre "App de delivery" y una portada en formato "<formato>"
    Entonces la API debe responder con el código de estado HTTP 201
    Y la respuesta incluye la dirección (URL) de la portada
    Y la portada del proyecto "App de delivery" queda guardada en el almacén de imágenes

    Ejemplos:
      | formato |
      | JPG     |
      | PNG     |
      | WebP    |

  @HU05 @CC6 @api @portada_4mb_exactos
  Escenario: Se acepta una portada de exactamente 4 MB
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando crea un proyecto con el nombre "App de delivery" y una portada de 4194304 bytes
    Entonces la API debe responder con el código de estado HTTP 201
    Y la portada del proyecto "App de delivery" queda guardada en el almacén de imágenes

  # Criterio de aceptación 8 - Imagen demasiado pesada sin portada cargada
  # Dado que un estudiante se encuentra en el formulario “Crear proyecto”
  # Y no tiene una portada cargada
  # Cuando elige una imagen de más de 4 MB
  # Entonces el sistema no carga la imagen
  # Y muestra la advertencia “La imagen supera los 4 MB. Usa una más ligera. El proyecto se creará sin portada.”
  #
  # Equivalente backend: el front no envía la imagen y crea el proyecto sin portada. Si una
  # imagen de más de 4 MB llega igualmente a la API, esta responde 400 en el campo
  # "portada", no guarda la imagen y no crea el proyecto. El mensaje de la API no repite
  # "El proyecto se creará sin portada" porque, en la API, el proyecto no se crea.
  @HU05 @CC8 @api @validacion @portada_pesada
  Escenario: Error al crear un proyecto con una portada de más de 4 MB
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando crea un proyecto con el nombre "App de delivery" y una portada de 4194305 bytes
    Entonces la API debe responder con el código de estado HTTP 400
    Y la API debe reportar en el campo "portada" el mensaje "La imagen supera los 4 MB. Usa una más ligera."
    Y no se crea ningún proyecto
    Y no se guarda ninguna imagen en el almacén de imágenes

  # Criterio de aceptación 9 - Archivo que no es imagen como portada
  # Dado que un estudiante se encuentra en el formulario “Crear proyecto”
  # Y no tiene una portada cargada
  # Cuando elige un archivo que no es una imagen
  # Entonces el sistema no carga el archivo
  # Y muestra la advertencia “El archivo debe ser una imagen. El proyecto se creará sin portada.”
  #
  # Equivalente backend: si un archivo que no es una imagen JPG, PNG o WebP llega a la API,
  # esta responde 400 en el campo "portada", no guarda nada y no crea el proyecto. Se
  # revisa el contenido real del archivo, no su nombre ni su extensión.
  @HU05 @CC9 @api @validacion @portada_no_imagen
  Esquema del escenario: Error al usar como portada <tipo_de_archivo>
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Cuando crea un proyecto con el nombre "App de delivery" y como portada "<tipo_de_archivo>"
    Entonces la API debe responder con el código de estado HTTP 400
    Y la API debe reportar en el campo "portada" el mensaje "El archivo debe ser una imagen (JPG, PNG o WebP)."
    Y no se crea ningún proyecto
    Y no se guarda ninguna imagen en el almacén de imágenes

    Ejemplos:
      | tipo_de_archivo                      |
      | un documento PDF                     |
      | un archivo de texto                  |
      | un archivo de texto llamado .png     |
      | una imagen GIF                       |

  # Protección y fallos (no corresponden a un criterio de aceptación)
  @HU05 @api @sesion @sin_token
  Escenario: No se puede crear un proyecto sin una sesión iniciada
    Cuando crea un proyecto con el nombre "App de delivery" sin enviar un access token
    Entonces la API debe responder con el código de estado HTTP 401
    Y la respuesta tiene el formato de error de la API
    Y no se crea ningún proyecto

  @HU05 @api @almacen @almacen_no_disponible
  Escenario: Si falla el almacén de imágenes no se crea el proyecto
    Dado que el estudiante tiene una sesión iniciada con el correo "fernando.huilca@epn.edu.ec"
    Y que el almacén de imágenes no está disponible
    Cuando crea un proyecto con el nombre "App de delivery" y una portada en formato "PNG"
    Entonces la API debe responder con el código de estado HTTP 503
    Y la respuesta contiene el mensaje "No pudimos guardar la imagen. Inténtalo de nuevo."
    Y no se crea ningún proyecto




# COBERTURA FUNCIONAL: qué criterios de aceptación tienen escenarios
#
# Criterios que NO pueden ser testeados desde el backend:
#
# Criterio de aceptación 1 - Acceso al formulario
# Dado que un estudiante se encuentra en la página “Mis proyectos”
# Cuando pulsa la tarjeta “Crear proyecto”
# Entonces el sistema muestra el formulario “Crear proyecto”.
# Motivo: es navegación entre pantallas del frontend; no envía ninguna petición a la API.
#
# Criterio de aceptación 4 - Contador de caracteres
# Dado que un estudiante se encuentra en el formulario “Crear proyecto”
# Cuando escribe en “Nombre del proyecto” o en “Descripción”
# Entonces el sistema actualiza el contador del campo (x/30 en el nombre y x/150 en la descripción).
# Motivo: es un comportamiento visual del frontend.
#
# Criterio de aceptación 7 - Quitar la portada
# Dado que un estudiante cargó una portada en el formulario “Crear proyecto”
# Cuando pulsa el botón “Quitar imagen”
# Entonces el sistema deja vacía la vista previa.
# Motivo: la portada solo se envía al crear el proyecto; quitarla no envía ninguna petición a la API.
#
# Criterio de aceptación 10 - Archivo inválido con una portada ya cargada
# Dado que un estudiante cargó una portada válida en el formulario “Crear proyecto”
# Cuando elige una imagen de más de 4 MB o un archivo que no es una imagen
# Entonces el sistema conserva la portada que ya estaba cargada
# Y muestra la advertencia “Archivo inválido, se mantiene la portada actual.”
# Motivo: el frontend descarta el archivo inválido antes de enviar nada a la API.
#
# Criterio de aceptación 11 - Salir del formulario sin crear el proyecto
# Dado que un estudiante se encuentra en el formulario “Crear proyecto”
# Cuando pulsa el botón “Cancelar” o el logo “Croma” de la barra superior
# Entonces el sistema muestra la página “Mis proyectos” sin pedir confirmación
# Y el proyecto no se crea.
# Motivo: cancelar no envía ninguna petición a la API; es navegación del frontend.
#
# Criterio de aceptación 12 - Visualizar información escrita en proyecto no guardado
# Dado que un estudiante escribió datos o cargó una portada en el formulario “Crear proyecto”
# Y salió con el botón “Cancelar” o con el logo “Croma”
# Cuando vuelve a pulsar la tarjeta “Crear proyecto”
# Entonces el sistema muestra el formulario con el nombre, la descripción y la portada que había ingresado la última vez.
# Motivo: el borrador se conserva en el frontend; el backend no guarda proyectos incompletos.

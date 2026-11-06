# language: es
Característica: Registro de estudiante con correo institucional
  Como estudiante
  Quiero registrarme con mi correo institucional
  Para guardar mis modelos en una cuenta propia

  Escenario: Registro exitoso de un nuevo estudiante
    Dado que el estudiante no tiene una cuenta registrada en el sistema
    Cuando envía una petición de registro con el nombre "Fernando", el correo "fernando.huilca@epn.edu.ec" y la contraseña "Password123"
    Entonces la cuenta se crea exitosamente
    Y la API debe responder con el código de estado HTTP 201

  Escenario: Error al intentar registrar un correo ya existente
    Dado que ya existe una cuenta registrada con el correo "fernando.huilca@epn.edu.ec"
    Cuando se envía una petición de registro con el correo "fernando.huilca@epn.edu.ec"
    Entonces la API debe rechazar la creación
    Y la API debe responder con el código de estado HTTP 409
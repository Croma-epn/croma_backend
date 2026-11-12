from rest_framework import status
from rest_framework.views import exception_handler

# Mensaje general para errores de validación (400). No viene de un CC.
MENSAJE_DATOS_INVALIDOS = 'Revisa los datos ingresados.'


def _aplanar(valor):
    """Convierte cualquier estructura de errores de DRF en una lista simple de textos."""
    if isinstance(valor, (list, tuple)):
        return [texto for item in valor for texto in _aplanar(item)]
    if isinstance(valor, dict):
        return [texto for item in valor.values() for texto in _aplanar(item)]
    return [str(valor)]


def manejador_de_errores(exc, context):
    """
    Manejador de excepciones de DRF (se activa con EXCEPTION_HANDLER en settings.py).

    Toda respuesta de error de la API queda con la misma estructura:

        {
            "mensaje": "Texto general del error.",
            "errores": {"campo": ["Mensaje 1", "Mensaje 2"]}
        }

    "errores" siempre existe; queda vacío cuando el error no pertenece a un campo.
    """
    # DRF hace el trabajo base: convierte la excepción en una Response con su código HTTP.
    response = exception_handler(exc, context)
    if response is None:
        return None  # Error no controlado: Django responde 500

    datos = response.data
    errores = {}
    mensaje = None

    if isinstance(datos, dict) and set(datos) == {'detail'}:
        # Error sin campo: 404, 405, 415, JSON mal formado...
        mensaje = str(datos['detail'])
    elif isinstance(datos, dict):
        # Errores por campo: validación del serializer, correo duplicado...
        errores = {campo: _aplanar(valor) for campo, valor in datos.items()}
    else:
        # Lista de errores sin campo
        errores = {'non_field_errors': _aplanar(datos)}

    if mensaje is None:
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            mensaje = MENSAJE_DATOS_INVALIDOS
        else:
            # Para otros códigos (ej. 409) el mensaje es el primer error, el del CC.
            mensaje = next(
                (texto for lista in errores.values() for texto in lista),
                MENSAJE_DATOS_INVALIDOS,
            )

    response.data = {'mensaje': mensaje, 'errores': errores}
    return response
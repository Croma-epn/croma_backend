from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def saludo_croma(request):
    # Extraemos el valor 'nombre' del cuerpo de la petición (JSON)
    # Si no envían la variable 'nombre', usamos 'Estudiante' por defecto.
    nombre_recibido = request.data.get('nombre', 'Estudiante')
    
    return Response({
        "proyecto": "Croma",
        "mensaje": f"¡Hola {nombre_recibido}, la conexión Cliente-Servidor fue un éxito!",
        "estado": 200
    })


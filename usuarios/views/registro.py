from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from usuarios.serializers import RegistroUsuarioSerializer


class RegistroUsuarioView(APIView):

    @extend_schema(
        tags=['Usuarios'],
        summary="Registrar usuario",
        description="Permite registrar un estudiante con su correo institucional.",
        request=RegistroUsuarioSerializer,
        responses={
            201: OpenApiResponse(description="Usuario registrado correctamente."),
            409: OpenApiResponse(description="El correo ya está registrado.")
        }
    )
    def post(self, request):
        serializer = RegistroUsuarioSerializer(data=request.data)

        if not serializer.is_valid():
            # Interceptamos el error de unicidad para devolver el 409 acordado
            if 'correo' in serializer.errors and any(err.code == 'unique' for err in serializer.errors['correo']):
                return Response(
                    {"detail": "El correo ya está registrado."},
                    status=status.HTTP_409_CONFLICT
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(
            {"mensaje": "Usuario registrado correctamente"},
            status=status.HTTP_201_CREATED
        )
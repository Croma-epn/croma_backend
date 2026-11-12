from django.db import IntegrityError, transaction

from usuarios.exceptions import CorreoYaRegistrado
from usuarios.models import Usuario


def _correo_existe(correo):
    return Usuario.objects.filter(correo=correo).exists()


def registrar_usuario(*, nombre, correo, contrasena):
    """
    Crea una cuenta nueva (CC2) o lanza CorreoYaRegistrado si el correo ya existe (CC6).

    No valida formato (eso es del serializer) ni sabe nada de HTTP.
    Devuelve el Usuario creado.
    """
    # No se confía en que quien llame ya normalizó el correo.
    correo = correo.strip().lower()

    # 1) Comprobación rápida: cubre el caso normal sin provocar errores en la BD.
    if _correo_existe(correo):
        raise CorreoYaRegistrado()

    # 2) Garantía real: el índice único de la BD.
    #    Si dos peticiones con el mismo correo pasan la comprobación anterior a la vez,
    #    la segunda falla aquí con IntegrityError.
    try:
        # atomic() crea un "punto de guardado": si el INSERT falla, solo se deshace
        # esta parte y la conexión queda utilizable (en Postgres, un error dentro de
        # una transacción la deja inutilizable hasta que se hace rollback).
        with transaction.atomic():
            return Usuario.objects.create_user(
                correo=correo,
                password=contrasena,  # create_user guarda el hash, no el texto
                nombre=nombre,
            )
    except IntegrityError:
        # Se confirma que el motivo fue el correo duplicado y no otro problema.
        if _correo_existe(correo):
            raise CorreoYaRegistrado()
        raise
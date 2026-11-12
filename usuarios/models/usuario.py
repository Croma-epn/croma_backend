from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UsuarioManager(BaseUserManager):
    """Sabe crear usuarios y superusuarios usando el correo como identificador."""

    use_in_migrations = True

    def _crear(self, correo, password, **extra_fields):
        if not correo:
            raise ValueError('El correo es obligatorio.')
        usuario = self.model(correo=correo, **extra_fields)
        usuario.set_password(password)  # Guarda el HASH, nunca el texto original
        usuario.save(using=self._db)
        return usuario

    def create_user(self, correo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._crear(correo, password, **extra_fields)

    def create_superuser(self, correo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields['is_staff'] is not True:
            raise ValueError('Un superusuario debe tener is_staff=True.')
        if extra_fields['is_superuser'] is not True:
            raise ValueError('Un superusuario debe tener is_superuser=True.')
        return self._crear(correo, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Usuario de Croma.

    AbstractBaseUser aporta: el campo `password` (hash), set_password(),
    check_password() y last_login.
    PermissionsMixin aporta: is_superuser, groups y user_permissions.
    """

    nombre = models.CharField('nombre completo', max_length=100)
    correo = models.EmailField('correo electrónico', max_length=254, unique=True)

    # Nombres exigidos por Django (admin y autenticación): se dejan en inglés.
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    fecha_registro = models.DateTimeField(auto_now_add=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'correo'    # Con qué campo se identifica el usuario (login)
    EMAIL_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre']  # Extra que pide `createsuperuser` además de correo y contraseña

    class Meta:
        db_table = 'croma_usuario'
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def save(self, *args, **kwargs):
        # Red de seguridad: el correo siempre se guarda sin espacios y en minúsculas,
        # sin importar si el usuario se crea desde la API, el admin o el shell.
        # Así "Ana@x.com" y "ana@x.com" son el mismo correo y unique=True lo detecta.
        self.correo = self.correo.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.correo
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from usuarios.models import Usuario


# Los formularios originales de Django están hechos para el User con "username".
# Con un modelo propio hay que indicarles qué modelo y qué campos usar.
class UsuarioCreationForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('correo', 'nombre')


class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = '__all__'


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    form = UsuarioChangeForm
    add_form = UsuarioCreationForm

    list_display = ('correo', 'nombre', 'is_staff', 'is_active', 'fecha_registro')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('correo', 'nombre')
    ordering = ('correo',)
    readonly_fields = ('fecha_registro', 'last_login')

    # Pantalla de edición
    fieldsets = (
        (None, {'fields': ('correo', 'password')}),
        ('Datos personales', {'fields': ('nombre',)}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('last_login', 'fecha_registro')}),
    )

    # Pantalla de creación
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('correo', 'nombre', 'password1', 'password2'),
        }),
    )
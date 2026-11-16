from django.contrib import admin

from proyectos.models import Proyecto


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'propietario', 'creado_en')
    search_fields = ('nombre', 'propietario__correo')
    readonly_fields = ('creado_en', 'actualizado_en')
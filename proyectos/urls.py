from django.urls import path

from .views import CrearProyectoView

urlpatterns = [
    path('', CrearProyectoView.as_view(), name='crear-proyecto'),
]   
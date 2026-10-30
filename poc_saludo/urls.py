from django.urls import path
from . import views

urlpatterns = [
    path('saludar/', views.saludo_croma, name='saludar'),
]
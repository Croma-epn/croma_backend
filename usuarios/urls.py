from django.urls import path

from .views import LoginView, LogoutView, PerfilView, RegistroUsuarioView, RenovarSesionView

urlpatterns = [
    path('registro/', RegistroUsuarioView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', RenovarSesionView.as_view(), name='renovar-sesion'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('yo/', PerfilView.as_view(), name='perfil'),
]
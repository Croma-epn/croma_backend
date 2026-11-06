from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=128) # Sin "ñ", respetando el JSON acordado con Mateo

    class Meta:
        db_table = 'croma_usuario'

    def __str__(self):
        return self.correo
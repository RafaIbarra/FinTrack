from django.db import models


# Create your models here.

class Usuarios(models.Model):
    
    Id = models.AutoField(primary_key=True, help_text="Campo de identificacion unica autogenerado")
    NombreUsuario=models.CharField(max_length=200,blank=False, help_text="Nombre completo")
    ApellidoUsuario=models.CharField(max_length=200,blank=False, help_text="Apellidos completo")
    UserName=models.CharField(max_length=100,blank=False,unique=True, help_text="Campo de identificacion del usuario unico")
    Correo=models.EmailField(blank=True, help_text="Correo electronico")
    FechaRegistro=models.DateTimeField("fecha registro", help_text="Fecha de registro del usuario")
    LastLogin=models.DateTimeField("Ultima conexion", help_text="Fecha de registro del usuario")
    
    class Meta:
        db_table="Usuarios"
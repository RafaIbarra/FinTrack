from django.db import models
from FinTrackApp.Modelos.Usuarios import Usuarios
class SesionesActivas(models.Model):
    Id = models.AutoField(primary_key=True)
    FechaConexion = models.DateTimeField(
        "Fecha conexion",
        help_text="Fecha/hora en que se conecto"
    )
    Dispositivo=models.CharField(max_length=200,blank=True, help_text="Dispositivo Conexion")
    IpConexion=models.CharField(max_length=200,blank=True, help_text="Ip desde donde se conecto")
    Usuario = models.ForeignKey(
        Usuarios, 
        db_column='UsuarioId',
        on_delete=models.PROTECT,
        related_name='sesion_activa_usuario'
    )
    IdDjangoUser = models.IntegerField(
        "ID Usuario Django",
        help_text="ID del usuario en la tabla User de Django"
    )
    TokenSesion = models.CharField(
        max_length=300, 
        unique=True,
        db_index=True,
        help_text="Token para validación de sesión"
    )
    FechaExpiracion = models.DateTimeField(
        "Fecha Expiración",
        db_index=True,  # ← Índice para limpieza masiva
        help_text="Fecha/hora hasta donde tendrá vigencia la conexión del usuario"
    )
    ConexionActiva=models.BooleanField(default=True)
    
    class Meta:
        db_table = "SesionesActivas"

    
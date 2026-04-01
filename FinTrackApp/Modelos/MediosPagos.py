from django.db import models
from FinTrackApp.Modelos.Usuarios import Usuarios



# Create your models here.

class MediosPagos(models.Model):
    
    Id = models.AutoField(primary_key=True, help_text="Campo de identificacion unica autogenerado")
    NombreMedioPago=models.CharField(max_length=200,blank=False, help_text="Nombre completo")
    FechaRegistro=models.DateTimeField("fecha registro", help_text="Fecha de registro del Medio",auto_now_add=True)
    Observacion=models.CharField(max_length=200,blank=True, help_text="Alguna observacion sobre el medio")
    Usuario = models.ForeignKey(
        Usuarios, 
        db_column='UsuarioId',
        on_delete=models.PROTECT,
        related_name='medio_pago_usuario'
    )
    
    IsActive=models.BooleanField(default=True)
    FechaActualizacion=models.DateTimeField("fecha registro", help_text="Fecha de Actualizacion",auto_now_add=True)
    
    class Meta:
        db_table="MediosPagos"
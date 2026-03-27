from django.db import models
from FinTrackApp.Modelos.Usuarios import Usuarios
from FinTrackApp.Modelos.TiposIngresos import TiposIngresos


# Create your models here.

class Ingresos(models.Model):
    
    Id = models.AutoField(primary_key=True, help_text="Campo de identificacion unica autogenerado")
    NombreIngreso=models.CharField(max_length=200,blank=False, help_text="Nombre completo")
    FechaRegistro=models.DateTimeField("fecha registro", help_text="Fecha de registro de la Categoria")
    Observacion=models.CharField(max_length=200,blank=True, help_text="Alguna observacion sobre el gasto")
    Usuario = models.ForeignKey(
        Usuarios, 
        db_column='UsuarioId',
        on_delete=models.PROTECT,
        related_name='ingreso_usuario'
    )
    
    TipoIngreso = models.ForeignKey(
        TiposIngresos, 
        db_column='TipoId',
        on_delete=models.PROTECT,
        related_name='tipo_ingreso_usuario'
    )
    
    
    class Meta:
        db_table="Ingresos"
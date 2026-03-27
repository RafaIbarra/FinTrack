from django.db import models
from FinTrackApp.Modelos.Usuarios import Usuarios
from FinTrackApp.Modelos.CategoriasGastos import CategoriasGastos
from FinTrackApp.Modelos.TiposGastos import TiposGastos


# Create your models here.

class Gastos(models.Model):
    
    Id = models.AutoField(primary_key=True, help_text="Campo de identificacion unica autogenerado")
    NombreGasto=models.CharField(max_length=200,blank=False, help_text="Nombre completo")
    FechaRegistro=models.DateTimeField("fecha registro", help_text="Fecha de registro de la Categoria")
    Observacion=models.CharField(max_length=200,blank=True, help_text="Alguna observacion sobre el gasto")
    Usuario = models.ForeignKey(
        Usuarios, 
        db_column='UsuarioId',
        on_delete=models.PROTECT,
        related_name='gasto_usuario'
    )
    Categoria = models.ForeignKey(
        CategoriasGastos, 
        db_column='CategoriaID',
        on_delete=models.PROTECT,
        related_name='categoria_gasto_usuario'
    )
    TipoGasto = models.ForeignKey(
        TiposGastos, 
        db_column='TipoId',
        on_delete=models.PROTECT,
        related_name='tipo_gasto_usuario'
    )
    
    
    class Meta:
        db_table="Gastos"
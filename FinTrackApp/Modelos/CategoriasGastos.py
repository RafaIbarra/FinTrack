from django.db import models
from FinTrackApp.Modelos.Usuarios import Usuarios

# Create your models here.

class CategoriasGastos(models.Model):
    
    Id = models.AutoField(primary_key=True, help_text="Campo de identificacion unica autogenerado")
    NombreCategoria=models.CharField(max_length=200,blank=False, help_text="Nombre completo")
    FechaRegistro=models.DateTimeField("fecha registro", help_text="Fecha de registro de la Categoria")
    Observacion=models.CharField(max_length=200,blank=True, help_text="Alguna observacion sobre la categoria")
    Usuario = models.ForeignKey(
        Usuarios, 
        db_column='UsuarioId',
        on_delete=models.PROTECT,
        related_name='categoria_usuario'
    )
    
    
    class Meta:
        db_table="CategoriasGastos"
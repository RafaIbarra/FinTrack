from django.db import models


# Create your models here.

class TiposGastos(models.Model):
    
    Id = models.AutoField(primary_key=True, help_text="Campo de identificacion unica autogenerado")
    NombreTipoGasto=models.CharField(max_length=200,blank=False, help_text="Nombre completo")
    FechaRegistro=models.DateTimeField("fecha registro", help_text="Fecha de registro del Tipo")
    
    
    
    class Meta:
        db_table="TiposGastos"
from django.db import models


# Create your models here.

class TiposIngresos(models.Model):
    
    Id = models.IntegerField(primary_key=True, help_text="Campo de identificación única, se debe asignar manualmente")
    NombreTipoIngreso=models.CharField(max_length=200,blank=False, help_text="Nombre completo")
    FechaRegistro=models.DateTimeField("fecha registro", help_text="Fecha de registro del Tipo",auto_now_add=True)
    
    class Meta:
        db_table="TiposIngresos"
from django.db import models
from FinTrackApp.Modelos.Usuarios import Usuarios
from django.utils import timezone
class Empresas(models.Model):
    
    Id = models.AutoField(primary_key=True, help_text="Campo de identificacion unica autogenerado")
    NombreEmpresa = models.CharField(max_length=200, blank=True, help_text="Alguna observacion sobre la empresa")
    Ruc = models.CharField(max_length=50, blank=True, help_text="RUC de la empresa")
    
    # Cambiado: ImageField en lugar de URLField
    UrlImg = models.ImageField(
        upload_to='Empresas/',      # Carpeta donde se guardarán las imágenes
        blank=True, 
        null=True,
        help_text="Logo de la empresa"
    )
    
    FechaRegistro = models.DateTimeField(
        "fecha registro", 
        help_text="Fecha de registro de la empresa",
        default=timezone.now
    )

    class Meta:
        db_table = "Empresas"
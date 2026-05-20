# Empresas.py
from django.db import models
from FinTrackApp.Modelos.Usuarios import Usuarios
from django.utils import timezone


class Empresas(models.Model):
    
    Id = models.AutoField(primary_key=True, help_text="Campo de identificacion unica autogenerado")
    NombreEmpresa = models.CharField(max_length=200, blank=True, help_text="Nombre de la empresa")
    Ruc = models.CharField(max_length=50, blank=True, help_text="RUC de la empresa")
    
    # Cambiado: URLField para almacenar la URL de R2
    UrlImg = models.URLField(
        max_length=500,
        blank=True, 
        null=True,
        help_text="URL del logo en Cloudflare R2 Storage"
    )
    
    FechaRegistro = models.DateTimeField(
        "fecha registro", 
        help_text="Fecha de registro de la empresa",
        default=timezone.now
    )

    def get_storage_path(self):
        """
        Extrae bucket y path de la URL del logo.
        Compatible con R2.
        """
        if not self.UrlImg:
            return None
        
        import re
        
        # Patrón R2 nativo
        pattern_r2 = r'\.r2\.cloudflarestorage\.com/([^/]+)/(.+)'
        match = re.search(pattern_r2, self.UrlImg)
        if match:
            return {
                'provider': 'r2',
                'bucket': match.group(1),
                'path': match.group(2)
            }
        
        # Patrón R2 custom domain
        pattern_r2_custom = r'fintrack-file-[^/]+\.rafaelibarra\.xyz/(.+)'
        match = re.search(pattern_r2_custom, self.UrlImg)
        if match:
            return {
                'provider': 'r2',
                'bucket': 'fintrack-file-dev-empresas',  # o prod según corresponda
                'path': match.group(1)
            }
        
        return None

    class Meta:
        db_table = "Empresas"
# MovimientosGastos.py
from django.db import models
from FinTrackApp.Modelos.Usuarios import Usuarios
from django.utils import timezone
from datetime import datetime
from FinTrackApp.Modelos.Empresas import Empresas


class MovimientosGastos(models.Model):
    
    Id = models.AutoField(primary_key=True, help_text="Campo de identificacion unica autogenerado")
    FechaGasto = models.DateField("fecha Operacion", help_text="Fecha de registro del gasto")
    Observacion = models.CharField(max_length=200, blank=True, help_text="Alguna observacion sobre el gasto")
    
    Usuario = models.ForeignKey(
        Usuarios, 
        db_column='UsuarioId',
        on_delete=models.PROTECT,
        related_name='movimiento_gasto_usuario'
    )
    
    Empresa = models.ForeignKey(
        Empresas, 
        db_column='EmpresaId',
        on_delete=models.PROTECT,
        related_name='movimiento_gasto_empresa',
        default=1
    )
    
    UrlImg = models.URLField(
        max_length=500,
        blank=True, 
        null=True,
        help_text="URL de la imagen en Cloudflare R2 Storage"
    )
    
    ObsImg = models.CharField(
        max_length=500, 
        blank=True, 
        null=True,
    )
    
    FechaRegistro = models.DateTimeField(
        "fecha registro", 
        help_text="Fecha de registro del gasto",
        default=timezone.now
    )

    def get_storage_path(self):
        """
        Extrae bucket y path de la URL de imagen.
        Compatible con Supabase y Cloudflare R2.
        """
        if not self.UrlImg:
            return None
        
        import re
        
        # Patrón Supabase
        pattern_supabase = r'/storage/v1/object/public/([^/]+)/(.+)'
        match = re.search(pattern_supabase, self.UrlImg)
        if match:
            return {
                'provider': 'supabase',
                'bucket': match.group(1),
                'path': match.group(2)
            }
        
        # Patrón R2 nativo: https://xxx.r2.cloudflarestorage.com/bucket/path
        pattern_r2 = r'\.r2\.cloudflarestorage\.com/([^/]+)/(.+)'
        match = re.search(pattern_r2, self.UrlImg)
        if match:
            return {
                'provider': 'r2',
                'bucket': match.group(1),
                'path': match.group(2)
            }
        
        # Patrón R2 custom domain: https://pub-xxx.r2.dev/bucket/path
        pattern_r2_custom = r'r2\.dev/([^/]+)/(.+)'
        match = re.search(pattern_r2_custom, self.UrlImg)
        if match:
            return {
                'provider': 'r2',
                'bucket': match.group(1),
                'path': match.group(2)
            }
        
        return None

    class Meta:
        db_table = "MovimientosGastos"
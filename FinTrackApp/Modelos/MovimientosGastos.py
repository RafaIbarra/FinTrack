from django.db import models
from FinTrackApp.Modelos.Usuarios import Usuarios



# Create your models here.

class MovimientosGastos(models.Model):
    
    Id = models.AutoField(primary_key=True, help_text="Campo de identificacion unica autogenerado")
    FechaGasto=models.DateTimeField("fecha registro", help_text="Fecha de registro del gasto",auto_now_add=True)
    Observacion=models.CharField(max_length=200,blank=True, help_text="Alguna observacion sobre el gasto")
    Usuario = models.ForeignKey(
        Usuarios, 
        db_column='UsuarioId',
        on_delete=models.PROTECT,
        related_name='movimiento_gasto_usuario'
    )
    UrlImg = models.URLField(
        max_length=500,  # Aumenté la longitud para URLs largas
        blank=True, 
        null=True,
        help_text="URL de la imagen en Supabase Storage"
    )
    def get_supabase_path(self):
        if self.UrlImg:
            # Extraer el path de la URL completa
            import re
            pattern = r'/storage/v1/object/public/([^/]+)/(.+)'
            match = re.search(pattern, self.UrlImg)
            if match:
                return {
                    'bucket': match.group(1),
                    'path': match.group(2)
                }
        return None



    class Meta:
        db_table="MovimientosGastos"
from django.db import models
from FinTrackApp.Modelos.MovimientosGastos import MovimientosGastos
from FinTrackApp.Modelos.Gastos import Gastos



# Create your models here.

class MovimientosGastosDetalles(models.Model):
    
    Id = models.AutoField(primary_key=True, help_text="Campo de identificacion unica autogenerado")
    MontoGasto=models.IntegerField()
    FechaRegistro=models.DateTimeField("fecha registro", help_text="Fecha de registro del gasto",auto_now_add=True)
    MovimientoGasto = models.ForeignKey(
        MovimientosGastos, 
        db_column='MovimientoId',
        on_delete=models.PROTECT,
        related_name='movimiento_gasto_cabecera_detalle'
    )
    GastoUsuario=models.ForeignKey(
        Gastos, 
        db_column='GastoId',
        on_delete=models.PROTECT,
        related_name='movimiento_gasto_seleccionado'
    )
    
    
    class Meta:
        db_table="MovimientosGastosDetalles"
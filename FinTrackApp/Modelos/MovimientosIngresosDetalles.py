from django.db import models
from FinTrackApp.Modelos.MovimientosIngresos import MovimientosIngresos
from FinTrackApp.Modelos.Ingresos import Ingresos



# Create your models here.

class MovimientosIngresosDetalles(models.Model):
    
    Id = models.AutoField(primary_key=True, help_text="Campo de identificacion unica autogenerado")
    MontoIngreso=models.IntegerField()
    FechaRegistro=models.DateTimeField("fecha registro", help_text="Fecha de registro del gasto",auto_now_add=True)
    MovimientoIngreso = models.ForeignKey(
        MovimientosIngresos, 
        db_column='MovimientoId',
        on_delete=models.PROTECT,
        related_name='movimiento_ingreso_cabecera_detalle'
    )
    IngresoUsuario=models.ForeignKey(
        Ingresos, 
        db_column='IngresoId',
        on_delete=models.PROTECT,
        related_name='movimiento_ingreso_seleccionado'
    )
    
    
    class Meta:
        db_table="MovimientosIngresosDetalles"
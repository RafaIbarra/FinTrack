from django.db import models
from FinTrackApp.Modelos.MovimientosGastos import MovimientosGastos
from FinTrackApp.Modelos.MediosPagos import MediosPagos



# Create your models here.

class MovimientosGastosMediosPagos(models.Model):
    
    Id = models.AutoField(primary_key=True, help_text="Campo de identificacion unica autogenerado")
    FechaRegistro=models.DateTimeField("fecha registro", help_text="Fecha de registro de la forma de pago",auto_now_add=True)
    MontoMedioPago=models.IntegerField()
    MovimientoGasto = models.ForeignKey(
        MovimientosGastos, 
        db_column='MovimientoId',
        on_delete=models.PROTECT,
        related_name='movimiento_gasto_cabecera_medio'
    )
    MedioPago=models.ForeignKey(
        MediosPagos, 
        db_column='MedioPagoId',
        on_delete=models.PROTECT,
        related_name='movimiento_gasto_medio_pago'
    )
    
    
    
    class Meta:
        db_table="MovimientosGastosMediosPagos"
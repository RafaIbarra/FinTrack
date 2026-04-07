from rest_framework import serializers
from FinTrackApp.Modelos.MovimientosIngresosDetalles import MovimientosIngresosDetalles

class InfoMovimientosIngresosDetallesSerializer(serializers.ModelSerializer):
    FechaRegistro= serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S")
    NombreIngreso=serializers.CharField(source='IngresoUsuario.NombreIngreso', read_only=True)
    class Meta:
        model = MovimientosIngresosDetalles
        fields =  ['Id','MontoIngreso','FechaRegistro','IngresoUsuario','NombreIngreso']
        
        
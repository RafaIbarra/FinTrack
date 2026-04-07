from rest_framework import serializers
from FinTrackApp.Modelos.MovimientosIngresos import MovimientosIngresos
from FinTrackApp.Serializadores.SerilizadoresModelos.MovimientosIngresosDetallesSerializers import InfoMovimientosIngresosDetallesSerializer


class InfoMovimientoIngresoSerializer(serializers.ModelSerializer):
    FechaIngreso = serializers.DateField(format="%d/%m/%Y")
    FechaRegistro= serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S")
    NombreUsuario=serializers.CharField(source='Usuario.UserName', read_only=True)
    DetalleIngresos = InfoMovimientosIngresosDetallesSerializer(
        source='movimiento_ingreso_cabecera_detalle',  # related_name definido en el FK
        many=True,
        read_only=True
    )
    
    TotalMovimiento = serializers.IntegerField(read_only=True) 
    class Meta:
        model = MovimientosIngresos
        fields =  ['Id','FechaIngreso','Observacion','Usuario','NombreUsuario','UrlImg','ObsImg','TotalMovimiento','FechaRegistro','DetalleIngresos']
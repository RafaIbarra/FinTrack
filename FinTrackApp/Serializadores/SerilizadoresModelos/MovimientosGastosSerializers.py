from rest_framework import serializers
from FinTrackApp.Modelos.MovimientosGastos import MovimientosGastos
from FinTrackApp.Serializadores.SerilizadoresModelos.MovimientosGastosDetallesSerializers import InfoMovimientosGastosDetallesSerializer
from FinTrackApp.Serializadores.SerilizadoresModelos.MovimientosGastosMediosPagosSerializers import InfoMovimientosGastosMediosPagosSerializer

class InfoMovimientosGastosSerializer(serializers.ModelSerializer):
    FechaGasto = serializers.DateField(format="%d/%m/%Y")
    FechaRegistro= serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S")
    NombreUsuario=serializers.CharField(source='Usuario.UserName', read_only=True)
    NombreEmpresa=serializers.CharField(source='Empresa.NombreEmpresa', read_only=True)
    LogoEmpresa=serializers.CharField(source='Empresa.UrlImg', read_only=True)
    DetalleGastos = InfoMovimientosGastosDetallesSerializer(
        source='movimiento_gasto_cabecera_detalle',  # related_name definido en el FK
        many=True,
        read_only=True
    )
    DetalleMediosPagos= InfoMovimientosGastosMediosPagosSerializer(
        source='movimiento_gasto_cabecera_medio',  # related_name definido en el FK
        many=True,
        read_only=True
    )
    TotalMovimiento = serializers.IntegerField(read_only=True) 
    class Meta:
        model = MovimientosGastos
        fields =  ['Id','FechaGasto','Empresa','NombreEmpresa','LogoEmpresa',
                   'Observacion','Usuario','NombreUsuario','UrlImg','TotalMovimiento',
                   'FechaRegistro','DetalleGastos','DetalleMediosPagos']



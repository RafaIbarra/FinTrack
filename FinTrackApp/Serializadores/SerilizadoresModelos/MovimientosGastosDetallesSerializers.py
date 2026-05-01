from rest_framework import serializers
from FinTrackApp.Modelos.MovimientosGastosDetalles import MovimientosGastosDetalles

class InfoMovimientosGastosDetallesSerializer(serializers.ModelSerializer):
    FechaRegistro= serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S")
    NombreGasto=serializers.CharField(source='GastoUsuario.NombreGasto', read_only=True)
    CategoriaGasto = serializers.CharField(source='GastoUsuario.Categoria.Id', read_only=True)
    NombreCategoriaGasto = serializers.CharField(source='GastoUsuario.Categoria.NombreCategoria', read_only=True)
    
    class Meta:
        model = MovimientosGastosDetalles
        fields =  ['Id','MontoGasto','FechaRegistro','GastoUsuario','NombreGasto','CategoriaGasto','NombreCategoriaGasto']

class InfoRegistroMovimientoGastoDetalleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MovimientosGastosDetalles
        fields =  ['Id','MontoGasto','GastoUsuario']
        
        



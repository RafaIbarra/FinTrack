from rest_framework import serializers
from FinTrackApp.Modelos.MovimientosGastosMediosPagos import MovimientosGastosMediosPagos

class InfoMovimientosGastosMediosPagosSerializer(serializers.ModelSerializer):
    FechaRegistro= serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S")
    NombreMedioPago=serializers.CharField(source='MedioPago.NombreMedioPago', read_only=True)
    class Meta:
        model = MovimientosGastosMediosPagos
        fields =  ['Id','MontoMedioPago','FechaRegistro','MedioPago','NombreMedioPago']

class InfoRegistroMovimientoGastoMediosPagosSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MovimientosGastosMediosPagos
        fields =  ['Id','MontoMedioPago','MedioPago']
        
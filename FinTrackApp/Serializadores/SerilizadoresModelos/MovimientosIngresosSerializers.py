from rest_framework import serializers
from FinTrackApp.Modelos.MovimientosIngresos import MovimientosIngresos



class InfoMovimientoIngresoSerializer(serializers.ModelSerializer):
    FechaIngreso = serializers.DateField(format="%d/%m/%Y")
    FechaRegistro= serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S")
    NombreUsuario=serializers.CharField(source='Usuario.UserName', read_only=True)
    NombreIngreso=serializers.CharField(source='IngresoUsuario.NombreIngreso', read_only=True)
    NombreEmpresa=serializers.CharField(source='Empresa.NombreEmpresa', read_only=True)
    LogoEmpresa=serializers.CharField(source='Empresa.UrlImg', read_only=True)

    class Meta:
        model = MovimientosIngresos
        fields =  ['Id','FechaIngreso','IngresoUsuario','NombreIngreso','Empresa','NombreEmpresa','LogoEmpresa','MontoIngreso',
                   'Observacion','Usuario','NombreUsuario','UrlImg','ObsImg','FechaRegistro']
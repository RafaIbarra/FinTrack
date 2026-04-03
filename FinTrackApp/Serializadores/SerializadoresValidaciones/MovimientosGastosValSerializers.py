from rest_framework import serializers
from FinTrackApp.Modelos.Gastos import Gastos
from FinTrackApp.Modelos.MediosPagos import MediosPagos


class VerificacionGastoUsuarioSerializer(serializers.Serializer):
    idgasto = serializers.IntegerField()
    monto = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_idgasto(self, value):
        usuario_id = self.context.get('usuario_id')
        if not Gastos.objects.filter(Id=value, Usuario_id=usuario_id).exists():
            raise serializers.ValidationError(
                f"El gasto con ID {value} no existe o no pertenece al usuario"
            )
        return value

    def validate_monto(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0")
        return value

    class Meta:
        def validate_list(self, data):  
            if not data:
                raise serializers.ValidationError("Debe enviar al menos un gasto")
            ids = [item['idgasto'] for item in data]
            if len(ids) != len(set(ids)):
                raise serializers.ValidationError("No se permiten IDs de gasto duplicados")
            return data

        list_serializer_class = type(
            'GastoListSerializer',
            (serializers.ListSerializer,),
            {'validate': validate_list}
        )


class VerificacionMedioPagoUsuarioSerializer(serializers.Serializer):
    idmedio = serializers.IntegerField()
    monto = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_idmedio(self, value):
        usuario_id = self.context.get('usuario_id')
        if not MediosPagos.objects.filter(Id=value, Usuario_id=usuario_id,IsActive=True).exists():
            raise serializers.ValidationError(
                f"El medio de pago con ID {value} no existe, no esta activo o no pertenece al usuario"
            )
        return value

    def validate_monto(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0")
        return value

    class Meta:
        def validate_list(self, data):  
            if not data:
                raise serializers.ValidationError("Debe enviar al menos un medio")
            ids = [item['idmedio'] for item in data]
            if len(ids) != len(set(ids)):
                raise serializers.ValidationError("No se permiten IDs de medio duplicados")
            return data

        list_serializer_class = type(
            'GastoListSerializer',
            (serializers.ListSerializer,),
            {'validate': validate_list}
        )
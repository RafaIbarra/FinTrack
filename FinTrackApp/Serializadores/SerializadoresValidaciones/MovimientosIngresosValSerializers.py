from rest_framework import serializers
from FinTrackApp.Modelos.Ingresos import Ingresos

class VerificacionIngresoUsuarioSerializer(serializers.Serializer):
    idingreso = serializers.IntegerField()
    monto = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_idingreso(self, value):
        usuario_id = self.context.get('usuario_id')
        if not Ingresos.objects.filter(Id=value, Usuario_id=usuario_id).exists():
            raise serializers.ValidationError(
                f"El ingreso con ID {value} no existe o no pertenece al usuario"
            )
        return value

    def validate_monto(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0")
        return value

    class Meta:
        def validate_list(self, data):  
            if not data:
                raise serializers.ValidationError("Debe enviar al menos un ingreso")
            ids = [item['idingreso'] for item in data]
            if len(ids) != len(set(ids)):
                raise serializers.ValidationError("No se permiten IDs de ingresos duplicados")
            return data

        list_serializer_class = type(
            'IngresoListSerializer',
            (serializers.ListSerializer,),
            {'validate': validate_list}
        )

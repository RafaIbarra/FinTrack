from rest_framework import serializers
from FinTrackApp.Modelos.Ingresos import Ingresos

class InfoIngresoSerializer(serializers.ModelSerializer):
    FechaRegistro= serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S")
    NombreTipoIngreso = serializers.CharField(source='TipoIngreso.NombreTipoIngreso', read_only=True)
    class Meta:
        model = Ingresos
        fields =  ['Id','NombreIngreso','Observacion','Usuario','FechaRegistro','TipoIngreso','NombreTipoIngreso']


class RegistroIngresoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingresos
        fields = '__all__'

    def validate(self, data):
        usuario_id = self.initial_data.get('Usuario')

        # Ya no necesita buscar la instancia por Id
        # si viene de PUT, self.instance ya existe (lo asignó la vista)
        # si viene de POST, self.instance es None

        nombre = data.get('NombreIngreso')
        if nombre:
            queryset = Ingresos.objects.filter(
                NombreIngreso=nombre,
                Usuario_id=usuario_id
            )
            if self.instance:
                queryset = queryset.exclude(Id=self.instance.Id)

            if queryset.exists():
                raise serializers.ValidationError(
                    {"NombreGasto": "Ya existe un ingreso con este nombre para este usuario."}
                )

        return data
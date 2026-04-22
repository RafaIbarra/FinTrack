from rest_framework import serializers
from FinTrackApp.Modelos.Gastos import Gastos

class InfoGastoSerializer(serializers.ModelSerializer):
    FechaRegistro= serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S")
    NombreCategoria = serializers.CharField(source='Categoria.NombreCategoria', read_only=True)
    NombreTipoGasto = serializers.CharField(source='TipoGasto.NombreTipoGasto', read_only=True)
    class Meta:
        model = Gastos
        fields =  ['Id','NombreGasto','Observacion','Usuario','FechaRegistro','Categoria','NombreCategoria','TipoGasto','NombreTipoGasto']

class InfoGastoReferencialSerializer(serializers.ModelSerializer):
    
    NombreCategoria = serializers.CharField(source='Categoria.NombreCategoria', read_only=True)
    NombreTipoGasto = serializers.CharField(source='TipoGasto.NombreTipoGasto', read_only=True)
    MontoGasto = serializers.IntegerField(default=0, read_only=True)
    class Meta:
        model = Gastos
        fields =  ['Id','NombreGasto','MontoGasto','NombreCategoria','NombreTipoGasto']


class RegistroGastoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gastos
        fields = '__all__'

    def validate(self, data):
        usuario_id = self.initial_data.get('Usuario')

        # Ya no necesita buscar la instancia por Id
        # si viene de PUT, self.instance ya existe (lo asignó la vista)
        # si viene de POST, self.instance es None

        nombre = data.get('NombreGasto')
        if nombre:
            queryset = Gastos.objects.filter(
                NombreGasto=nombre,
                Usuario_id=usuario_id
            )
            if self.instance:
                queryset = queryset.exclude(Id=self.instance.Id)

            if queryset.exists():
                raise serializers.ValidationError(
                    {"NombreGasto": "Ya existe un gasto con este nombre para este usuario."}
                )

        return data
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from FinTrackApp.Modelos.CategoriasGastos import CategoriasGastos


class InfoCategoriaGastoSerializer(serializers.ModelSerializer):
    FechaRegistro= serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S")
    usuario_nombre = serializers.CharField(source='Usuario.NombreUsuario', read_only=True)

    class Meta:
        model = CategoriasGastos
        fields = ['Id','NombreCategoria','Observacion','Usuario','FechaRegistro','usuario_nombre']


class RegistroCategoriaGastoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriasGastos
        fields = '__all__'

    def validate(self, data):
        usuario_id = self.initial_data.get('Usuario')

        # Ya no necesita buscar la instancia por Id
        # si viene de PUT, self.instance ya existe (lo asignó la vista)
        # si viene de POST, self.instance es None

        nombre = data.get('NombreCategoria')
        if nombre:
            queryset = CategoriasGastos.objects.filter(
                NombreCategoria=nombre,
                Usuario_id=usuario_id
            )
            if self.instance:
                queryset = queryset.exclude(Id=self.instance.Id)

            if queryset.exists():
                raise serializers.ValidationError(
                    {"NombreCategoria": "Ya existe una categoría con este nombre para este usuario."}
                )

        return data
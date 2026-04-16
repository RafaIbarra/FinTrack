from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from FinTrackApp.Modelos.Empresas import Empresas


class InfoEmpresasSerializer(serializers.ModelSerializer):
    FechaRegistro= serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S")
    

    class Meta:
        model = Empresas
        fields = '__all__'


class RegistroEmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresas
        fields = '__all__'

    def validate(self, data):
        

        # Ya no necesita buscar la instancia por Id
        # si viene de PUT, self.instance ya existe (lo asignó la vista)
        # si viene de POST, self.instance es None

        nombre = data.get('NombreEmpresa')
        ruc= data.get('Ruc')
        if nombre:
            queryset = Empresas.objects.filter(
                NombreEmpresa=nombre,
                
            )
            if self.instance:
                queryset = queryset.exclude(Id=self.instance.Id)

            if queryset.exists():
                raise serializers.ValidationError(
                    {"NombreEmpresa": "Ya existe una empresa con este nombre."}
                )
        if ruc:
            queryset = Empresas.objects.filter(
                Ruc=ruc,
                
            )
            if self.instance:
                queryset = queryset.exclude(Id=self.instance.Id)

            if queryset.exists():
                raise serializers.ValidationError(
                    {"Ruc": "Ya existe una empresa con este ruc"}
                )

        return data
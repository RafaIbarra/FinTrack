from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from FinTrackApp.Modelos.CategoriasGastos import CategoriasGastos
from FinTrackApp.Modelos.Gastos import Gastos



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


class ConceptosGastosCategoriaSerializer(serializers.ModelSerializer):
    TotalConcepto = serializers.IntegerField ()
    CantidadRegistrosConcepto = serializers.IntegerField(read_only=True)
    PorcentajeConcepto = serializers.SerializerMethodField()

    class Meta:
        model = Gastos
        fields = ['Id', 'NombreGasto', 'TotalConcepto', 
                  'CantidadRegistrosConcepto', 'PorcentajeConcepto']

    def get_PorcentajeConcepto(self, obj):
        total_categoria = self.context.get('total_categoria') or 0
        if total_categoria and obj.TotalConcepto:
            return round((obj.TotalConcepto / total_categoria) * 100, 2)
        return 0
    

class InfoCategoriaGastoSerializer(serializers.ModelSerializer):
    FechaRegistro = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S")
    usuario_nombre = serializers.CharField(
        source='Usuario.NombreUsuario', read_only=True
    )
    TotalGastoCategoria = serializers.IntegerField ()
    CantidadGastosCategoria = serializers.IntegerField(read_only=True)
    CantidadConceptoGastos = serializers.IntegerField(read_only=True)
    DetalleGastos = serializers.SerializerMethodField()

    class Meta:
        model = CategoriasGastos
        fields = [
            'Id', 'NombreCategoria', 'Observacion', 'Usuario',
            'FechaRegistro', 'usuario_nombre',
            'TotalGastoCategoria', 'CantidadGastosCategoria',
            'CantidadConceptoGastos', 'DetalleGastos'
        ]

    def get_DetalleGastos(self, obj):
        # .all() usa los objetos precargados por Prefetch (sin N+1)
        gastos = obj.categoria_gasto_usuario.all()
        return ConceptosGastosCategoriaSerializer(
            gastos,
            many=True,
            context={'total_categoria': obj.TotalGastoCategoria}
        ).data




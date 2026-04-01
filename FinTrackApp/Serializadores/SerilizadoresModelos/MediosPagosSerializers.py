from rest_framework import serializers
from FinTrackApp.Modelos.MediosPagos import MediosPagos


class InfoMedioPagoSerializer(serializers.ModelSerializer):
    FechaRegistro= serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S")
    usuario_nombre = serializers.CharField(source='Usuario.NombreUsuario', read_only=True)

    class Meta:
        model = MediosPagos
        fields = ['Id','NombreMedioPago','Observacion','Usuario','FechaRegistro','usuario_nombre']


class RegistroMedioPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediosPagos
        fields = '__all__'

    def validate(self, data):
        usuario_id = self.initial_data.get('Usuario')

        # Ya no necesita buscar la instancia por Id
        # si viene de PUT, self.instance ya existe (lo asignó la vista)
        # si viene de POST, self.instance es None

        nombre = data.get('NombreMedioPago')
        if nombre:
            queryset = MediosPagos.objects.filter(
                NombreMedioPago=nombre,
                Usuario_id=usuario_id
            )
            if self.instance:
                queryset = queryset.exclude(Id=self.instance.Id)

            if queryset.exists():
                raise serializers.ValidationError(
                    {"NombreMedioPago": "Ya existe un medio de pago con este nombre para este usuario."}
                )

        return data
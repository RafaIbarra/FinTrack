from rest_framework import serializers

from FinTrackApp.Modelos.Usuarios import Usuarios

class RegistroUsuariosSerializer(serializers.ModelSerializer):
    class Meta:
        model=Usuarios
        fields= '__all__'
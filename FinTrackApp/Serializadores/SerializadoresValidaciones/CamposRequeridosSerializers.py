from rest_framework import serializers
class RegistroUsuarioInputSerializer(serializers.Serializer):
        nombre = serializers.CharField(max_length=100)
        apellido = serializers.CharField(max_length=100)
        user = serializers.CharField(max_length=50)
        correo = serializers.EmailField()
        def validate(self, data):
            # VERIFICA QUE LLEGUEN TODAS LAS KEY Y NO LLEGUEN DE MAS
            if len(self.initial_data) > len(self.fields):
                campos_recibidos = set(self.initial_data.keys())
                campos_permitidos = set(self.fields.keys())
                campos_extra = campos_recibidos - campos_permitidos
                
                if campos_extra:
                    raise serializers.ValidationError({
                        'campos_extra': f'Campos no permitidos: {", ".join(campos_extra)}'
                    })  
            return data
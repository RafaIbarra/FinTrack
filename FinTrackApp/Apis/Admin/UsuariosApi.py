from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import serializers 
from rest_framework.permissions import AllowAny
from FinTrackApp.Serializadores.SerializadoresValidaciones.CamposRequeridosSerializers import RegistroUsuarioInputSerializer
from FinTrackApp.Serializadores.SerilizadoresModelos.UsuariosSerializer import RegistroUsuariosSerializer
from FinTrackApp.Utils.funciones_seguridad import formato_user
class RegistroUsuario(APIView):
    """
    Operaciones:\n
    1) Registro inicial del usuario, se carga en la tabla Usuarios con estado=3 para posterior activacion
    2) Se crea una contraseña temporal que se enviara al correo
    

    Validaciones:\n
    1) El user name es unico
    2) El user name no puede existir en el sistema de Django

    Funciones Internas: \n
    1) formato_user(): Para unificar el estandar que debe tener el UserName
    2) generar_password_temp(): Generacion de clave aleatoria
    3) registrar_password_temp(): Registro de contraseña temporal
    """
    permission_classes = [AllowAny]

    
    
    
    def post(self, request, *args, **kwargs):
        try:
            # ✅ Esto ya valida: campos requeridos, tipos, max_length Y campos extra
            input_serializer =RegistroUsuarioInputSerializer(data=request.data)
            if not input_serializer.is_valid():
                return Response(
                    {'message': input_serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            validated_data = input_serializer.validated_data
            
            nombre = validated_data['nombre'].strip()
            apellido = validated_data['apellido'].strip()
            user_ing = validated_data['user'].strip()
            correo = validated_data['correo']
            
            user_reg = formato_user(user_ing)
            
            
            if User.objects.filter(username=user_reg).exists():
                return Response(
                    {'message': {'Username': f'Ya existe el usuario {user_reg}'}}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            
            
            with transaction.atomic():
                # Crear el usuario principal
                data_user = {
                    
                    'NombreUsuario': nombre,
                    'ApellidoUsuario': apellido,
                    'UserName': user_reg,
                    'Correo': correo,
                    'FechaRegistro': datetime.now(),
                    'LastLogin': datetime.now()
                }
                
                user_serializer = RegistroUsuariosSerializer(data=data_user)

                if not user_serializer.is_valid():
                    errors = {'usuario': {}} 
                    for campo, detalles in user_serializer.errors.items():
                        errors['usuario'][campo] = str(detalles[0])
                    raise serializers.ValidationError(errors)
                
                user_serializer.save()

                
            

            
            return Response({'message': 'Registro exitoso',}, status=status.HTTP_201_CREATED)
        
        except serializers.ValidationError as e:
            
            return Response(
                {'message': e.detail}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
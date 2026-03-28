
from django.contrib.auth.models import User
from django.db import transaction

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import serializers 
from rest_framework.permissions import AllowAny

from FinTrackApp.Serializadores.SerializadoresValidaciones.CamposRequeridosSerializers import RegistroUsuarioInputSerializer
from FinTrackApp.Serializadores.SerilizadoresModelos.UsuariosSerializer import RegistroUsuariosSerializer
from FinTrackApp.Modelos.Usuarios import Usuarios
from FinTrackApp.Utils.funciones_seguridad import formato_user,informacion_peticion,registrar_login


from datetime import datetime

class RegistroUsuario(APIView):
    """
  
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
            password = validated_data['password']
            user_reg = formato_user(user_ing)
            
            data_peticion=informacion_peticion(request)
            ip_peticion=data_peticion.get('Ip')
            dispositivo=data_peticion.get('Dispositivo')

            
            if User.objects.filter(username=user_reg).exists() or Usuarios.objects.filter(UserName=user_reg).exists():
                return Response(
                    {'message':  f'Ya existe el usuario {user_reg}'}, 
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
                User.objects.create_user(
                    username=user_reg, 
                    password=password,
                   
                )
            #UNA VEZ CREADO EL USUARIO INTENTA HACER EL LOGUEO 
            loguedo,data,mensaje=registrar_login(user_reg,password,ip_peticion,dispositivo)
            
            valores_logueo={
                'Registro':'Registro existoso usuario',
                'Logueado':loguedo,
                'token': data.get('token_jwt') if data else '',  # Puede ser None
                'refresh': data.get('refresh_jwt') if data else '',  # Puede ser None
                'sesion': data.get('token_clasico') if data else '',  # Puede ser None
                'user_name': user_reg.capitalize(),
                'message':mensaje
            }
        
            return Response(valores_logueo, status=status.HTTP_201_CREATED)
        
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
        




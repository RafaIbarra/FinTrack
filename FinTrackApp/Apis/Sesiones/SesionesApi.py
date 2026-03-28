from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.permissions import AllowAny
from FinTrackApp.Serializadores.SerializadoresValidaciones.CamposRequeridosSerializers import LoginUsuarioInputSerializers
from FinTrackApp.Utils.funciones_seguridad import informacion_peticion,registrar_login

class LoginUsuario(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        try:
            input_serializer =LoginUsuarioInputSerializers(data=request.data)
            if not input_serializer.is_valid():
                return Response(
                    {'message': input_serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            validated_data = input_serializer.validated_data
            user_name = validated_data['user'].strip()
            password = validated_data['password']
            data_peticion=informacion_peticion(request)
            ip_peticion=data_peticion.get('Ip')
            dispositivo=data_peticion.get('Dispositivo')
            loguedo,data,mensaje=registrar_login(user_name,password,ip_peticion,dispositivo)
           
            if loguedo:
                valores_logueo={
                    'Logueado':loguedo,
                    'token': data.get('token_jwt') if data else '',  # Puede ser None
                    'refresh': data.get('refresh_jwt') if data else '',  # Puede ser None
                    'sesion': data.get('token_clasico') if data else '',  # Puede ser None
                    'user_name': user_name.capitalize(),
                    'message':mensaje
                }
            
                return Response(valores_logueo, status=status.HTTP_200_OK)
            else:
                return Response({'message':mensaje}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

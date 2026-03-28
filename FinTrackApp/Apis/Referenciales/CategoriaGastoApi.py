from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db import transaction
from datetime import datetime
from FinTrackApp.Decoradores.DecoradoresSeguridad import AutenticacionToken
from FinTrackApp.Modelos.CategoriasGastos import CategoriasGastos
from FinTrackApp.Serializadores.SerilizadoresModelos.CategoriaGastoSerializers import RegistroCategoriaGastoSerializer,InfoCategoriaGastoSerializer
class RegistroCategoria(APIView):
    @AutenticacionToken
    
    def post(self, request, *args, **kwargs):
        try:
            
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')


            id = int(request.data.get('id', 0))
            nombre=request.data.get('nombre').strip()
            descripcion = request.data.get('descripcion', 'sin').strip()
            
            data_registrar={
              'Id':id,
              'NombreCategoria':nombre,
              'Observacion':descripcion,
              'Usuario':id_usuario,
              'FechaRegistro':datetime.now(),
              
            }
            serializer = RegistroCategoriaGastoSerializer(data=data_registrar)
            if not serializer.is_valid():
                # Obtener todos los mensajes de error
                errores = serializer.errors
                
                # Concatenar todos los mensajes en un solo string
                mensajes_error = []
                
                for campo, mensajes in errores.items():
                    # Cada campo puede tener una lista de mensajes
                    for mensaje in mensajes:
                        # Agregar el campo al mensaje
                        mensajes_error.append(f"{campo}: {mensaje}")
                
                # Unir todos los mensajes con punto y coma
                error_concatenado = "; ".join(mensajes_error)
                
                return Response({
                    'message': error_concatenado,
                    'detalles': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            categoria = serializer.save()
            detail_serializer = InfoCategoriaGastoSerializer(categoria)
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )